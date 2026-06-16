# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

import json

import click

from grain.adapters.filesystem import resolve_repo_root
from grain.services.hooks_service import install_hooks, status_hooks, uninstall_hooks


@click.group("hooks")
def hooks_group():
    """Manage Grain-managed git hooks."""


@hooks_group.command("install")
@click.option("--dry-run", is_flag=True, default=False, help="Show what would be written without writing.")
@click.pass_context
def hooks_install(ctx, dry_run):
    """Write pre-commit and post-checkout hooks to .git/hooks/.

    Skips any hook that already exists and is not grain-managed.
    Re-running is safe — existing up-to-date hooks are skipped.
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result = install_hooks(root, dry_run=dry_run)

    if fmt == "json":
        click.echo(json.dumps({
            "ok": result.ok,
            "installed": result.installed,
            "skipped": result.skipped,
            "errors": result.errors,
            "dry_run": result.dry_run,
        }, indent=2))
        if not result.ok:
            raise SystemExit(1)
        return

    label = "hooks install: dry_run" if dry_run else "hooks install: ok"
    if not result.ok and not result.installed:
        label = "hooks install: blocked"
    click.echo(label)
    for name in result.installed:
        click.echo(f"  written   {name}")
    for name in result.skipped:
        click.echo(f"  skipped   {name}")
    for err in result.errors:
        click.echo(f"  error     {err}", err=True)
    if not result.installed and not result.errors:
        click.echo("  (all hooks already up to date)")
    if not result.ok:
        raise SystemExit(1)


@hooks_group.command("uninstall")
@click.option("--dry-run", is_flag=True, default=False, help="Show what would be removed without removing.")
@click.pass_context
def hooks_uninstall(ctx, dry_run):
    """Remove Grain-managed hooks from .git/hooks/.

    Only removes hooks that Grain wrote — non-grain hooks are untouched.
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result = uninstall_hooks(root, dry_run=dry_run)

    if fmt == "json":
        click.echo(json.dumps({
            "ok": result.ok,
            "removed": result.removed,
            "skipped": result.skipped,
            "errors": result.errors,
            "dry_run": result.dry_run,
        }, indent=2))
        if not result.ok:
            raise SystemExit(1)
        return

    label = "hooks uninstall: dry_run" if dry_run else "hooks uninstall: ok"
    click.echo(label)
    for name in result.removed:
        click.echo(f"  removed   {name}")
    for name in result.skipped:
        click.echo(f"  skipped   {name}")
    for err in result.errors:
        click.echo(f"  error     {err}", err=True)
    if not result.ok:
        raise SystemExit(1)


@hooks_group.command("status")
@click.pass_context
def hooks_status(ctx):
    """Show whether Grain hooks are installed and up to date."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result = status_hooks(root)

    if fmt == "json":
        click.echo(json.dumps({
            "ok": result.ok,
            "statuses": [
                {
                    "hook_name": s.hook_name,
                    "installed": s.installed,
                    "current": s.current,
                    "grain_managed": s.grain_managed,
                    "path": s.path,
                }
                for s in result.statuses
            ],
        }, indent=2))
        return

    click.echo("hooks status:")
    _SYM = {(True, True): "✓", (True, False): "⚠", (False, False): "✗"}
    for s in result.statuses:
        sym = _SYM.get((s.installed, s.current), "?")
        note = ""
        if s.installed and not s.current:
            note = " (outdated — re-run grain hooks install)"
        elif s.installed and not s.grain_managed:
            note = " (not grain-managed)"
        elif not s.installed:
            note = " (not installed)"
        click.echo(f"  {sym} {s.hook_name}{note}")
