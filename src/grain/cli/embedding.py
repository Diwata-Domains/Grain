# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

import dataclasses
import json

import click

from grain.adapters.filesystem import resolve_repo_root
from grain.services.embedding_service import inspect_embedding_provider


@click.group("embedding")
def embedding_group():
    """Inspect embedding-provider configuration and runtime resolution."""


@embedding_group.command("show")
@click.pass_context
def embedding_show(ctx):
    """Show the active embedding provider and fallback status."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, resolved = inspect_embedding_provider(root)
    status = resolved.provider_status

    if fmt == "json":
        data = dataclasses.asdict(result)
        data["embedding"] = dataclasses.asdict(resolved)
        click.echo(json.dumps(data, indent=2))
        return

    click.echo("embedding show: ok")
    click.echo(f"  configured_provider  {resolved.configured_provider}")
    click.echo(f"  active_provider      {resolved.active_provider}")
    click.echo(f"  configured_model     {resolved.configured_model}")
    click.echo(f"  active_model         {resolved.active_model}")
    click.echo(f"  fallback_active      {'yes' if resolved.fallback_active else 'no'}")
    if resolved.fallback_reason:
        click.echo(f"  fallback_reason      {resolved.fallback_reason}")
    if status is not None:
        click.echo(f"  available            {'yes' if status.available else 'no'}")
        click.echo(f"  status_provider      {status.provider_id}")
        click.echo(f"  status_model         {status.model_name}")
        if status.detail:
            click.echo(f"  detail               {status.detail}")
