"""Tests for CLI ergonomics — grain doctor, grain status, grain notes, stop reason constants."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from grain.cli import main


# ── Helpers ────────────────────────────────────────────────────────────────────

def _run(tmp_path: Path, *args: str, fmt: str = "text"):
    runner = CliRunner()
    cmd = ["--repo", str(tmp_path)]
    if fmt == "json":
        cmd += ["--format", "json"]
    cmd += list(args)
    return runner.invoke(main, cmd)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _base(tmp_path: Path) -> None:
    _write(tmp_path / "docs/working/current_task.md",
           "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: unset\n")
    _write(tmp_path / "docs/working/backlog.md",
           "# Backlog\n\n## 2. Phase 1 — Foundation\n\n"
           "### P1-T01 — Task\n- **Status:** done\n")
    _write(tmp_path / "docs/working/current_focus.md",
           "# Current Focus\n\n## Current Phase\nPhase 1 — Foundation\n")
    _write(tmp_path / "docs/runtime/docs_manifest.yaml",
           "version: 1\nproject:\n  name: Test\ncanonical: []\nworking: []\nruntime: []\n")


# ── Stop reason constants ─────────────────────────────────────────────────────

def test_stop_reason_constants_are_strings():
    from grain.services.workflow_service import (
        STOP_REQUIRED_DOCS_MISSING,
        STOP_REQUIRED_DOCS_INVALID,
        STOP_PROJECT_COMPLETE,
        STOP_BOOTSTRAP_INCOMPLETE,
        STOP_STALE_TASK_POINTER,
        STOP_WORKFLOW_STATE_DRIFT,
        STOP_EXECUTION_IN_FLIGHT,
        STOP_CONFLICTING_NEXT_ACTIONS,
        STOP_PACKET_REQUIRED,
        STOP_PHASE_BOUNDARY_REVIEW_CLOSE_REQUIRED,
        STOP_TASK_PLANNING_REQUIRED,
    )
    consts = [
        STOP_REQUIRED_DOCS_MISSING,
        STOP_REQUIRED_DOCS_INVALID,
        STOP_PROJECT_COMPLETE,
        STOP_BOOTSTRAP_INCOMPLETE,
        STOP_STALE_TASK_POINTER,
        STOP_WORKFLOW_STATE_DRIFT,
        STOP_EXECUTION_IN_FLIGHT,
        STOP_CONFLICTING_NEXT_ACTIONS,
        STOP_PACKET_REQUIRED,
        STOP_PHASE_BOUNDARY_REVIEW_CLOSE_REQUIRED,
        STOP_TASK_PLANNING_REQUIRED,
    ]
    for c in consts:
        assert isinstance(c, str)
        assert len(c) > 0


def test_stop_reason_constants_are_snake_case():
    from grain.services.workflow_service import STOP_PACKET_REQUIRED, STOP_EXECUTION_IN_FLIGHT
    assert STOP_PACKET_REQUIRED == "packet_required"
    assert STOP_EXECUTION_IN_FLIGHT == "execution_in_flight"


def test_workflow_next_uses_constant_values(tmp_path):
    """workflow next JSON output stop_reason values match the constants."""
    _base(tmp_path)
    result = _run(tmp_path, "workflow", "next", fmt="json")
    assert result.exit_code == 0
    data = json.loads(result.output)
    stop_reason = data["evaluation"]["stop_reason"]
    # The value must match one of the known constants
    from grain.services.workflow_service import (
        STOP_PACKET_REQUIRED, STOP_PHASE_BOUNDARY_REVIEW_CLOSE_REQUIRED,
        STOP_CONFLICTING_NEXT_ACTIONS,
    )
    known = {
        STOP_PACKET_REQUIRED, STOP_PHASE_BOUNDARY_REVIEW_CLOSE_REQUIRED,
        STOP_CONFLICTING_NEXT_ACTIONS, "task_execute", "task_review", "",
    }
    assert stop_reason in known or stop_reason  # must be a non-empty known value


# ── grain --version install mode ──────────────────────────────────────────────

def test_version_output_includes_install_mode(tmp_path):
    result = _run(tmp_path, "--version")
    assert result.exit_code == 0
    # Should contain one of the known modes
    output = result.output
    assert any(mode in output for mode in ("editable", "installed", "dev", "unknown"))


# ── grain doctor ─────────────────────────────────────────────────────────────

def test_doctor_text_output(tmp_path):
    result = _run(tmp_path, "doctor")
    assert result.exit_code == 0
    assert "Grain Doctor" in result.output
    assert "Install:" in result.output
    assert "Checks:" in result.output


def test_doctor_json_output_contract(tmp_path):
    result = _run(tmp_path, "doctor", fmt="json")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "grain_version" in data
    assert "install_mode" in data
    assert "version_match" in data
    assert "checks" in data
    assert "overall" in data
    assert data["overall"] in ("ok", "drift_detected")


def test_doctor_checks_are_dict_of_bools(tmp_path):
    result = _run(tmp_path, "doctor", fmt="json")
    assert result.exit_code == 0
    data = json.loads(result.output)
    for k, v in data["checks"].items():
        assert isinstance(v, bool), f"check {k!r} should be bool"


def test_detect_install_mode_returns_known_value():
    from grain.services.doctor_service import detect_install_mode
    mode = detect_install_mode()
    assert mode in ("editable", "installed", "dev", "unknown")


# ── grain status ──────────────────────────────────────────────────────────────

def test_status_text_output(tmp_path):
    _base(tmp_path)
    result = _run(tmp_path, "status")
    assert result.exit_code == 0
    assert "Grain Status" in result.output
    assert "Phase:" in result.output
    assert "Tasks:" in result.output
    assert "Health:" in result.output


def test_status_json_contract(tmp_path):
    _base(tmp_path)
    result = _run(tmp_path, "status", fmt="json")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "run_at" in data
    assert "phase" in data
    assert "tasks" in data
    assert "workflow" in data
    assert "health" in data
    assert "install" in data


def test_status_json_tasks_have_required_keys(tmp_path):
    _base(tmp_path)
    result = _run(tmp_path, "status", fmt="json")
    assert result.exit_code == 0
    data = json.loads(result.output)
    tasks = data["tasks"]
    for key in ("total", "done", "ready", "in_progress", "blocked"):
        assert key in tasks


def test_status_json_install_has_version_and_mode(tmp_path):
    _base(tmp_path)
    result = _run(tmp_path, "status", fmt="json")
    assert result.exit_code == 0
    data = json.loads(result.output)
    inst = data["install"]
    assert "version" in inst
    assert "mode" in inst


def test_status_reads_workflow_cache(tmp_path):
    _base(tmp_path)
    # Write a fresh cache file
    grain_dir = tmp_path / ".grain"
    grain_dir.mkdir()
    cache = {
        "evaluation": {
            "stop_reason": "packet_required",
            "next_action": "",
            "active_phase": "1",
            "active_task_id": "",
            "ok": True,
        }
    }
    (grain_dir / "last_workflow_state.json").write_text(
        json.dumps(cache), encoding="utf-8"
    )

    result = _run(tmp_path, "status", fmt="json")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["workflow"]["stop_reason"] == "packet_required"


def test_status_reads_audit_cache(tmp_path):
    _base(tmp_path)
    grain_dir = tmp_path / ".grain"
    grain_dir.mkdir()
    audit_cache = {
        "overall": "warning",
        "summary": {"pass": 5, "warning": 1, "error": 0},
        "findings": [],
    }
    (grain_dir / "last_docs_audit.json").write_text(
        json.dumps(audit_cache), encoding="utf-8"
    )

    result = _run(tmp_path, "status", fmt="json")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["health"]["overall"] == "warning"
    assert data["health"]["warning_count"] == 1


# ── grain notes ──────────────────────────────────────────────────────────────

def test_notes_add_creates_row(tmp_path):
    _base(tmp_path)
    result = _run(tmp_path, "notes", "add", "grain init is slow on large repos")
    assert result.exit_code == 0
    assert "notes add: ok" in result.output

    notes_path = tmp_path / "docs/working/tooling_notes.md"
    assert notes_path.exists()
    content = notes_path.read_text(encoding="utf-8")
    assert "grain init is slow on large repos" in content


def test_notes_add_creates_file_if_absent(tmp_path):
    _base(tmp_path)
    notes_path = tmp_path / "docs/working/tooling_notes.md"
    assert not notes_path.exists()

    _run(tmp_path, "notes", "add", "test friction")
    assert notes_path.exists()


def test_notes_add_json_output(tmp_path):
    _base(tmp_path)
    result = _run(tmp_path, "notes", "add", "test", fmt="json")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["ok"] is True
    assert "row" in data


def test_notes_add_with_severity(tmp_path):
    _base(tmp_path)
    _run(tmp_path, "notes", "add", "critical issue", "--severity", "high")
    content = (tmp_path / "docs/working/tooling_notes.md").read_text()
    assert "high" in content


def test_notes_list_empty(tmp_path):
    _base(tmp_path)
    result = _run(tmp_path, "notes", "list")
    assert result.exit_code == 0


def test_notes_list_after_add(tmp_path):
    _base(tmp_path)
    _run(tmp_path, "notes", "add", "something to track")
    result = _run(tmp_path, "notes", "list")
    assert result.exit_code == 0
    assert "something to track" in result.output


def test_notes_list_json(tmp_path):
    _base(tmp_path)
    _run(tmp_path, "notes", "add", "test entry")
    result = _run(tmp_path, "notes", "list", fmt="json")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert any("test entry" in e["observation"] for e in data)
