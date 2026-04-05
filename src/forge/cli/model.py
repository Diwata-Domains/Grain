import dataclasses
import json

import click

from forge.adapters.filesystem import resolve_repo_root
from forge.adapters.model_config import load_model_profiles


@click.group("model")
def model_group():
    """Inspect model class routing and routing decisions."""


@model_group.command("show")
@click.pass_context
def model_show(ctx):
    """Show configured model classes and profiles."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    config = load_model_profiles(root)

    if fmt == "json":
        data = {
            "ok": True,
            "command": "model show",
            "repo": str(root),
            "model_profiles": [
                dataclasses.asdict(profile)
                for profile in config.profiles
            ],
            "escalation_rules": [
                dataclasses.asdict(rule)
                for rule in config.escalation_rules
            ],
            "source_path": config.source_path,
        }
        click.echo(json.dumps(data, indent=2))
        return

    click.echo("model show: ok")
    click.echo(f"  source            {config.source_path}")
    click.echo(f"  model_classes     {len(config.profiles)}")
    for profile in config.profiles:
        click.echo(f"  class             {profile.model_class}")
        click.echo(
            "    use_for         "
            + (", ".join(profile.use_for) if profile.use_for else "(none)")
        )
        click.echo(
            "    avoid_for       "
            + (", ".join(profile.avoid_for) if profile.avoid_for else "(none)")
        )
        click.echo(
            "    preferred       "
            + (
                ", ".join(profile.preferred_models)
                if profile.preferred_models
                else "(none)"
            )
        )
        click.echo(
            "    escalate_to     "
            + (
                ", ".join(profile.escalation_targets)
                if profile.escalation_targets
                else "(none)"
            )
        )


@model_group.command("select")
@click.option("--stage", default=None, help="Workflow stage name to route.")
@click.option("--role", default=None, help="Task role to route.")
@click.pass_context
def model_select(ctx, stage, role):
    """Resolve which model class should be used for a workflow stage or task."""
    if not stage and not role:
        raise click.UsageError("At least one of --stage or --role is required.")

    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    from forge.services.model_service import select_model_for_stage_or_role

    result, decision = select_model_for_stage_or_role(root, stage=stage, role=role)

    if not result.ok:
        if fmt == "json":
            data = {"ok": False, "command": "model select", "errors": result.errors}
            click.echo(json.dumps(data, indent=2))
        else:
            for err in result.errors:
                click.echo(f"error: {err}", err=True)
        ctx.exit(1)
        return

    if fmt == "json":
        data = {
            "ok": True,
            "command": "model select",
            "repo": str(root),
            "selected_class": decision.selected_class,
            "reason": decision.reason,
            "stage": decision.stage,
            "role": decision.role,
        }
        click.echo(json.dumps(data, indent=2))
        return

    click.echo("model select: ok")
    click.echo(f"  selected_class    {decision.selected_class}")
    click.echo(f"  reason            {decision.reason}")
    if decision.stage:
        click.echo(f"  stage             {decision.stage}")
    if decision.role:
        click.echo(f"  role              {decision.role}")


@model_group.command("escalate")
def model_escalate():
    """Promote a task or stage from one model class to another."""
