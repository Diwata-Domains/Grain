# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""grain notes — tooling_notes.md CLI stub.

Full implementation is Phase 37. This stub unblocks agents that call
`grain notes add` to log friction without crashing.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import click

from grain.adapters.filesystem import resolve_repo_root

_NOTES_PATH = "docs/working/tooling_notes.md"
_TABLE_HEADER = "| Date | Type | Command | Observation | Severity | Status |"
_TABLE_SEP = "|------|------|---------|-------------|----------|--------|"


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
    """Append a row to docs/working/tooling_notes.md.

    \b
    Example:
      grain notes add "grain phase close requires workflow_metrics entry even when empty"
      grain notes add "init --name flag missing reminder" --severity medium
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    today = date.today().isoformat()
    row = f"| {today} | {note_type} | {command or '—'} | {message} | {severity} | open |"

    path = root / _NOTES_PATH
    _ensure_table(path)
    _append_row(path, row)

    if fmt == "json":
        click.echo(json.dumps({"ok": True, "path": _NOTES_PATH, "row": row}, indent=2))
    else:
        click.echo("notes add: ok")
        click.echo(f"  → {_NOTES_PATH}")


@notes_group.command("list")
@click.option("--status", default=None,
              type=click.Choice(["open", "closed", "all"]),
              help="Filter by status (default: open).")
@click.pass_context
def notes_list(ctx, status):
    """List entries from docs/working/tooling_notes.md."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    path = root / _NOTES_PATH
    if not path.exists():
        if fmt == "json":
            click.echo(json.dumps([], indent=2))
        else:
            click.echo("notes list: (empty — tooling_notes.md not found)")
        return

    entries = _parse_rows(path, status_filter=status or "open")

    if fmt == "json":
        click.echo(json.dumps(entries, indent=2))
        return

    if not entries:
        click.echo("notes list: (no matching entries)")
        return

    click.echo(f"notes list: {len(entries)} entry(ies)")
    for e in entries:
        sev_marker = {"high": "✗", "medium": "⚠", "low": "·"}.get(e.get("severity", ""), "·")
        click.echo(f"  {sev_marker}  {e['date']:<12} [{e['severity']:<6}] {e['observation']}")


def _ensure_table(path: Path) -> None:
    """Create the file with a header table if it doesn't exist or has no table."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"# Tooling Notes\n\nLightweight inbox for workflow friction and observations.\n\n"
            f"{_TABLE_HEADER}\n{_TABLE_SEP}\n",
            encoding="utf-8",
        )
        return

    content = path.read_text(encoding="utf-8")
    if _TABLE_HEADER not in content:
        path.write_text(
            content.rstrip("\n") + f"\n\n{_TABLE_HEADER}\n{_TABLE_SEP}\n",
            encoding="utf-8",
        )


def _append_row(path: Path, row: str) -> None:
    content = path.read_text(encoding="utf-8")
    # Insert after the separator line
    sep_pos = content.find(_TABLE_SEP)
    if sep_pos != -1:
        insert_pos = sep_pos + len(_TABLE_SEP)
        content = content[:insert_pos] + "\n" + row + content[insert_pos:]
    else:
        content = content.rstrip("\n") + "\n" + row + "\n"
    path.write_text(content, encoding="utf-8")


def _parse_rows(path: Path, status_filter: str = "open") -> list[dict]:
    _ROW_RE = re.compile(
        r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|"
    )
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = _ROW_RE.match(line)
        if not m:
            continue
        row_status = m.group(6).strip().lower()
        if status_filter != "all" and row_status != status_filter:
            continue
        entries.append({
            "date": m.group(1).strip(),
            "type": m.group(2).strip(),
            "command": m.group(3).strip(),
            "observation": m.group(4).strip(),
            "severity": m.group(5).strip().lower(),
            "status": row_status,
        })
    return entries
