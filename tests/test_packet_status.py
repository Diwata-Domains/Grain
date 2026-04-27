from pathlib import Path

import pytest

from grain.domain.packets import (
    PacketRecord,
    parse_task_metadata,
    read_packet_record,
    write_packet_status,
)
from grain.validators.packet_validator import (
    validate_status_transition,
    validate_status_value,
)

TASK_MD_CONTENT = """\
# Task: Test Task

## Metadata
- **ID:** TASK-0042
- **Status:** draft
- **Phase:** Phase 3 — Task Packet System
- **Backlog:** P3-T07
- **Dependencies:** none

## Objective
Does something.
"""

TASK_MD_WITH_ADAPTERS = """\
# Task: Adapter Task

## Metadata
- **ID:** TASK-0043
- **Status:** draft
- **Phase:** Phase 6 — Adapter System Foundation (V2)
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** frontend_adapter, docs_adapter

## Objective
Does adapter work.
"""


# --- parse_task_metadata ---


def test_parse_metadata_extracts_id_status_phase(tmp_path):
    task_md = tmp_path / "task.md"
    task_md.write_text(TASK_MD_CONTENT)
    metadata = parse_task_metadata(task_md)
    assert metadata["id"] == "TASK-0042"
    assert metadata["status"] == "draft"
    assert metadata["phase"] == "Phase 3 — Task Packet System"


def test_parse_metadata_returns_empty_when_no_section(tmp_path):
    task_md = tmp_path / "task.md"
    task_md.write_text("# Task: No Metadata\n\nJust text.\n")
    assert parse_task_metadata(task_md) == {}


def test_parse_metadata_extracts_adapter_fields_when_present(tmp_path):
    task_md = tmp_path / "task.md"
    task_md.write_text(TASK_MD_WITH_ADAPTERS)
    metadata = parse_task_metadata(task_md)
    assert metadata["primary_adapter"] == "code_adapter"
    assert metadata["secondary_adapters"] == "frontend_adapter, docs_adapter"


def test_parse_metadata_stops_at_next_section(tmp_path):
    content = """\
## Metadata
- **ID:** TASK-0001
- **Status:** ready

## Objective
Should not appear.
- **ID:** TASK-9999
"""
    task_md = tmp_path / "task.md"
    task_md.write_text(content)
    metadata = parse_task_metadata(task_md)
    assert metadata["id"] == "TASK-0001"
    assert "TASK-9999" not in metadata.values()


def test_parse_metadata_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        parse_task_metadata(tmp_path / "nonexistent.md")


# --- read_packet_record ---


def test_read_packet_record_returns_correct_record(tmp_path):
    (tmp_path / "task.md").write_text(TASK_MD_CONTENT)
    record = read_packet_record(tmp_path)
    assert isinstance(record, PacketRecord)
    assert record.id == "TASK-0042"
    assert record.status == "draft"
    assert record.phase == "Phase 3 — Task Packet System"
    assert record.path == tmp_path


def test_read_packet_record_missing_task_md_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_packet_record(tmp_path)


# --- write_packet_status ---


def test_write_packet_status_updates_status_line(tmp_path):
    task_md = tmp_path / "task.md"
    task_md.write_text(TASK_MD_CONTENT)
    write_packet_status(tmp_path, "ready")
    updated = parse_task_metadata(task_md)
    assert updated["status"] == "ready"


def test_write_packet_status_does_not_change_other_fields(tmp_path):
    task_md = tmp_path / "task.md"
    task_md.write_text(TASK_MD_CONTENT)
    write_packet_status(tmp_path, "in_progress")
    updated = parse_task_metadata(task_md)
    assert updated["id"] == "TASK-0042"
    assert updated["phase"] == "Phase 3 — Task Packet System"
    assert updated["status"] == "in_progress"


def test_write_packet_status_preserves_non_metadata_content(tmp_path):
    task_md = tmp_path / "task.md"
    task_md.write_text(TASK_MD_CONTENT)
    write_packet_status(tmp_path, "review")
    text = task_md.read_text()
    assert "# Task: Test Task" in text
    assert "## Objective" in text
    assert "Does something." in text


# --- validate_status_value ---


def test_validate_status_value_valid(tmp_path):
    for status in ("draft", "ready", "in_progress", "blocked", "review", "done"):
        assert validate_status_value(status) == []


def test_validate_status_value_invalid():
    errors = validate_status_value("DRAFT")
    assert errors
    assert "DRAFT" in errors[0]


def test_validate_status_value_unknown():
    errors = validate_status_value("pending")
    assert errors


# --- validate_status_transition ---


def test_validate_transition_allowed():
    assert validate_status_transition("draft", "ready") == []
    assert validate_status_transition("ready", "in_progress") == []
    assert validate_status_transition("in_progress", "review") == []
    assert validate_status_transition("in_progress", "blocked") == []
    assert validate_status_transition("blocked", "ready") == []
    assert validate_status_transition("review", "done") == []
    assert validate_status_transition("review", "in_progress") == []
    assert validate_status_transition("blocked", "draft") == []


def test_validate_transition_disallowed():
    errors = validate_status_transition("draft", "done")
    assert errors
    assert "draft" in errors[0]
    assert "done" in errors[0]


def test_validate_transition_done_is_terminal():
    errors = validate_status_transition("done", "ready")
    assert errors


def test_validate_transition_invalid_from_status():
    errors = validate_status_transition("unknown", "ready")
    assert errors


def test_validate_transition_invalid_to_status():
    errors = validate_status_transition("draft", "READY")
    assert errors
