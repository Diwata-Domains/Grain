"""CLI command for upgrading Grain-managed files to the current bundled versions."""

from __future__ import annotations

import json
from pathlib import Path

import click

from grain.services.upgrade_service import upgrade_repo


@click.command("upgrade")
@click.option("--dry-run", is_flag=True, default=False, help="Preview changes without writing.")
@click.option(
    "--format",
    "local_fmt",
    type=click.Choice(["text", "json"]),
    default=None,
    help="Output format override for this command.",
)
@click.pass_context
def upgrade_cmd(ctx, dry_run: bool, local_fmt: str | None) -> None:
    """Update Grain-managed prompts and templates to the current installed version.

    Updates: prompts, task templates, safe runtime docs.

    Never touches: canonical docs, working docs, task packets,
    docs_manifest.yaml, adapter_profiles.md.
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = local_fmt or (ctx.obj.get("fmt", "text") if ctx.obj else "text")

    if repo:
        root = Path(repo).resolve()
    else:
        from grain.adapters.filesystem import resolve_repo_root
        root = resolve_repo_root(None)

    result = upgrade_repo(root, dry_run=dry_run)

    if fmt == "json":
        click.echo(
            json.dumps(
                {
                    "updated": result.updated,
                    "added": result.added,
                    "unchanged": result.unchanged,
                    "protected": result.protected,
                    "dry_run": dry_run,
                },
                indent=2,
            )
        )
        return

    status = "dry-run" if dry_run else "ok"
    click.echo(f"upgrade: {status}")
    if dry_run:
        click.echo("  dry_run           true")

    click.echo("Updated:")
    for rel in result.updated:
        click.echo(f"- {rel}")
    if not result.updated:
        click.echo("- (none)")

    click.echo("Added:")
    for rel in result.added:
        click.echo(f"- {rel}")
    if not result.added:
        click.echo("- (none)")

    click.echo("Unchanged:")
    for rel in result.unchanged:
        click.echo(f"- {rel}")
    if not result.unchanged:
        click.echo("- (none)")

    click.echo("Protected (not touched):")
    for rel in result.protected:
        click.echo(f"- {rel}")
