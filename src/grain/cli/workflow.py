# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

import dataclasses
import json

import click

from grain.adapters.filesystem import resolve_repo_root
from grain.domain.errors import UsageError
from grain.services.guard_service import run_guard
from grain.services.reconcile_service import reconcile
from grain.services.task_observability_service import read_task_observability
from grain.services.workflow_diagnostics_service import (
    diagnostic_to_dict,
    explain_workflow_state,
)
from grain.services.workflow_loop_service import run_workflow_loop
from grain.services.workflow_service import evaluate_workflow_state, evaluation_to_dict
from grain.services.workflow_run_service import run_workflow_step

# Stop reasons that mean "no obvious next task" — surface a suggestion (P32-T05).
_NO_NEXT_TASK_STOP_REASONS = frozenset(
    {"task_planning_required", "phase_has_no_tasks", "phase_boundary_review_close_required"}
)


@click.group("workflow")
def workflow_group():
    """State-driven workflow commands."""


@workflow_group.command("next")
@click.pass_context
def workflow_next(ctx):
    """Report the next legal workflow action or explicit stop reason."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, evaluation = evaluate_workflow_state(root)

    # The command should always return structured state output when evaluation
    # can run, even when the state is stopped/blocked.
    if evaluation is None:
        if fmt == "json":
            click.echo(json.dumps(dataclasses.asdict(result), indent=2))
        else:
            click.echo("workflow next: failed")
            for err in result.errors:
                click.echo(f"  error     {err}", err=True)
        raise click.ClickException("workflow evaluation failed")

    suggestion = _surface_top_suggestion(root, evaluation)
    _emit_stop_reason_telemetry(root, evaluation)

    if fmt == "json":
        data = dataclasses.asdict(result)
        data["evaluation"] = evaluation_to_dict(evaluation)
        data["observability"] = _workflow_observability_payload(root, evaluation.active_task_id)
        data["suggestion"] = suggestion
        click.echo(json.dumps(data, indent=2))
        return

    label = "ok" if evaluation.ok else "stopped"
    click.echo(f"workflow next: {label}")
    click.echo(f"  phase             {evaluation.active_phase or '(unknown)'}")
    click.echo(f"  active_task_id    {evaluation.active_task_id or 'none'}")
    if evaluation.next_action:
        click.echo(f"  next_action       {evaluation.next_action}")
    if evaluation.stop_reason:
        click.echo(f"  stop_reason       {evaluation.stop_reason}")
    if evaluation.recommended_prompt:
        click.echo(f"  recommended_prompt  {evaluation.recommended_prompt}")
    click.echo(f"  blocking_reasons  {len(evaluation.blocking_reasons)}")
    for reason in evaluation.blocking_reasons:
        click.echo(f"    - {reason}")
    click.echo(f"  affected_artifacts  {len(evaluation.affected_artifacts)}")
    for artifact in evaluation.affected_artifacts:
        click.echo(f"    - {artifact}")
    if evaluation.candidate_tasks:
        click.echo("  candidate_tasks")
        for task in evaluation.candidate_tasks:
            click.echo(f"    - {task.task_ref} ({task.status})")
    observability = _workflow_observability_payload(root, evaluation.active_task_id)
    if observability:
        click.echo("  observability")
        click.echo(f"    executor_identity  {observability['executor_identity'] or 'unset'}")
        click.echo(f"    model_class        {observability['model_class'] or 'unset'}")
        click.echo(f"    last_stage         {observability['last_stage'] or 'unset'}")
        click.echo(f"    last_action        {observability['last_workflow_action'] or 'unset'}")

    if evaluation.warnings:
        for w in evaluation.warnings:
            click.echo(f"  warning           {w}", err=True)

    no_active_task = not evaluation.active_task_id
    if no_active_task and evaluation.next_action == "task_execute" and evaluation.candidate_tasks:
        click.echo(
            f"  tip               if no packet exists for {evaluation.candidate_tasks[0].task_ref}, "
            "run `grain task create` first to create one before executing"
        )
    elif no_active_task and evaluation.stop_reason in {"task_planning_required", "task_planning", None}:
        click.echo(
            "  tip               completed ad-hoc work outside the workflow? "
            "`grain task create --simple` creates a lightweight audit record — say no to skip"
        )

    if suggestion:
        click.echo("  suggestion")
        click.echo(f"    kind            {suggestion['kind']}")
        if suggestion["kind"] == "pick-up":
            click.echo(
                f"    task            {suggestion['task_ref']}"
                + (f" ({suggestion['task_id']})" if suggestion.get("task_id") else "")
            )
        else:
            click.echo(f"    objective       {suggestion.get('objective') or suggestion['title']}")
        click.echo(f"    signal          {suggestion['signal']}")
        click.echo("    → run           grain suggest  (then `grain suggest accept ...`)")


@workflow_group.command("guard")
@click.option("--strict", is_flag=True, default=False, help="Treat warnings as violations.")
@click.option("--check-docs", is_flag=True, default=False, help="Include docs audit findings.")
@click.option("--check-dev-alignment", is_flag=True, default=False, help="Check dev/install alignment.")
@click.pass_context
def workflow_guard(ctx, strict, check_docs, check_dev_alignment):
    """Run enforcement checks against the current workspace state.

    Checks: packet_open, results_not_stub, phase_alignment,
    implementation_ahead_of_packet. Returns exit code 1 on violation.
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    guard = run_guard(root, strict=strict, check_docs=check_docs, check_dev_alignment=check_dev_alignment)

    if fmt == "json":
        click.echo(json.dumps({
            "status": guard.status,
            "ok": guard.ok,
            "checks": [
                {
                    "id": f.id,
                    "result": f.result,
                    "severity": f.severity,
                    "message": f.message,
                    "remediation": f.remediation,
                }
                for f in guard.checks
            ],
            "errors": guard.errors,
        }, indent=2))
        if not guard.ok:
            raise SystemExit(1)
        return

    if guard.errors:
        for err in guard.errors:
            click.echo(f"  error  {err}", err=True)
        raise SystemExit(1)

    _RESULT_SYMBOL = {"pass": "✓", "warn": "⚠", "fail": "✗"}
    for finding in guard.checks:
        sym = _RESULT_SYMBOL.get(finding.result, "?")
        click.echo(f"  {sym} {finding.id:<38} {finding.message}")
        if finding.remediation and finding.result != "pass":
            click.echo(f"    → {finding.remediation}")

    violations = sum(1 for f in guard.checks if f.result == "fail")
    warnings = sum(1 for f in guard.checks if f.result == "warn")

    click.echo("")
    if violations:
        click.echo(f"Guard: {violations} violation{'s' if violations != 1 else ''}" +
                   (f", {warnings} warning{'s' if warnings != 1 else ''}" if warnings else ""))
        raise SystemExit(1)
    elif warnings:
        click.echo(f"Guard: {warnings} warning{'s' if warnings != 1 else ''}")
    else:
        click.echo("Guard: OK")


@workflow_group.command("run")
@click.option(
    "--simple",
    is_flag=True,
    default=False,
    help="When auto-creating a missing packet, use simple mode (task.md + results.md only).",
)
@click.pass_context
def workflow_run(ctx, simple):
    """Execute one legal workflow step or stop at an explicit gate."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, payload = run_workflow_step(root, simple=simple)

    if payload is None:
        if fmt == "json":
            click.echo(json.dumps(dataclasses.asdict(result), indent=2))
        else:
            click.echo("workflow run: failed")
            for err in result.errors:
                click.echo(f"  error     {err}", err=True)
        raise click.ClickException("workflow runner evaluation failed")

    if fmt == "json":
        data = dataclasses.asdict(result)
        data["workflow_run"] = payload
        click.echo(json.dumps(data, indent=2))
        return

    action_taken = payload.get("action_taken", "none")
    gate_reason = payload.get("gate_reason", "")

    if action_taken != "none":
        click.echo("workflow run: ok")
        click.echo(f"  action_taken      {action_taken}")
        click.echo(f"  task_activated    {payload.get('task_activated', '')}")
        if payload.get("packet_created"):
            click.echo("  packet_created    true")
        click.echo(f"  active_phase      {payload.get('active_phase', '')}")
        click.echo(f"  recommended_prompt  {payload.get('recommended_prompt', '')}")
        for path in result.files_updated:
            click.echo(f"  updated           {path}")
    else:
        click.echo("workflow run: gated")
        click.echo(f"  gate_reason       {gate_reason}")
        click.echo(f"  gate_condition    {payload.get('gate_condition', '')}")
        click.echo(f"  active_phase      {payload.get('active_phase', '')}")
        if payload.get("active_task_id"):
            click.echo(f"  active_task_id    {payload['active_task_id']}")
        if payload.get("recommended_prompt"):
            click.echo(f"  recommended_prompt  {payload['recommended_prompt']}")
        click.echo(f"  blocking_reasons  {len(payload.get('blocking_reasons', []))}")
        for reason in payload.get("blocking_reasons", []):
            click.echo(f"    - {reason}")


@workflow_group.command("explain")
@click.pass_context
def workflow_explain(ctx):
    """Explain why the workflow is blocked or what the next operator move should be."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, evaluation, diagnostic = explain_workflow_state(root)

    if evaluation is None or diagnostic is None:
        if fmt == "json":
            click.echo(json.dumps(dataclasses.asdict(result), indent=2))
        else:
            click.echo("workflow explain: failed")
            for err in result.errors:
                click.echo(f"  error     {err}", err=True)
        raise click.ClickException("workflow explanation failed")

    if fmt == "json":
        data = dataclasses.asdict(result)
        data["evaluation"] = evaluation_to_dict(evaluation)
        data["diagnostic"] = diagnostic_to_dict(diagnostic)
        click.echo(json.dumps(data, indent=2))
        return

    click.echo(f"workflow explain: {diagnostic.status}")
    click.echo(f"  summary           {diagnostic.summary}")
    click.echo(f"  likely_cause      {diagnostic.likely_cause}")
    click.echo(f"  active_phase      {diagnostic.active_phase or '(unknown)'}")
    click.echo(f"  active_task_id    {diagnostic.active_task_id or 'none'}")
    if diagnostic.stop_reason:
        click.echo(f"  stop_reason       {diagnostic.stop_reason}")
    if diagnostic.next_action:
        click.echo(f"  next_action       {diagnostic.next_action}")
    if diagnostic.recommended_prompt:
        click.echo(f"  recommended_prompt  {diagnostic.recommended_prompt}")
    click.echo(f"  affected_artifacts  {len(diagnostic.affected_artifacts)}")
    for artifact in diagnostic.affected_artifacts:
        click.echo(f"    - {artifact}")
    click.echo(f"  recommended_actions  {len(diagnostic.recommended_actions)}")
    for action in diagnostic.recommended_actions:
        click.echo(f"    - {action}")
    click.echo(f"  suggested_commands  {len(diagnostic.suggested_commands)}")
    for command in diagnostic.suggested_commands:
        click.echo(f"    - {command}")


@workflow_group.command("reconcile")
@click.option(
    "--fix",
    is_flag=True,
    default=False,
    help="Auto-repair safe drift (backlog status sync, current_task.md stale pointer).",
)
@click.option(
    "--dry-run",
    "dry_run",
    is_flag=True,
    default=False,
    help="Show what --fix would do without writing changes.",
)
@click.pass_context
def workflow_reconcile(ctx, fix, dry_run):
    """Detect drift across working docs and optionally repair it.

    Checks:
    - Backlog task statuses vs existing packet task.md Status fields.
    - current_task.md pointer vs active packet status.
    - Packets with Status: needs_fix not visible in current_task.md.

    Use --fix to auto-repair safe drift. Use --dry-run to preview repairs.
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result = reconcile(root, fix=fix, dry_run=dry_run)

    if fmt == "json":
        data = {
            "ok": result.ok,
            "dry_run": result.dry_run,
            "issue_count": len(result.issues),
            "issues": [
                {
                    "severity": i.severity,
                    "check": i.check,
                    "description": i.description,
                    "fix_available": i.fix_available,
                    "fix_description": i.fix_description,
                }
                for i in result.issues
            ],
            "fixed": result.fixed,
        }
        click.echo(json.dumps(data, indent=2))
        if not result.ok:
            raise SystemExit(1)
        return

    label = "ok" if result.ok else "issues found"
    if result.dry_run:
        label += " (dry-run)"
    click.echo(f"workflow reconcile: {label}")
    click.echo(f"  issues            {len(result.issues)}")
    for issue in result.issues:
        marker = "[error]" if issue.severity == "error" else "[warn] "
        click.echo(f"    {marker}  {issue.check}: {issue.description}")
        if issue.fix_available and not fix and not dry_run:
            click.echo(f"             fix: {issue.fix_description}")
    if result.fixed:
        click.echo(f"  fixed             {len(result.fixed)}")
        for fix_desc in result.fixed:
            click.echo(f"    - {fix_desc}")
    elif fix and not result.issues:
        click.echo("  nothing to fix")
    if not result.ok:
        raise SystemExit(1)


def _surface_top_suggestion(root, evaluation):
    """Read-only top suggestion for no-next-task states. Writes nothing (P32-T05).

    Surface-only: degrades to None on any error so it never breaks `workflow next`.
    """
    if evaluation is None or evaluation.stop_reason not in _NO_NEXT_TASK_STOP_REASONS:
        return None
    try:
        from grain.services.suggest_service import top_suggestion
        proposal = top_suggestion(root)
    except Exception:
        return None
    if proposal is None:
        return None
    return {
        "kind": proposal.kind,
        "title": proposal.title,
        "signal": proposal.signal,
        "signal_ref": proposal.signal_ref,
        "task_ref": proposal.task_ref,
        "task_id": proposal.task_id,
        "objective": proposal.objective,
        "rationale": proposal.rationale,
    }


def _emit_stop_reason_telemetry(root, evaluation):
    """Side-band: emit the workflow-next stop reason when telemetry is enabled.

    Opt-in and fire-and-forget — never raises, never alters `workflow next`
    control flow. No-op when the evaluation produced no stop reason.
    """
    if evaluation is None or not evaluation.stop_reason:
        return
    try:
        from grain.services.telemetry_service import (
            emit_built,
            make_workflow_next_stop_event,
        )
        emit_built(
            root,
            make_workflow_next_stop_event,
            evaluation.stop_reason,
            evaluation.active_phase or "",
        )
    except Exception:
        return


def _workflow_observability_payload(root, task_id: str):
    if not task_id:
        return None
    record, _ = read_task_observability(root, task_id)
    if record is None:
        return None
    payload = dataclasses.asdict(record)
    if not any(
        payload.get(key)
        for key in (
            "executor_identity",
            "model_class",
            "last_stage",
            "last_workflow_action",
            "started_at",
            "updated_at",
        )
    ):
        return None
    return payload


@workflow_group.command("loop")
@click.option(
    "--steps",
    type=click.IntRange(min=1),
    default=None,
    help="Maximum number of loop steps to execute before stopping.",
)
@click.option(
    "--supervision-level",
    "supervision_level",
    type=click.Choice(["supervised", "gated", "autonomous"]),
    default=None,
    help="Override supervision level from docs/runtime/workflow_loop.yaml.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    show_default=True,
    help="Print planned loop action(s) without invoking stage commands or mutating state.",
)
@click.pass_context
def workflow_loop(ctx, steps, supervision_level, dry_run):
    """Run repeated workflow steps until a stop condition is reached."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, payload = run_workflow_loop(
        root,
        steps=steps,
        supervision_level_override=supervision_level,
        dry_run=dry_run,
    )

    if payload is None:
        if fmt == "json":
            click.echo(json.dumps(dataclasses.asdict(result), indent=2))
        else:
            click.echo("workflow loop: failed")
            for err in result.errors:
                click.echo(f"  error     {err}", err=True)
        raise UsageError("workflow loop execution failed")

    if fmt == "json":
        data = dataclasses.asdict(result)
        data["workflow_loop"] = payload
        click.echo(json.dumps(data, indent=2))
        return

    click.echo("workflow loop: ok")
    click.echo(f"  supervision_level  {payload.get('supervision_level', '')}")
    click.echo(f"  steps_requested    {payload.get('steps_requested', 0)}")
    click.echo(f"  steps_completed    {payload.get('steps_completed', 0)}")
    click.echo(f"  stop_reason        {payload.get('stop_reason', '')}")
    click.echo(f"  active_phase       {payload.get('active_phase', '')}")
    click.echo(f"  active_task_id     {payload.get('active_task_id') or 'none'}")
    if payload.get("recommended_prompt"):
        click.echo(f"  recommended_prompt  {payload['recommended_prompt']}")
    click.echo(f"  blocking_reasons   {len(payload.get('blocking_reasons', []))}")
    for reason in payload.get("blocking_reasons", []):
        click.echo(f"    - {reason}")

    for step in payload.get("steps", []):
        click.echo(
            (
                "  step[{index}] action={action} stage={stage} exit={exit_code} "
                "changed={changed_state} dry_run={dry_run} duration_ms={duration_ms}"
            ).format(
                **step
            )
        )
