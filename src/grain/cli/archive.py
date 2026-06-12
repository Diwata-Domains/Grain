"""CLI command group for grain archive operations."""

from __future__ import annotations

import json
import re

import click

from grain.adapters.filesystem import resolve_repo_root


@click.group("archive")
def archive_group():
    """Manage working doc snapshots, phase archives, and milestone archives."""


@archive_group.command("snapshot")
@click.option("--label", default=None, help="Optional label for the snapshot directory.")
@click.option("--dry-run", is_flag=True, default=False, help="Preview without writing.")
@click.pass_context
def archive_snapshot(ctx, label, dry_run):
    """Snapshot docs/working/ to docs/archive/snapshots/<YYYYMMDD>-<label>."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    from grain.services.archive_service import snapshot_working_docs
    result = snapshot_working_docs(root, label=label, dry_run=dry_run)

    if fmt == "json":
        click.echo(json.dumps({
            "ok": result.ok,
            "archive_path": result.archive_path,
            "files_written": result.files_written,
            "dry_run": result.dry_run,
            "errors": result.errors,
        }, indent=2))
        return

    if not result.ok:
        for e in result.errors:
            click.echo(f"error  {e}", err=True)
        raise click.ClickException("snapshot failed")

    status = "dry-run" if dry_run else "ok"
    click.echo(f"archive snapshot: {status}")
    click.echo(f"  path   {result.archive_path}")
    click.echo(f"  files  {len(result.files_written)}")
    if dry_run:
        for f in result.files_written:
            click.echo(f"  +  {f}")


@archive_group.command("milestone")
@click.argument("version")
@click.option("--dry-run", is_flag=True, default=False, help="Preview without writing.")
@click.pass_context
def archive_milestone_cmd(ctx, version, dry_run):
    """Create a milestone archive at docs/archive/milestones/<version>/.

    Includes snapshots of docs/working/, docs/canonical/, a tasks_index.json,
    and metadata.json. Does not auto-commit — add to the release commit manually.
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    from grain.services.archive_service import archive_milestone
    result = archive_milestone(root, version, dry_run=dry_run)

    if fmt == "json":
        click.echo(json.dumps({
            "ok": result.ok,
            "archive_path": result.archive_path,
            "files_written": result.files_written,
            "tasks_count": result.tasks_count,
            "dry_run": result.dry_run,
            "errors": result.errors,
        }, indent=2))
        return

    if not result.ok:
        for e in result.errors:
            click.echo(f"error  {e}", err=True)
        raise click.ClickException("milestone archive failed")

    status = "dry-run" if dry_run else "ok"
    click.echo(f"archive milestone: {status}")
    click.echo(f"  version  {version}")
    click.echo(f"  path     {result.archive_path}")
    click.echo(f"  tasks    {result.tasks_count}")
    click.echo(f"  files    {len(result.files_written)}")
    if not dry_run:
        click.echo("  note     commit this archive as part of your release commit")


@archive_group.command("list")
@click.option("--type", "type_filter", default=None,
              type=click.Choice(["phase", "milestone", "snapshot"]),
              help="Filter by archive type.")
@click.pass_context
def archive_list(ctx, type_filter):
    """List all archives (phases, milestones, snapshots)."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    from grain.services.archive_service import list_archives
    entries = list_archives(root, type_filter=type_filter)

    if fmt == "json":
        click.echo(json.dumps([
            {
                "type": e.type,
                "name": e.name,
                "path": e.path,
                "date": e.date,
                "metadata": e.metadata,
            }
            for e in entries
        ], indent=2))
        return

    if not entries:
        click.echo("archive list: (empty)")
        return

    click.echo("archive list:")
    for e in entries:
        extra = ""
        if e.type == "phase" and e.metadata.get("tasks_done"):
            extra = f"  ({e.metadata['tasks_done']} tasks)"
        elif e.type == "snapshot" and e.metadata.get("label"):
            extra = f"  ({e.metadata['label']})"
        elif e.type == "milestone" and e.metadata.get("tasks_count"):
            extra = f"  ({e.metadata['tasks_count']} tasks)"
        click.echo(f"  {e.name:<30} {e.type:<12} {e.date}{extra}")


@archive_group.command("show")
@click.argument("target")
@click.pass_context
def archive_show(ctx, target):
    """Show contents and metadata of an archive.

    TARGET can be a phase name (phase-30), milestone version (v0.4.0),
    or snapshot name (20260611-pre-refactor).
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    from grain.services.archive_service import show_archive
    result = show_archive(root, target)

    if fmt == "json":
        click.echo(json.dumps({
            "ok": result.ok,
            "name": result.name,
            "type": result.archive_type,
            "files": result.files,
            "metadata": result.metadata,
            "errors": result.errors,
        }, indent=2))
        return

    if not result.ok:
        for e in result.errors:
            click.echo(f"error  {e}", err=True)
        raise click.ClickException(f"archive not found: {target!r}")

    click.echo(f"archive show: {result.name}")
    click.echo(f"  type   {result.archive_type}")
    if result.metadata:
        for k, v in result.metadata.items():
            click.echo(f"  {k:<10} {v}")
    click.echo(f"  files  ({len(result.files)})")
    for f in result.files:
        click.echo(f"    {f}")


@archive_group.command("prune")
@click.option("--older-than", "older_than", required=True,
              help="Remove archived proposals older than this (e.g. 90d).")
@click.option("--dry-run", is_flag=True, default=False, help="Preview without deleting.")
@click.pass_context
def archive_prune(ctx, older_than, dry_run):
    """Remove archived proposals older than the given threshold.

    Only removes files from docs/archive/proposals/ — never touches
    phase archives, milestone archives, or snapshots.

    \b
    Example:
      grain archive prune --older-than 90d
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    days = _parse_days(older_than)
    if days is None:
        raise click.UsageError(f"cannot parse --older-than value: {older_than!r} (use e.g. 90d)")

    from grain.services.archive_service import prune_archived_proposals
    result = prune_archived_proposals(root, days, dry_run=dry_run)

    if fmt == "json":
        click.echo(json.dumps({
            "ok": result.ok,
            "pruned": result.pruned,
            "dry_run": result.dry_run,
        }, indent=2))
        return

    status = "dry-run" if dry_run else "ok"
    click.echo(f"archive prune: {status}")
    if result.pruned:
        for p in result.pruned:
            click.echo(f"  {'(would remove)' if dry_run else 'removed'}  {p}")
    else:
        click.echo("  (nothing to prune)")


def _parse_days(value: str) -> int | None:
    m = re.match(r"^(\d+)d$", value.strip())
    if m:
        return int(m.group(1))
    try:
        return int(value)
    except ValueError:
        return None
