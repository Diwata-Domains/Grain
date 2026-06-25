# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Notes service — read/write the queryable friction inbox.

Backs ``grain notes`` against the single human-readable file
``docs/working/tooling_notes.md``. Rows are stored as markdown table rows with
an auto-incremented ID, timestamp, and a default ``open`` status. Legacy rows
written before IDs existed are normalized on read so they remain addressable
without ever being dropped.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from grain.domain.notes import (
    TABLE_HEADER,
    TABLE_SEP,
    Note,
    parse_note_line,
)

_NOTES_PATH = "docs/working/tooling_notes.md"

_FILE_PREAMBLE = (
    "# Tooling Notes\n\n"
    "Lightweight inbox for workflow friction, tool bugs, or observations noticed mid-session.\n"
    "Agents write here; user reviews and escalates to the appropriate tracker.\n\n"
)


# ── Result types ──────────────────────────────────────────────────────────────

@dataclass
class NoteAddResult:
    ok: bool
    note: Note | None = None
    path: str = ""
    errors: list[str] = field(default_factory=list)


@dataclass
class NoteListResult:
    ok: bool
    notes: list[Note] = field(default_factory=list)
    path: str = ""
    errors: list[str] = field(default_factory=list)


@dataclass
class NoteShowResult:
    ok: bool
    note: Note | None = None
    path: str = ""
    errors: list[str] = field(default_factory=list)


@dataclass
class NoteResolveResult:
    ok: bool
    note: Note | None = None
    path: str = ""
    errors: list[str] = field(default_factory=list)


# ── Public API ────────────────────────────────────────────────────────────────

def add_note(
    root: Path,
    body: str,
    *,
    note_type: str = "friction",
    command: str = "",
    severity: str = "low",
) -> NoteAddResult:
    """Append a structured note with an auto ID, timestamp, and ``open`` status."""
    path = root / _NOTES_PATH
    rel = str(Path(_NOTES_PATH))

    text = body.strip()
    if not text:
        return NoteAddResult(ok=False, path=rel, errors=["note body is empty"])

    existing = _read_notes(path)
    next_id = (max((n.id for n in existing), default=0)) + 1

    note = Note(
        id=next_id,
        created_at=date.today().isoformat(),
        type=note_type,
        command=command,
        body=text,
        severity=severity,
        status="open",
    )

    _ensure_table(path)
    _append_row(path, note.to_row())
    return NoteAddResult(ok=True, note=note, path=rel)


def list_notes(
    root: Path,
    *,
    type_filter: str | None = None,
    status_filter: str | None = None,
) -> NoteListResult:
    """Return notes filtered by type and/or status (default: open only)."""
    path = root / _NOTES_PATH
    rel = str(Path(_NOTES_PATH))
    if not path.exists():
        return NoteListResult(ok=True, notes=[], path=rel)

    notes = _read_notes(path)
    effective_status = "open" if status_filter is None else status_filter

    selected: list[Note] = []
    for n in notes:
        if type_filter and n.type != type_filter:
            continue
        if effective_status != "all" and n.status != effective_status:
            continue
        selected.append(n)
    return NoteListResult(ok=True, notes=selected, path=rel)


def show_note(root: Path, note_id: int) -> NoteShowResult:
    """Return a single note by ID."""
    path = root / _NOTES_PATH
    rel = str(Path(_NOTES_PATH))
    if not path.exists():
        return NoteShowResult(ok=False, path=rel, errors=[f"note {note_id} not found"])

    for n in _read_notes(path):
        if n.id == note_id:
            return NoteShowResult(ok=True, note=n, path=rel)
    return NoteShowResult(ok=False, path=rel, errors=[f"note {note_id} not found"])


def resolve_note(root: Path, note_id: int, resolution: str = "") -> NoteResolveResult:
    """Flip a note to ``resolved`` and optionally append a resolution note."""
    path = root / _NOTES_PATH
    rel = str(Path(_NOTES_PATH))
    if not path.exists():
        return NoteResolveResult(ok=False, path=rel, errors=[f"note {note_id} not found"])

    notes = _read_notes(path)
    target = next((n for n in notes if n.id == note_id), None)
    if target is None:
        return NoteResolveResult(ok=False, path=rel, errors=[f"note {note_id} not found"])

    if target.status == "resolved":
        return NoteResolveResult(
            ok=False, note=target, path=rel,
            errors=[f"note {note_id} is already resolved"],
        )

    target.status = "resolved"
    if resolution.strip():
        suffix = f" — resolved: {resolution.strip()}"
        if suffix not in target.body:
            target.body = f"{target.body}{suffix}"

    _rewrite_notes(path, notes)
    return NoteResolveResult(ok=True, note=target, path=rel)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _read_notes(path: Path) -> list[Note]:
    """Parse every data row from the notes file, normalizing legacy rows.

    Legacy (un-IDed) rows are assigned synthesized IDs that do not collide with
    explicit IDs already present in the file.
    """
    if not path.exists():
        return []

    explicit: list[Note] = []
    legacy_lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        note = parse_note_line(line, fallback_id=-1)
        if note is None:
            continue
        if note.id == -1:
            legacy_lines.append(line)
        else:
            explicit.append(note)

    # Allocate synthesized IDs for legacy rows above the explicit max.
    next_synth = (max((n.id for n in explicit), default=0)) + 1
    legacy: list[Note] = []
    for line in legacy_lines:
        note = parse_note_line(line, fallback_id=next_synth)
        if note is not None:
            legacy.append(note)
            next_synth += 1

    return explicit + legacy


def _ensure_table(path: Path) -> None:
    """Create the file (or append a structured header) if needed."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{_FILE_PREAMBLE}{TABLE_HEADER}\n{TABLE_SEP}\n", encoding="utf-8")
        return

    content = path.read_text(encoding="utf-8")
    if TABLE_HEADER not in content:
        path.write_text(
            content.rstrip("\n") + f"\n\n{TABLE_HEADER}\n{TABLE_SEP}\n",
            encoding="utf-8",
        )


def _append_row(path: Path, row: str) -> None:
    content = path.read_text(encoding="utf-8")
    sep_pos = content.find(TABLE_SEP)
    if sep_pos != -1:
        insert_pos = sep_pos + len(TABLE_SEP)
        content = content[:insert_pos] + "\n" + row + content[insert_pos:]
    else:
        content = content.rstrip("\n") + "\n" + row + "\n"
    path.write_text(content, encoding="utf-8")


def _rewrite_notes(path: Path, notes: list[Note]) -> None:
    """Rewrite the file: preserve the preamble, regenerate the table.

    Every prose/blank line before the first table line is kept verbatim; the
    table itself is rebuilt from ``notes`` (in their normalized, ID'd form) so
    resolves and legacy-row normalization persist. This collapses any legacy
    six-column rows into the canonical seven-column schema.
    """
    preamble: list[str] = []
    seen_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("|"):
            seen_table = True
            break
        preamble.append(line)

    out_lines: list[str] = []
    out_lines.extend(preamble)
    if not seen_table and preamble and preamble[-1].strip():
        out_lines.append("")
    out_lines.append(TABLE_HEADER)
    out_lines.append(TABLE_SEP)
    for n in notes:
        out_lines.append(n.to_row())

    path.write_text("\n".join(out_lines).rstrip("\n") + "\n", encoding="utf-8")
