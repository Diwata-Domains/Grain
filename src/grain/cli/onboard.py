# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""CLI command for additive existing-project scaffold onboarding."""

from __future__ import annotations

import json
from pathlib import Path

import click

from grain.services.onboard_service import OnboardService


@click.command("onboard")
@click.argument("path", required=False, default=".")
@click.option("--dry-run", is_flag=True, default=False, show_default=True, help="Report intended scaffold actions without writing.")
@click.option(
    "--format",
    "local_fmt",
    type=click.Choice(["text", "json"]),
    default=None,
    help="Output format override for this command.",
)
@click.pass_context
def onboard_cmd(ctx, path: str, dry_run: bool, local_fmt: str | None) -> None:
    """Scaffold Grain directory structure into an existing repository path."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = local_fmt or (ctx.obj.get("fmt", "text") if ctx.obj else "text")

    if path == "." and repo:
        target = Path(repo).resolve()
    else:
        target = Path(path).resolve()

    if not target.exists() or not target.is_dir():
        raise click.UsageError(f"Onboard path must be an existing directory: {target}")

    manifest = OnboardService(target).scaffold(dry_run=dry_run)

    if fmt == "json":
        click.echo(
            json.dumps(
                {
                    "created": manifest.created,
                    "skipped": manifest.skipped,
                    "root": manifest.root,
                    "agents_md_action": manifest.agents_md_action,
                    "claude_md_exists": manifest.claude_md_exists,
                },
                indent=2,
            )
        )
        return

    click.echo("onboard: ok")
    click.echo(f"  root              {manifest.root}")
    if dry_run:
        click.echo("  dry_run           true")
    click.echo("Created:")
    for rel in manifest.created:
        click.echo(f"- {rel}")
    click.echo("Skipped:")
    for rel in manifest.skipped:
        click.echo(f"- {rel}")
    if manifest.agents_md_action and manifest.agents_md_action != "skipped":
        _agents_note = {
            "created": "AGENTS.md created with grain workflow instructions",
            "updated": "AGENTS.md grain block updated",
            "appended": "grain workflow instructions appended to existing AGENTS.md",
        }.get(manifest.agents_md_action, "")
        if _agents_note:
            click.echo(f"Note: {_agents_note}")
        if manifest.claude_md_exists:
            click.echo("Note: CLAUDE.md also exists — grain block is in AGENTS.md which Claude Code reads")
