"""Tests for the notes service — add/list/show/resolve, ID allocation, filters."""

from __future__ import annotations

from pathlib import Path

from grain.domain.notes import TABLE_HEADER
from grain.services.notes_service import (
    add_note,
    list_notes,
    resolve_note,
    show_note,
)

_NOTES = "docs/working/tooling_notes.md"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ── add ─────────────────────────────────────────────────────────────────────

def test_add_note_creates_file_with_structured_row(tmp_path):
    result = add_note(tmp_path, "phase close requires metrics entry")
    assert result.ok
    assert result.note.id == 1
    assert result.note.status == "open"
    assert result.note.type == "friction"
    assert result.note.severity == "low"
    assert result.note.created_at  # timestamp assigned

    text = (tmp_path / _NOTES).read_text(encoding="utf-8")
    assert TABLE_HEADER in text
    assert "phase close requires metrics entry" in text
    assert "| 1 |" in text


def test_add_note_auto_increments_id(tmp_path):
    add_note(tmp_path, "first")
    add_note(tmp_path, "second")
    third = add_note(tmp_path, "third", note_type="bug")
    assert third.note.id == 3


def test_add_note_rejects_empty_body(tmp_path):
    result = add_note(tmp_path, "   ")
    assert not result.ok
    assert result.errors


def test_add_note_records_type_and_severity(tmp_path):
    result = add_note(tmp_path, "broken", note_type="bug", severity="high", command="grain x")
    assert result.note.type == "bug"
    assert result.note.severity == "high"
    assert result.note.command == "grain x"


# ── list ────────────────────────────────────────────────────────────────────

def test_list_empty_when_no_file(tmp_path):
    result = list_notes(tmp_path)
    assert result.ok
    assert result.notes == []


def test_list_defaults_to_open_only(tmp_path):
    add_note(tmp_path, "open one")
    second = add_note(tmp_path, "to resolve")
    resolve_note(tmp_path, second.note.id)

    result = list_notes(tmp_path)
    bodies = [n.body for n in result.notes]
    assert "open one" in bodies
    assert all(n.status == "open" for n in result.notes)


def test_list_filter_by_type(tmp_path):
    add_note(tmp_path, "a friction", note_type="friction")
    add_note(tmp_path, "a bug", note_type="bug")

    result = list_notes(tmp_path, type_filter="bug")
    assert len(result.notes) == 1
    assert result.notes[0].type == "bug"


def test_list_filter_by_status_all(tmp_path):
    add_note(tmp_path, "one")
    second = add_note(tmp_path, "two")
    resolve_note(tmp_path, second.note.id)

    result = list_notes(tmp_path, status_filter="all")
    assert len(result.notes) == 2


def test_list_filter_by_status_resolved(tmp_path):
    add_note(tmp_path, "one")
    second = add_note(tmp_path, "two")
    resolve_note(tmp_path, second.note.id)

    result = list_notes(tmp_path, status_filter="resolved")
    assert len(result.notes) == 1
    assert result.notes[0].status == "resolved"


# ── show ────────────────────────────────────────────────────────────────────

def test_show_returns_note(tmp_path):
    added = add_note(tmp_path, "find me", note_type="bug")
    result = show_note(tmp_path, added.note.id)
    assert result.ok
    assert result.note.body == "find me"


def test_show_missing_id(tmp_path):
    add_note(tmp_path, "only one")
    result = show_note(tmp_path, 999)
    assert not result.ok
    assert result.errors


def test_show_missing_file(tmp_path):
    result = show_note(tmp_path, 1)
    assert not result.ok


# ── resolve ─────────────────────────────────────────────────────────────────

def test_resolve_flips_status_and_records_note(tmp_path):
    added = add_note(tmp_path, "needs fixing")
    result = resolve_note(tmp_path, added.note.id, "done in TASK-0217")
    assert result.ok
    assert result.note.status == "resolved"
    assert "done in TASK-0217" in result.note.body

    text = (tmp_path / _NOTES).read_text(encoding="utf-8")
    assert "resolved" in text
    assert "done in TASK-0217" in text


def test_resolve_without_resolution_note(tmp_path):
    added = add_note(tmp_path, "needs fixing")
    result = resolve_note(tmp_path, added.note.id)
    assert result.ok
    assert result.note.status == "resolved"


def test_resolve_missing_id(tmp_path):
    add_note(tmp_path, "one")
    result = resolve_note(tmp_path, 999)
    assert not result.ok


def test_resolve_already_resolved(tmp_path):
    added = add_note(tmp_path, "one")
    resolve_note(tmp_path, added.note.id)
    result = resolve_note(tmp_path, added.note.id)
    assert not result.ok
    assert result.errors


# ── backward compatibility with legacy (un-IDed) rows ────────────────────────

_LEGACY = (
    "# Tooling Notes\n\n"
    "Lightweight inbox.\n\n"
    "| Date | Type | Command | Observation | Severity | Status |\n"
    "|------|------|---------|-------------|----------|--------|\n"
    "| 2026-06-11 | bug | `grain x` | legacy observation | high | open |\n"
)


def test_legacy_rows_are_parsed_and_get_synthesized_ids(tmp_path):
    _write(tmp_path / _NOTES, _LEGACY)
    result = list_notes(tmp_path, status_filter="all")
    assert len(result.notes) == 1
    assert result.notes[0].body == "legacy observation"
    assert result.notes[0].id >= 1


def test_add_after_legacy_rows_does_not_collide(tmp_path):
    _write(tmp_path / _NOTES, _LEGACY)
    added = add_note(tmp_path, "new note")
    # New ID must not reuse the synthesized legacy ID.
    legacy = list_notes(tmp_path, status_filter="all").notes
    ids = [n.id for n in legacy]
    assert len(ids) == len(set(ids))  # all unique
    assert added.note.id in ids


def test_resolve_legacy_row_normalizes_table(tmp_path):
    _write(tmp_path / _NOTES, _LEGACY)
    notes = list_notes(tmp_path, status_filter="all").notes
    legacy_id = notes[0].id
    result = resolve_note(tmp_path, legacy_id, "handled")
    assert result.ok

    text = (tmp_path / _NOTES).read_text(encoding="utf-8")
    assert TABLE_HEADER in text  # collapsed into canonical schema
    assert "resolved" in text
    assert "legacy observation" in text  # data preserved


# ── F3: legacy-row IDs stay stable across adds ───────────────────────────────

_EXPLICIT_PLUS_LEGACY = (
    "# Tooling Notes\n\n"
    "| ID | Date | Type | Command | Observation | Severity | Status |\n"
    "|----|------|------|---------|-------------|----------|--------|\n"
    "| 1 | 2026-06-01 | bug | grain | explicit one | low | open |\n"
    "| 2026-06-02 | bug | grain | legacy row | low | open |\n"
)


def test_legacy_row_id_is_stable_across_adds(tmp_path):
    """A legacy row's synthesized ID must not float when a new note is added.

    Before the fix the legacy row was id 2, then floated to id 4 after an add
    (because add appended id 3 and the next read recomputed max(explicit)+1),
    so ``show_note(2)`` started failing.
    """
    _write(tmp_path / _NOTES, _EXPLICIT_PLUS_LEGACY)
    before = list_notes(tmp_path, status_filter="all").notes
    legacy = next(n for n in before if n.body == "legacy row")
    legacy_id = legacy.id

    add_note(tmp_path, "brand new note")

    # The very same legacy row is still addressable under the same ID.
    shown = show_note(tmp_path, legacy_id)
    assert shown.ok, shown.errors
    assert shown.note.body == "legacy row"


# ── F4: a pipe in the body survives round-trip ───────────────────────────────

def test_pipe_in_body_round_trips_without_corruption(tmp_path):
    """A literal ``|`` in the body must not leak into severity/status cells."""
    added = add_note(
        tmp_path, "init | flag broke", note_type="bug", severity="high",
    )
    assert added.ok
    assert added.note.severity == "high"
    assert added.note.status == "open"

    back = show_note(tmp_path, added.note.id)
    assert back.ok, back.errors
    assert back.note.body == "init | flag broke"
    assert back.note.severity == "high"
    assert back.note.status == "open"  # not clobbered by the pipe

    # And the note is still visible in the default (open-only) list.
    listed = [n.body for n in list_notes(tmp_path).notes]
    assert "init | flag broke" in listed


def test_pipe_in_command_round_trips(tmp_path):
    added = add_note(
        tmp_path, "noted", note_type="bug", command="grep a | wc -l",
    )
    back = show_note(tmp_path, added.note.id)
    assert back.ok, back.errors
    assert back.note.command == "grep a | wc -l"
    assert back.note.status == "open"


# ── F5: resolve preserves original row order ─────────────────────────────────

def test_resolve_preserves_row_order(tmp_path):
    """A resolve must not relocate legacy rows below explicit-ID rows."""
    _write(
        tmp_path / _NOTES,
        "# Tooling Notes\n\n"
        "| ID | Date | Type | Command | Observation | Severity | Status |\n"
        "|----|------|------|---------|-------------|----------|--------|\n"
        "| 2026-06-01 | bug | grain | legacy first | low | open |\n"
        "| 5 | 2026-06-02 | bug | grain | explicit five | low | open |\n"
        "| 2026-06-03 | bug | grain | legacy third | low | open |\n",
    )
    before = [n.body for n in list_notes(tmp_path, status_filter="all").notes]
    assert before == ["legacy first", "explicit five", "legacy third"]

    target = next(
        n.id for n in list_notes(tmp_path, status_filter="all").notes
        if n.body == "explicit five"
    )
    resolve_note(tmp_path, target)

    after = [n.body for n in list_notes(tmp_path, status_filter="all").notes]
    assert after == ["legacy first", "explicit five", "legacy third"]
