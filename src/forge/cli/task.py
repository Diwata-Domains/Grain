import dataclasses
import json

import click

from forge.adapters.filesystem import resolve_repo_root
from forge.cli.output import print_result
from forge.domain.errors import GeneralError, InvalidTransitionError, ValidationError
from forge.services import task_service


@click.group("task")
def task_group():
    """Create and manage task packets."""


@task_group.command("create")
@click.option("--phase", type=int, required=True, help="Phase number (e.g. 3).")
@click.option("--task-num", type=int, required=True, help="Task number within phase (e.g. 4).")
@click.option("--title", default="", help="Task title (replaces [Title] placeholder in task.md).")
@click.pass_context
def task_create(ctx, phase, task_num, title):
    """Create a new task packet."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result = task_service.create_packet_directory(root, phase, task_num, title=title)
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

    click.echo(f"task show: ok")
    click.echo(f"  id      {record.id}")
    click.echo(f"  status  {record.status}")
    click.echo(f"  phase   {record.phase}")
    click.echo(f"  path    {record.path.name}")
    click.echo(f"  files")
    for name, present in inventory.items():
        state = "present" if present else "absent"
        click.echo(f"    {name:<24}  {state}")


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
        click.echo(f"task status: ok")
        click.echo(f"  {task_id}  ->  {new_status}")
        for path in result.files_updated:
            click.echo(f"  updated   {path}")


@task_group.command("validate")
@click.option("--id", "task_id", default=None, metavar="TASK-####", help="Validate one packet.")
@click.option("--all", "validate_all", is_flag=True, default=False, help="Validate all packets.")
@click.pass_context
def task_validate(ctx, task_id, validate_all):
    """Validate one packet or all packets."""
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
@click.pass_context
def task_close(ctx, task_id):
    """Attempt closure validation for a packet."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result = task_service.close_packet(root, task_id)

    if not result.ok:
        if any("not found" in e for e in result.errors):
            for err in result.errors:
                click.echo(f"  error     {err}", err=True)
            raise click.UsageError(f"packet '{task_id}' not found")
        raise ValidationError(
            "closure validation failed",
            detail=f"{len(result.errors)} error(s)",
        )

    if fmt == "json":
        print_result(result, fmt=fmt)
    else:
        click.echo(f"task close: ok")
        click.echo(f"  {task_id}  ->  done")
        for path in result.files_updated:
            click.echo(f"  updated   {path}")
