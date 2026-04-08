import dataclasses
import json

import click

from forge.adapters.filesystem import resolve_repo_root
from forge.services.workflow_service import evaluate_workflow_state


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
