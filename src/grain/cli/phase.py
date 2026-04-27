import dataclasses
import json

import click

from grain.adapters.filesystem import resolve_repo_root
from grain.services.phase_archive_service import archive_phase
from grain.services.phase_close_service import close_phase
from grain.services.workflow_service import evaluate_workflow_state


@click.group("phase")
def phase_group():
    """Phase-level workflow commands."""


@phase_group.command("next")
@click.pass_context
def phase_next(ctx):
    """Report whether phase planning/review-close/no-phase-action is next."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, evaluation = evaluate_workflow_state(root)
    if evaluation is None:
        if fmt == "json":
            click.echo(json.dumps(dataclasses.asdict(result), indent=2))
        else:
            click.echo("phase next: failed")
            for err in result.errors:
                click.echo(f"  error     {err}", err=True)
        raise click.ClickException("phase selection failed")

    phase_action = "no_phase_action"
    reason = "task-level action remains available"
    if evaluation.stop_reason == "phase_boundary_review_close_required":
        phase_action = "phase_review_close"
        reason = "no executable tasks remain in active phase"
    elif evaluation.stop_reason == "project_complete":
        phase_action = "no_phase_action"
        reason = "project is marked complete"
    elif evaluation.next_action == "task_planning" or evaluation.stop_reason == "task_planning_required":
        phase_action = "phase_planning"
        reason = "task planning is required before execution can continue"

    if fmt == "json":
        data = dataclasses.asdict(result)
        data["phase_next"] = {
            "active_phase": evaluation.active_phase,
            "phase_action": phase_action,
            "reason": reason,
            "next_action": evaluation.next_action,
            "stop_reason": evaluation.stop_reason,
            "blocking_reasons": evaluation.blocking_reasons,
            "recommended_prompt": evaluation.recommended_prompt,
            "affected_artifacts": evaluation.affected_artifacts,
        }
        click.echo(json.dumps(data, indent=2))
        return

    click.echo("phase next: ok")
    click.echo(f"  active_phase      {evaluation.active_phase or '(unknown)'}")
    click.echo(f"  phase_action      {phase_action}")
    click.echo(f"  reason            {reason}")
    if evaluation.next_action:
        click.echo(f"  next_action       {evaluation.next_action}")
    if evaluation.stop_reason:
        click.echo(f"  stop_reason       {evaluation.stop_reason}")
    click.echo(f"  blocking_reasons  {len(evaluation.blocking_reasons)}")
    for item in evaluation.blocking_reasons:
        click.echo(f"    - {item}")


@phase_group.command("close")
@click.option("--dry-run", is_flag=True, default=False, help="Validate without writing anything.")
@click.pass_context
def phase_close(ctx, dry_run):
    """Validate and seal the current phase.

    Writes a grain-verified closed marker to current_focus.md.
    The workflow engine requires this marker before routing to the next phase.
    After running this command, update '## Current Phase' in
    docs/working/current_focus.md to begin the next phase.
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result = close_phase(root, dry_run=dry_run)

    if fmt == "json":
        click.echo(
            json.dumps(
                {
                    "ok": result.ok,
                    "closed_phase": result.closed_phase,
                    "tasks_done": result.tasks_done,
                    "dry_run": result.dry_run,
                    "marker_written": result.marker_written,
                    "errors": result.errors,
                },
                indent=2,
            )
        )
        if not result.ok:
            raise SystemExit(1)
        return

    if not result.ok:
        click.echo("phase close: blocked", err=True)
        for err in result.errors:
            click.echo(f"  error   {err}", err=True)
        raise SystemExit(1)

    label = "phase close: dry_run" if dry_run else "phase close: ok"
    click.echo(label)
    click.echo(f"  closed_phase    {result.closed_phase}")
    click.echo(f"  tasks_done      {result.tasks_done}")
    if result.marker_written:
        click.echo(f"  marker_written  {result.marker_written}")
    if dry_run:
        click.echo("  (no changes written)")
    else:
        click.echo(
            f"  next step       update '## Current Phase' in current_focus.md "
            f"to Phase {int(result.closed_phase) + 1} to begin the next phase"
        )


@phase_group.command("archive")
@click.argument("phase_number")
@click.option("--dry-run", is_flag=True, default=False, help="Show what would be moved without writing anything.")
@click.pass_context
def phase_archive(ctx, phase_number, dry_run):
    """Move closed phase packets to tasks/archive/phase-N/.

    PHASE_NUMBER is the phase to archive (e.g. 15).

    Requires a grain-verified closed marker in current_focus.md for the given
    phase. Use `grain phase close` to seal a phase before archiving.
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result = archive_phase(root, phase_number, dry_run=dry_run)

    if fmt == "json":
        click.echo(
            json.dumps(
                {
                    "ok": result.ok,
                    "phase": result.phase,
                    "packets_moved": result.packets_moved,
                    "archive_path": result.archive_path,
                    "dry_run": result.dry_run,
                    "errors": result.errors,
                },
                indent=2,
            )
        )
        if not result.ok:
            raise SystemExit(1)
        return

    if not result.ok:
        click.echo("phase archive: blocked", err=True)
        for err in result.errors:
            click.echo(f"  error   {err}", err=True)
        raise SystemExit(1)

    label = "phase archive: dry_run" if dry_run else "phase archive: ok"
    click.echo(label)
    click.echo(f"  phase           {result.phase}")
    click.echo(f"  archive_path    {result.archive_path}")
    click.echo(f"  packets_moved   {len(result.packets_moved)}")
    for p in result.packets_moved:
        click.echo(f"    - {p}")
    if dry_run:
        click.echo("  (no changes written)")
