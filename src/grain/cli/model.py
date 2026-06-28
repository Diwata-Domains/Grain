# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

import dataclasses
import json

import click

from grain.adapters.filesystem import resolve_repo_root
from grain.adapters.model_config import load_model_profiles
from grain.services.model_service import escalate_model_for_class, select_model_for_stage_or_role


@click.group("model")
def model_group():
    """Inspect model class routing and routing decisions."""


def _print_model_failure(command: str, errors: list[str], context: dict[str, str] | None = None) -> None:
    """Render model command failures in the same style as other CLI groups."""
    click.echo(f"{command}: failed")
    if context:
        for key, value in context.items():
            if value:
                click.echo(f"  {key:<16}{value}")
    for err in errors:
        click.echo(f"  error     {err}", err=True)
    if any("agent_profiles.md" in err for err in errors):
        click.echo(
            "  hint      ensure docs/runtime/agent_profiles.md exists in the target repo",
            err=True,
        )


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
@click.option(
    "--stage",
    default=None,
    help="Workflow stage name to route. At least one of --stage or --role is required.",
)
@click.option(
    "--role",
    default=None,
    help="Task role to route. At least one of --stage or --role is required.",
)
@click.pass_context
def model_select(ctx, stage, role):
    """Resolve which model class should be used for a workflow stage or task."""
    if not stage and not role:
        raise click.UsageError("At least one of --stage or --role is required.")

    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, decision = select_model_for_stage_or_role(root, stage=stage, role=role)

    if not result.ok:
        if fmt == "json":
            data = {
                "ok": False,
                "command": "model select",
                "errors": result.errors,
                "stage": stage,
                "role": role,
            }
            click.echo(json.dumps(data, indent=2))
        else:
            _print_model_failure(
                "model select",
                result.errors,
                context={"stage": stage or "", "role": role or ""},
            )
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
@click.option("--from-class", "from_class", required=True, help="Model class to escalate from.")
@click.option("--reason", default=None, help="Reason for escalation (advisory).")
@click.pass_context
def model_escalate(ctx, from_class, reason):
    """Promote a task or stage from one model class to another."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, target = escalate_model_for_class(root, current_class=from_class, reason=reason)

    if not result.ok:
        if fmt == "json":
            data = {
                "ok": False,
                "command": "model escalate",
                "errors": result.errors,
                "from_class": from_class,
                "reason": reason or "",
            }
            click.echo(json.dumps(data, indent=2))
        else:
            _print_model_failure(
                "model escalate",
                result.errors,
                context={"from_class": from_class, "reason": reason or ""},
            )
        ctx.exit(1)
        return

    if fmt == "json":
        data = {
            "ok": True,
            "command": "model escalate",
            "repo": str(root),
            "from_class": from_class,
            "target_class": target,
            "reason": reason or "",
        }
        click.echo(json.dumps(data, indent=2))
        return

    click.echo("model escalate: ok")
    click.echo(f"  from_class        {from_class}")
    click.echo(f"  target_class      {target}")
    if reason:
        click.echo(f"  reason            {reason}")
