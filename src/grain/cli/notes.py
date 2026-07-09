# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""grain notes — queryable friction inbox over docs/working/tooling_notes.md.

Notes are structured rows (id / type / status / created_at / body) appended with
an auto-incremented ID, a timestamp, and a default ``open`` status. The inbox is
queryable (`list`, `show`), resolvable (`resolve`), and feeds `grain docs audit`.
"""

from __future__ import annotations

import json
from pathlib import Path

import click

from grain.adapters.filesystem import resolve_repo_root

_NOTES_PATH = "docs/working/tooling_notes.md"


def _truncate(text: str, width: int) -> str:
    """Collapse whitespace and clip ``text`` to ``width`` display columns."""
    text = " ".join(text.split())
    return text if len(text) <= width else text[: width - 1] + "…"


@click.group("notes")
def notes_group():
    """Log and review tooling friction notes."""


@notes_group.command("add")
@click.argument("message")
@click.option("--type", "note_type", default="friction",
              type=click.Choice(["friction", "bug", "observation"]),
              help="Note type (default: friction).")
@click.option("--command", "command", default="",
              help="Command that triggered this note.")
@click.option("--severity", default="low",
              type=click.Choice(["low", "medium", "high"]),
              help="Severity (default: low).")
@click.pass_context
def notes_add(ctx, message, note_type, command, severity):
    """Append a structured note to docs/working/tooling_notes.md.

    \b
    Example:
      grain notes add "grain phase close requires workflow_metrics entry even when empty"
      grain notes add "init --name flag missing reminder" --type bug --severity medium
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    from grain.services.notes_service import add_note
    result = add_note(root, message, note_type=note_type, command=command, severity=severity)

    if fmt == "json":
        click.echo(json.dumps({
            "ok": result.ok,
            "path": result.path,
            "note": result.note.to_dict() if result.note else None,
            "errors": result.errors,
        }, indent=2))
        return

    if not result.ok:
        for e in result.errors:
            click.echo(f"error  {e}", err=True)
        raise click.ClickException("notes add failed")

    note = result.note
    click.echo("notes add: ok")
    click.echo(f"  id     {note.id}")
    click.echo(f"  → {result.path}")


@notes_group.command("list")
@click.option("--type", "type_filter", default=None,
              type=click.Choice(["friction", "bug", "observation"]),
              help="Filter by note type.")
@click.option("--status", "status_filter", default=None,
              type=click.Choice(
                  ["open", "closed", "resolved", "reported", "published", "all"]
              ),
              help="Filter by status (default: open).")
@click.option("--fleet", is_flag=True, default=False,
              help="Roll notes up across many workspaces given as ROOTS "
                   "(dedupes worktree copies; one finding per defect).")
@click.argument("roots", nargs=-1, type=click.Path())
@click.pass_context
def notes_list(ctx, type_filter, status_filter, fleet, roots):
    """List entries from docs/working/tooling_notes.md.

    \b
    Fleet rollup across workspaces:
      grain notes list --fleet ~/repos/a ~/repos/b
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"

    if fleet:
        _run_fleet_list(repo, roots, type_filter, status_filter, fmt)
        return
    if roots:
        raise click.UsageError("ROOTS are only accepted with --fleet")

    root = resolve_repo_root(repo)

    from grain.services.notes_service import list_notes
    result = list_notes(root, type_filter=type_filter, status_filter=status_filter)

    if fmt == "json":
        click.echo(json.dumps([n.to_dict() for n in result.notes], indent=2))
        return

    if not result.notes:
        click.echo("notes list: (no matching entries)")
        return

    click.echo(f"notes list: {len(result.notes)} entry(ies)")
    for n in result.notes:
        sev_marker = {"high": "✗", "medium": "⚠", "low": "·"}.get(n.severity, "·")
        click.echo(
            f"  {sev_marker}  #{n.id:<4} {n.created_at:<12} "
            f"[{n.type:<11}] [{n.status:<8}] {n.body}"
        )


def _fleet_roots(repo, roots) -> list[Path]:
    """Resolve the scan roots: explicit ROOTS, else the current workspace."""
    if roots:
        return [Path(r) for r in roots]
    return [resolve_repo_root(repo)]


def _run_fleet_list(repo, roots, type_filter, status_filter, fmt):
    from grain.services.notes_service import scan_fleet
    result = scan_fleet(
        _fleet_roots(repo, roots),
        type_filter=type_filter,
        status_filter=status_filter,
    )

    if fmt == "json":
        click.echo(json.dumps({
            "fleet": True,
            "workspaces": result.workspaces,
            "discovered": result.discovered,
            "skipped": {
                "archive": result.skipped_archive,
                "worktree": result.skipped_worktree,
                "template": result.skipped_template,
            },
            "findings": [
                {
                    "command": f.command,
                    "observation": f.observation,
                    "type": f.type,
                    "severity": f.severity,
                    "count": f.count,
                    "workspaces": f.workspaces,
                }
                for f in result.findings
            ],
        }, indent=2))
        return

    click.echo(
        f"notes list --fleet: {result.workspaces} workspace(s), "
        f"{len(result.findings)} distinct finding(s)"
    )
    click.echo(
        f"  scanned {result.discovered} inbox(es); collapsed "
        f"{result.skipped_worktree} worktree copy(ies); skipped "
        f"{result.skipped_archive} archive + {result.skipped_template} template"
    )
    if not result.findings:
        click.echo("  (no matching findings)")
        return
    for f in result.findings:
        sev_marker = {"high": "✗", "medium": "⚠", "low": "·"}.get(f.severity, "·")
        click.echo(f"  {sev_marker}  ×{f.count} [{f.type}] {f.command or '—'}")
        click.echo(f"        {_truncate(f.observation, 100)}")
        click.echo(f"        seen in: {', '.join(f.workspaces)}")


@notes_group.command("show")
@click.argument("note_id", type=int)
@click.pass_context
def notes_show(ctx, note_id):
    """Show a single note by ID."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    from grain.services.notes_service import show_note
    result = show_note(root, note_id)

    if fmt == "json":
        click.echo(json.dumps({
            "ok": result.ok,
            "note": result.note.to_dict() if result.note else None,
            "errors": result.errors,
        }, indent=2))
        return

    if not result.ok:
        for e in result.errors:
            click.echo(f"error  {e}", err=True)
        raise click.UsageError(f"note not found: {note_id}")

    n = result.note
    click.echo(f"notes show: #{n.id}")
    click.echo(f"  created   {n.created_at}")
    click.echo(f"  type      {n.type}")
    click.echo(f"  status    {n.status}")
    click.echo(f"  severity  {n.severity}")
    if n.command:
        click.echo(f"  command   {n.command}")
    click.echo(f"  body      {n.body}")


@notes_group.command("resolve")
@click.argument("note_id", type=int)
@click.argument("resolution", required=False, default="")
@click.pass_context
def notes_resolve(ctx, note_id, resolution):
    """Mark a note resolved, optionally recording a resolution note.

    \b
    Example:
      grain notes resolve 3
      grain notes resolve 3 "fixed in TASK-0217 — auto ID allocation added"
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    from grain.services.notes_service import resolve_note
    result = resolve_note(root, note_id, resolution)

    if fmt == "json":
        click.echo(json.dumps({
            "ok": result.ok,
            "note": result.note.to_dict() if result.note else None,
            "errors": result.errors,
        }, indent=2))
        return

    if not result.ok:
        for e in result.errors:
            click.echo(f"error  {e}", err=True)
        raise click.UsageError(f"could not resolve note: {note_id}")

    n = result.note
    click.echo("notes resolve: ok")
    click.echo(f"  id      {n.id}")
    click.echo(f"  status  {n.status}")
    click.echo(f"  → {result.path}")


@notes_group.command("publish")
@click.argument("note_id", type=int)
@click.pass_context
def notes_publish(ctx, note_id):
    """File a note as an issue in github.repo via the API, then mark it published.

    Headless, no browser. Maps the note type to a label (bug→bug,
    friction/feature→enhancement). The token is read from GRAIN_GITHUB_TOKEN
    only — never written to workspace files. A missing token yields a clear,
    non-crashing error.

    \b
    Example:
      GRAIN_GITHUB_TOKEN=ghp_... grain notes publish 3
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    from grain.adapters.manifest import load_github_config
    from grain.services.github_service import (
        build_issue_body,
        build_issue_title,
        create_issue,
        label_for_type,
    )
    from grain.services.notes_service import set_note_status, show_note

    note_result = show_note(root, note_id)
    if not note_result.ok:
        if fmt == "json":
            click.echo(json.dumps(
                {"ok": False, "errors": note_result.errors}, indent=2,
            ))
            return
        for e in note_result.errors:
            click.echo(f"error  {e}", err=True)
        raise click.UsageError(f"note not found: {note_id}")

    note = note_result.note
    gh = load_github_config(root)
    label = label_for_type(note.type)
    title = build_issue_title(note.type, note.command, note.body)
    body = build_issue_body(note.body, severity=note.severity)

    result = create_issue(gh.repo, title, body, [label])

    marked = False
    if result.ok:
        marked = set_note_status(root, note_id, "published").ok

    if fmt == "json":
        click.echo(json.dumps({
            "ok": result.ok,
            "id": note_id,
            "issue_url": result.issue_url,
            "issue_number": result.issue_number,
            "labels": result.labels,
            "repo": result.repo,
            "published": marked,
            "errors": result.errors,
        }, indent=2))
        return

    if not result.ok:
        for e in result.errors:
            click.echo(f"error  {e}", err=True)
        raise click.ClickException("notes publish failed")

    click.echo("notes publish: ok")
    click.echo(f"  id      {note_id}")
    click.echo(f"  label   {', '.join(result.labels)}")
    if marked:
        click.echo("  status  published")
    click.echo(f"  → {result.issue_url}")


@notes_group.command("triage")
@click.option("--resolve-stale", is_flag=True, default=False,
              help="Resolve the stale candidates (default: dry-run — nothing "
                   "is mutated).")
@click.option("--fleet", is_flag=True, default=False,
              help="Triage across many workspaces given as ROOTS "
                   "(one replay per deduped defect).")
@click.argument("roots", nargs=-1, type=click.Path())
@click.pass_context
def notes_triage(ctx, resolve_stale, fleet, roots):
    """Replay each open note's recorded command and classify it.

    Replay is a HEURISTIC: a note is a closure *candidate* only when its command
    now exits 0 in a throwaway workspace. Anything that still errors stays open;
    empty/free-prose commands need a human. Dry-run by default — pass
    ``--resolve-stale`` to resolve the candidates, recording the fixing version.

    \b
    Example:
      grain notes triage                 # dry-run report
      grain notes triage --resolve-stale # close the stale ones
      grain notes triage --fleet ~/a ~/b # rollup + replay across repos
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"

    from grain.services.notes_service import triage_fleet, triage_notes

    if fleet:
        result = triage_fleet(
            _fleet_roots(repo, roots), resolve_stale=resolve_stale,
        )
    else:
        if roots:
            raise click.UsageError("ROOTS are only accepted with --fleet")
        result = triage_notes(resolve_repo_root(repo), resolve_stale=resolve_stale)

    if fmt == "json":
        _emit_triage_json(result)
        return
    _emit_triage_text(result)


_VERDICT_LABEL = {"stale": "stale ✓", "open": "open  ·", "human": "human ?"}


def _emit_triage_text(result) -> None:
    scope = "fleet" if result.fleet else "local"
    mode = "resolve-stale" if not result.dry_run else "dry-run"
    click.echo(f"notes triage ({scope}, {mode}) — grain {result.version}")
    click.echo(
        "  replay is a heuristic: a note is a closure candidate only when its "
        "recorded command now exits 0 in a throwaway workspace."
    )
    click.echo(
        f"  {len(result.stale)} stale candidate(s) · "
        f"{len(result.still_open)} still open · "
        f"{len(result.needs_human)} need human"
    )
    if not result.items:
        click.echo("  (no open notes to triage)")
        return
    click.echo("")
    for item in result.items:
        note = item.note
        label = _VERDICT_LABEL.get(item.verdict, item.verdict)
        exit_str = (
            "" if item.replay.exit_code is None
            else f" exit={item.replay.exit_code}"
        )
        span = f" ×{len(item.workspaces)}" if result.fleet else ""
        cmd = item.replay.command or item.note.command or "—"
        click.echo(f"  [{label}]{span} #{note.id} {cmd}{exit_str}")
        click.echo(f"        {_truncate(note.body, 100)}")
        if item.resolved:
            click.echo(f"        → resolved {item.resolved} note(s)")
    if result.dry_run and result.stale:
        click.echo("")
        click.echo("  re-run with --resolve-stale to resolve the candidate(s).")


def _emit_triage_json(result) -> None:
    click.echo(json.dumps({
        "fleet": result.fleet,
        "dry_run": result.dry_run,
        "version": result.version,
        "resolved_count": result.resolved_count,
        "summary": {
            "stale": len(result.stale),
            "open": len(result.still_open),
            "human": len(result.needs_human),
        },
        "items": [
            {
                "id": i.note.id,
                "verdict": i.verdict,
                "command": i.replay.command or i.note.command,
                "observation": i.note.body,
                "replayable": i.replay.replayable,
                "exit_code": i.replay.exit_code,
                "workspaces": i.workspaces,
                "resolved": i.resolved,
            }
            for i in result.items
        ],
    }, indent=2))
