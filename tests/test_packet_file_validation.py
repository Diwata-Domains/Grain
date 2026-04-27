from pathlib import Path

import pytest

from grain.validators.packet_validator import (
    validate_packet,
    validate_packet_files,
    validate_packet_metadata,
)

_REQUIRED_FILES = ("task.md", "context.md", "plan.md", "deliverable_spec.md")

_VALID_TASK_MD = """\
# Task: Test Task

## Metadata
- **ID:** TASK-0042
- **Status:** draft
- **Phase:** Phase 3 — Task Packet System
- **Dependencies:** none

## Objective
Does something.
"""


def _make_valid_packet(tmp_path: Path) -> Path:
    """Write all required files into tmp_path and return it as the packet dir."""
    tmp_path.write_text  # ensure it's a dir (it is by pytest)
    (tmp_path / "task.md").write_text(_VALID_TASK_MD)
    for name in ("context.md", "plan.md", "deliverable_spec.md"):
        (tmp_path / name).write_text(f"# {name}\n")
    return tmp_path


# --- validate_packet_files ---


def test_validate_packet_files_passes_when_all_present(tmp_path):
    _make_valid_packet(tmp_path)
    assert validate_packet_files(tmp_path) == []


def test_validate_packet_files_reports_missing_task_md(tmp_path):
    _make_valid_packet(tmp_path)
    (tmp_path / "task.md").unlink()
    errors = validate_packet_files(tmp_path)
    assert any("task.md" in e for e in errors)


def test_validate_packet_files_reports_all_missing(tmp_path):
    errors = validate_packet_files(tmp_path)
    assert len(errors) == len(_REQUIRED_FILES)


def test_validate_packet_files_reports_one_missing(tmp_path):
    _make_valid_packet(tmp_path)
    (tmp_path / "plan.md").unlink()
    errors = validate_packet_files(tmp_path)
    assert len(errors) == 1
    assert "plan.md" in errors[0]


# --- validate_packet_metadata ---


def test_validate_packet_metadata_passes_valid(tmp_path):
    _make_valid_packet(tmp_path)
    assert validate_packet_metadata(tmp_path) == []


def test_validate_packet_metadata_missing_task_md(tmp_path):
    errors = validate_packet_metadata(tmp_path)
    assert any("task.md not found" in e for e in errors)


def test_validate_packet_metadata_missing_id(tmp_path):
    (tmp_path / "task.md").write_text(
        "## Metadata\n- **Status:** draft\n- **Phase:** Phase 3\n"
    )
    errors = validate_packet_metadata(tmp_path)
    assert any("id" in e for e in errors)


def test_validate_packet_metadata_missing_status(tmp_path):
    (tmp_path / "task.md").write_text(
        "## Metadata\n- **ID:** TASK-0001\n- **Phase:** Phase 3\n"
    )
    errors = validate_packet_metadata(tmp_path)
    assert any("status" in e for e in errors)


def test_validate_packet_metadata_invalid_status(tmp_path):
    (tmp_path / "task.md").write_text(
        "## Metadata\n- **ID:** TASK-0001\n- **Status:** INVALID\n- **Phase:** Phase 3\n"
    )
    errors = validate_packet_metadata(tmp_path)
    assert any("INVALID" in e for e in errors)


def test_validate_packet_metadata_missing_phase(tmp_path):
    (tmp_path / "task.md").write_text(
        "## Metadata\n- **ID:** TASK-0001\n- **Status:** draft\n"
    )
    errors = validate_packet_metadata(tmp_path)
    assert any("phase" in e for e in errors)


# --- validate_packet (composite) ---


def test_validate_packet_passes_valid(tmp_path):
    _make_valid_packet(tmp_path)
    assert validate_packet(tmp_path) == []


def test_validate_packet_catches_missing_file_and_bad_metadata(tmp_path):
    # Only task.md present, but with bad status
    (tmp_path / "task.md").write_text(
        "## Metadata\n- **ID:** TASK-0001\n- **Status:** NOPE\n- **Phase:** Phase 3\n"
    )
    errors = validate_packet(tmp_path)
    # Missing context.md, plan.md, deliverable_spec.md + invalid status
    assert len(errors) >= 4


def test_validate_packet_empty_dir_has_errors(tmp_path):
    errors = validate_packet(tmp_path)
    assert errors
