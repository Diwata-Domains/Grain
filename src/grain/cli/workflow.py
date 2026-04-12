import dataclasses
import json

import click

from grain.adapters.filesystem import resolve_repo_root
from grain.domain.errors import UsageError
from grain.services.workflow_loop_service import run_workflow_loop
from grain.services.workflow_service import evaluate_workflow_state, evaluation_to_dict
from grain.services.workflow_run_service import run_workflow_step


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

    if fmt == "json":
        data = dataclasses.asdict(result)
        data["evaluation"] = evaluation_to_dict(evaluation)
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


@workflow_group.command("run")
@click.pass_context
def workflow_run(ctx):
    """Execute one legal workflow step or stop at an explicit gate."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, payload = run_workflow_step(root)

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
