import dataclasses
import json
from pathlib import Path

import click

from grain.adapters.filesystem import resolve_repo_root
from grain.cli.output import print_result
from grain.domain.errors import GeneralError, InvalidTransitionError, ValidationError
from grain.services import task_service
from grain.services.task_observability_service import (
    read_task_observability,
    update_task_observability,
)


@click.group("task")
def task_group():
    """Create and manage task packets."""


@task_group.command("create")
@click.option("--phase", type=int, required=True, help="Phase number (e.g. 3).")
@click.option("--task-num", type=int, required=True, help="Task number within phase (e.g. 4).")
@click.option("--title", default="", help="Task title (replaces [Title] placeholder in task.md).")
@click.option(
    "--simple",
    is_flag=True,
    default=False,
    help="Minimal packet: task.md + results.md only. For small mechanical tasks where planning files add no value.",
)
@click.pass_context
def task_create(ctx, phase, task_num, title, simple):
    """Create a new task packet."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result = task_service.create_packet_directory(root, phase, task_num, title=title, simple=simple)
    print_result(result, fmt=fmt)

    if not result.ok:
        raise GeneralError("task create failed", detail="; ".join(result.errors))


@task_group.command("list")
@click.pass_context
def task_list(ctx):
    """List task packets."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, records = task_service.list_packets(root)

    if fmt == "json":
        data = dataclasses.asdict(result)
        data["packets"] = [
            {"id": r.id, "status": r.status, "phase": r.phase, "path": str(r.path)}
            for r in records
        ]
        click.echo(json.dumps(data, indent=2))
        return

    click.echo(f"task list: ok  ({len(records)} packet{'s' if len(records) != 1 else ''})")
    for warn in result.warnings:
        click.echo(f"  warning   {warn}")
    if not records:
        click.echo("  (no packets found)")
        return
    for r in records:
        click.echo(f"  {r.id:<12}  {r.status:<12}  {r.path.name}")


@task_group.command("next")
@click.pass_context
def task_next(ctx):
    """Report the next actionable backlog task or planning requirement."""
    from grain.services.workflow_service import evaluate_workflow_state

    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, evaluation = evaluate_workflow_state(root)

    if evaluation is None:
        if fmt == "json":
            click.echo(json.dumps(dataclasses.asdict(result), indent=2))
        else:
            print_result(result, fmt)
        raise click.ClickException("task selection failed")

    next_task = ""
    if (
        evaluation.next_action == "task_execute"
        or evaluation.stop_reason == "packet_required"
    ) and evaluation.candidate_tasks:
        next_task = evaluation.candidate_tasks[0].task_ref

    planning_required = (
        evaluation.next_action == "task_planning"
        or evaluation.stop_reason == "task_planning_required"
    )

    if fmt == "json":
        data = dataclasses.asdict(result)
        data["task_next"] = {
            "next_task": next_task,
            "next_action": evaluation.next_action,
            "planning_required": planning_required,
            "stop_reason": evaluation.stop_reason,
            "blocking_reasons": evaluation.blocking_reasons,
            "recommended_prompt": evaluation.recommended_prompt,
            "affected_artifacts": evaluation.affected_artifacts,
        }
        click.echo(json.dumps(data, indent=2))
        return

    if next_task:
        click.echo("task next: ok")
        click.echo(f"  next_task         {next_task}")
        if evaluation.next_action:
            click.echo(f"  next_action       {evaluation.next_action}")
        if evaluation.stop_reason:
            click.echo(f"  stop_reason       {evaluation.stop_reason}")
    elif planning_required:
        click.echo("task next: planning_required")
        click.echo("  reason            no ready task candidate; planning required first")
        click.echo(f"  recommended_prompt  {evaluation.recommended_prompt}")
    else:
        click.echo("task next: stopped")
        if evaluation.stop_reason:
            click.echo(f"  stop_reason       {evaluation.stop_reason}")
    click.echo(f"  blocking_reasons  {len(evaluation.blocking_reasons)}")
    for reason in evaluation.blocking_reasons:
        click.echo(f"    - {reason}")


@task_group.command("show")
@click.option("--id", "task_id", required=True, metavar="TASK-####", help="Packet ID to show.")
@click.pass_context
def task_show(ctx, task_id):
    """Show packet metadata and status."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, record, inventory = task_service.show_packet(root, task_id)

    if not result.ok:
        for err in result.errors:
            click.echo(f"  error     {err}", err=True)
        raise click.UsageError(f"packet '{task_id}' not found")

    if fmt == "json":
        data = dataclasses.asdict(result)
        data["packet"] = {
            "id": record.id,
            "status": record.status,
            "phase": record.phase,
            "path": str(record.path),
            "files": inventory,
        }
        click.echo(json.dumps(data, indent=2))
        return

    click.echo("task show: ok")
    click.echo(f"  id      {record.id}")
    click.echo(f"  status  {record.status}")
    click.echo(f"  phase   {record.phase}")
    click.echo(f"  path    {record.path.name}")
    click.echo("  files")
    for name, present in inventory.items():
        state = "present" if present else "absent"
        click.echo(f"    {name:<24}  {state}")


@task_group.command("observe")
@click.option("--id", "task_id", default=None, metavar="TASK-####", help="Packet ID (defaults to current_task.md).")
@click.option("--executor", "executor_identity", default=None, help="Executor identity to record, e.g. codex or claude.")
@click.option("--model-class", "model_class", default=None, help="Model class used for the task, e.g. frontier_model.")
@click.option(
    "--stage",
    type=click.Choice(["execute", "review", "close"]),
    default=None,
    help="Task stage to record.",
)
@click.option("--action", "workflow_action", default=None, help="Last workflow action to record.")
@click.pass_context
def task_observe(ctx, task_id, executor_identity, model_class, stage, workflow_action):
    """Inspect or update packet-local task observability metadata."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    resolved_task_id = task_id or _read_active_task_id(root)
    if not resolved_task_id or resolved_task_id == "none":
        raise click.UsageError("no active task; pass --id TASK-#### or set docs/working/current_task.md")

    wants_update = any(
        value is not None
        for value in (executor_identity, model_class, stage, workflow_action)
    )

    if wants_update:
        try:
            record, observability_path = update_task_observability(
                root,
                resolved_task_id,
                executor_identity=executor_identity,
                model_class=model_class,
                stage=stage,
                workflow_action=workflow_action,
            )
        except FileNotFoundError:
            raise click.UsageError(f"packet '{resolved_task_id}' not found")
        result = {
            "task_id": resolved_task_id,
            "observability_path": str(observability_path.relative_to(root)),
            "observability": dataclasses.asdict(record),
        }
    else:
        record, observability_path = read_task_observability(root, resolved_task_id)
        if record is None or observability_path is None:
            raise click.UsageError(f"packet '{resolved_task_id}' not found")
        result = {
            "task_id": resolved_task_id,
            "observability_path": str(observability_path.relative_to(root)),
            "observability": dataclasses.asdict(record),
        }

    if fmt == "json":
        click.echo(json.dumps(result, indent=2))
        return

    click.echo("task observe: ok")
    click.echo(f"  task_id           {resolved_task_id}")
    click.echo(f"  observability     {result['observability_path']}")
    payload = result["observability"]
    click.echo(f"  executor_identity {payload['executor_identity'] or 'unset'}")
    click.echo(f"  model_class       {payload['model_class'] or 'unset'}")
    click.echo(f"  last_stage        {payload['last_stage'] or 'unset'}")
    click.echo(f"  last_workflow_action  {payload['last_workflow_action'] or 'unset'}")
    click.echo(f"  started_at        {payload['started_at'] or 'unset'}")
    click.echo(f"  updated_at        {payload['updated_at'] or 'unset'}")


@task_group.command("prepare")
@click.option("--id", "task_id", required=True, metavar="TASK-####", help="Packet ID to prepare.")
@click.pass_context
def task_prepare(ctx, task_id):
    """Check packet/context/prompt prerequisites for one task."""
    from grain.services.task_prepare_service import prepare_task_packet

    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, payload = prepare_task_packet(root, task_id)

    if payload is None:
        if any("not found" in e for e in result.errors):
            for err in result.errors:
                click.echo(f"  error     {err}", err=True)
            raise click.UsageError(f"packet '{task_id}' not found")
        raise GeneralError("task prepare failed", detail="; ".join(result.errors))

    if fmt == "json":
        data = dataclasses.asdict(result)
        data["prepare"] = payload
        click.echo(json.dumps(data, indent=2))
        return

    label = "ok" if payload["ready"] else "missing_inputs"
    click.echo(f"task prepare: {label}")
    click.echo(f"  task_id           {payload['task_id']}")
    click.echo(f"  packet_dir        {Path(payload['packet_dir']).name}")
    click.echo(f"  task_status       {payload['task_status'] or '(missing)'}")
    click.echo(f"  recommended_prompt  {payload['recommended_prompt']}")
    click.echo(f"  missing_inputs    {len(payload['missing_inputs'])}")
    for item in payload["missing_inputs"]:
        click.echo(f"    - {item}")

    has_stubs = any("stub packet file" in item for item in payload["missing_inputs"])
    if has_stubs:
        click.echo(
            f"  tip               planning files have unresolved placeholders — "
            f"consider using {payload['recommended_prompt']} in a fresh conversation for best results"
        )


@task_group.command("status")
@click.option("--id", "task_id", required=True, metavar="TASK-####", help="Packet ID.")
@click.option("--status", "new_status", required=True, help="New status value.")
@click.pass_context
def task_status(ctx, task_id, new_status):
    """Update packet status."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result = task_service.update_packet_status(root, task_id, new_status)

    if not result.ok:
        # Distinguish not-found (exit 2) from invalid transition (exit 5)
        if any("not found" in e for e in result.errors):
            for err in result.errors:
                click.echo(f"  error     {err}", err=True)
            raise click.UsageError(f"packet '{task_id}' not found")
        raise InvalidTransitionError(
            "status transition not allowed",
            detail="; ".join(result.errors),
        )

    if fmt == "json":
        print_result(result, fmt=fmt)
    else:
        click.echo("task status: ok")
        click.echo(f"  {task_id}  ->  {new_status}")
        for path in result.files_updated:
            click.echo(f"  updated   {path}")


@task_group.command("validate")
@click.option("--id", "task_id", default=None, metavar="TASK-####", help="Validate one packet by task ID.")
@click.option(
    "--all",
    "validate_all",
    is_flag=True,
    default=False,
    show_default=True,
    help="Validate all packets (default behavior when no selector is provided).",
)
@click.pass_context
def task_validate(ctx, task_id, validate_all):
    """Validate one packet or all packets.

    When neither --id nor --all is provided, defaults to validating all packets.
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    if task_id and validate_all:
        raise click.UsageError("specify --id or --all, not both")
    if not task_id and not validate_all:
        # default: validate all
        validate_all = True

    if task_id:
        result = task_service.validate_one_packet(root, task_id)
        if not result.ok and any("not found" in e for e in result.errors):
            for err in result.errors:
                click.echo(f"  error     {err}", err=True)
            raise click.UsageError(f"packet '{task_id}' not found")
    else:
        result = task_service.validate_all_packets(root)

    print_result(result, fmt=fmt)

    if not result.ok:
        raise ValidationError(
            "task validation failed",
            detail=f"{len(result.errors)} error(s)",
        )


@task_group.command("close")
@click.option("--id", "task_id", required=True, metavar="TASK-####", help="Packet ID to close.")
@click.option(
    "--quick",
    is_flag=True,
    default=False,
    help="Minimal closure: writes results.md from --summary and marks done without full validation.",
)
@click.option(
    "--summary",
    default="",
    metavar="TEXT",
    help="One-line summary for quick closure (required with --quick).",
)
@click.option(
    "--files",
    "files_list",
    multiple=True,
    metavar="PATH",
    help="Files changed (repeatable). Used with --quick to populate results.md.",
)
@click.pass_context
def task_close(ctx, task_id, quick, summary, files_list):
    """Attempt closure validation for a packet.

    Use --quick for conversational or voice workflows: writes a minimal results.md
    from --summary (and optional --files) and marks the packet done without
    requiring handoff.md or efficiency metrics.
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    if quick:
        if not summary:
            raise click.UsageError("--quick requires --summary TEXT")
        result = task_service.quick_close_packet(root, task_id, summary, list(files_list) or None)
    else:
        result = task_service.close_packet(root, task_id)

    if result.ok:
        try:
            _, observability_path = update_task_observability(
                root,
                task_id,
                stage="close",
                workflow_action="task_close",
            )
            result.files_updated.append(str(observability_path.relative_to(root)))
        except FileNotFoundError:
            pass

    if not result.ok:
        if any("not found" in e for e in result.errors):
            for err in result.errors:
                click.echo(f"  error     {err}", err=True)
            raise click.UsageError(f"packet '{task_id}' not found")
        print_result(result, fmt=fmt)
        raise ValidationError(
            "closure validation failed",
            detail=f"{len(result.errors)} error(s)",
        )

    if fmt == "json":
        print_result(result, fmt=fmt)
    else:
        click.echo("task close: ok")
        click.echo(f"  {task_id}  ->  done")
        for path in result.files_created or []:
            click.echo(f"  created   {path}")
        for path in result.files_updated or []:
            click.echo(f"  updated   {path}")


def _read_active_task_id(root: Path) -> str:
    current_task_path = root / "docs" / "working" / "current_task.md"
    if not current_task_path.exists():
        return ""
    for line in current_task_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Task ID:"):
            return line.split(":", 1)[1].strip()
    return ""
