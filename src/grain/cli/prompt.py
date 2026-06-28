# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

import dataclasses
import json

import click

from grain.adapters.filesystem import resolve_repo_root


@click.group("prompt")
def prompt_group():
    """Prompt entrypoint commands."""


@prompt_group.command("show")
@click.pass_context
def prompt_show(ctx):
    """Surface the recommended stable prompt entrypoint for current state."""
    from grain.services.prompt_service import show_prompt

    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, payload = show_prompt(root)

    if payload is None:
        if fmt == "json":
            click.echo(json.dumps(dataclasses.asdict(result), indent=2))
        else:
            click.echo("prompt show: failed")
            for err in result.errors:
                click.echo(f"  error     {err}", err=True)
        raise click.ClickException("prompt show failed")

    if fmt == "json":
        data = dataclasses.asdict(result)
        data["prompt"] = payload
        click.echo(json.dumps(data, indent=2))
        return

    label = "ok" if result.ok else "stopped"
    click.echo(f"prompt show: {label}")
    click.echo(f"  recommended_prompt  {payload['recommended_prompt']}")
    click.echo(f"  prompt_exists       {payload['prompt_exists']}")
    if payload["model_class"]:
        click.echo(f"  model_class         {payload['model_class']}")
    if payload["escalation_model_class"]:
        click.echo(f"  escalation_class    {payload['escalation_model_class']}")
    if payload["scope"]:
        click.echo(f"  scope               {payload['scope']}")
    if payload["stage"]:
        click.echo(f"  stage               {payload['stage']}")
    if payload["next_action"]:
        click.echo(f"  next_action         {payload['next_action']}")
    if payload["stop_reason"]:
        click.echo(f"  stop_reason         {payload['stop_reason']}")
    click.echo(f"  active_phase        {payload['active_phase'] or '(unknown)'}")
    if payload["active_task_id"]:
        click.echo(f"  active_task_id      {payload['active_task_id']}")
    if payload["blocking_reasons"]:
        click.echo(f"  blocking_reasons    {len(payload['blocking_reasons'])}")
        for reason in payload["blocking_reasons"]:
            click.echo(f"    - {reason}")
