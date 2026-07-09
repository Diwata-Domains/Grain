# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Tests for `grain phase list` and `grain phase status` (both read-only)."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main


def _run(tmp_path: Path, *args: str):
    runner = CliRunner()
    return runner.invoke(main, ["--repo", str(tmp_path), *args])


def _seed(
    tmp_path: Path,
    backlog: str,
    current_phase_line: str = "Phase 2 — Test Phase",
    closed_markers: str = "",
) -> None:
    working = tmp_path / "docs" / "working"
    working.mkdir(parents=True)
    focus = f"# Current Focus\n\n## Current Phase\n{current_phase_line}\n"
    if closed_markers:
        focus += f"\n{closed_markers}\n"
    (working / "current_focus.md").write_text(focus, encoding="utf-8")
    (working / "current_task.md").write_text(
        "Task ID: none\nTask Path: none\nStatus: unset\n", encoding="utf-8"
    )
    (working / "backlog.md").write_text(backlog, encoding="utf-8")


# Canonical heading form: `## Phase N — Title`
_CANONICAL_BACKLOG = """# Backlog

## Phase 1 — Foundation
> **Status:** ACTIVE

### P1-T01 — First
- **Status:** done

### P1-T02 — Second
- **Status:** ready

## Phase 2 — Test Phase
> **Status:** in progress

### P2-T01 — Only
- **Status:** in_progress

## Backlog Maintenance Rules
Some trailing prose that must not be counted as a phase.
"""

# Numbered heading form used by older scaffolds: `## N. Phase N — Title`
_NUMBERED_BACKLOG = """# Backlog

## 1. Phase 1 — Foundation
> **Status:** shipped

### P1-T01 — First
- **Status:** done

## 2. Phase 2 — Test Phase
> **Status:** drafting

### P2-T01 — Only
- **Status:** ready
"""


# ---------------------------------------------------------------------------
# phase list — command must exist (regression: exited 2 "No such command")
# ---------------------------------------------------------------------------

def test_phase_list_command_exists(tmp_path: Path):
    _seed(tmp_path, _CANONICAL_BACKLOG)
    result = _run(tmp_path, "phase", "list")
    assert result.exit_code == 0, result.output
    assert "Phase 1" in result.output
    assert "Phase 2" in result.output


def test_phase_status_command_exists(tmp_path: Path):
    _seed(tmp_path, _CANONICAL_BACKLOG)
    result = _run(tmp_path, "phase", "status")
    assert result.exit_code == 0, result.output
    assert "Phase 2 — Test Phase" in result.output


# ---------------------------------------------------------------------------
# Rollups, markers, and BOTH heading forms
# ---------------------------------------------------------------------------

def test_phase_list_json_canonical_heading(tmp_path: Path):
    _seed(
        tmp_path,
        _CANONICAL_BACKLOG,
        closed_markers="Phase 1 closed: 2026-07-01 — 2 tasks done (grain-verified)",
    )
    result = _run(tmp_path, "--format", "json", "phase", "list")
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["active_phase"] == "2"
    by_num = {p["number"]: p for p in payload["phases"]}
    assert set(by_num) == {"1", "2"}

    p1 = by_num["1"]
    assert p1["title"] == "Foundation"
    assert p1["status"] == "ACTIVE"
    assert p1["closed"] is True
    assert p1["active"] is False
    assert p1["tasks_rollup"] == {
        "total": 2, "done": 1, "ready": 1, "in_progress": 0, "blocked": 0
    }

    p2 = by_num["2"]
    assert p2["active"] is True
    assert p2["closed"] is False
    assert p2["tasks_rollup"]["in_progress"] == 1
    assert p2["tasks_rollup"]["total"] == 1


def test_phase_list_json_numbered_heading(tmp_path: Path):
    # The exact bug being fixed: a regex demanding `## N. Phase N` (or one
    # rejecting it) must not drop phases or zero out task counts.
    _seed(tmp_path, _NUMBERED_BACKLOG)
    result = _run(tmp_path, "--format", "json", "phase", "list")
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    by_num = {p["number"]: p for p in payload["phases"]}
    assert set(by_num) == {"1", "2"}
    assert by_num["1"]["title"] == "Foundation"
    assert by_num["1"]["tasks_rollup"]["total"] == 1
    assert by_num["1"]["tasks_rollup"]["done"] == 1
    assert by_num["2"]["tasks_rollup"]["ready"] == 1


def test_phase_list_text_marks_active_and_closed(tmp_path: Path):
    _seed(
        tmp_path,
        _CANONICAL_BACKLOG,
        closed_markers="Phase 1 closed: 2026-07-01 — 2 tasks done (grain-verified)",
    )
    result = _run(tmp_path, "phase", "list")
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    p1_line = next(ln for ln in lines if "Phase 1" in ln)
    p2_line = next(ln for ln in lines if "Phase 2" in ln)
    assert "closed" in p1_line
    assert "*" in p2_line and "active" in p2_line


def test_phase_list_ignores_non_phase_sections(tmp_path: Path):
    _seed(tmp_path, _CANONICAL_BACKLOG)
    result = _run(tmp_path, "--format", "json", "phase", "list")
    payload = json.loads(result.output)
    assert len(payload["phases"]) == 2  # Backlog Maintenance Rules excluded


# ---------------------------------------------------------------------------
# phase status
# ---------------------------------------------------------------------------

def test_phase_status_json_active_detail(tmp_path: Path):
    _seed(tmp_path, _CANONICAL_BACKLOG)
    result = _run(tmp_path, "--format", "json", "phase", "status")
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["active_phase"] == "2"
    phase = payload["phase"]
    assert phase["number"] == "2"
    assert phase["title"] == "Test Phase"
    assert phase["active"] is True
    assert phase["tasks_rollup"]["in_progress"] == 1
    assert [t["task_ref"] for t in phase["tasks"]] == ["P2-T01"]


def test_phase_status_text_lists_tasks(tmp_path: Path):
    _seed(tmp_path, _CANONICAL_BACKLOG)
    result = _run(tmp_path, "phase", "status")
    assert result.exit_code == 0, result.output
    assert "P2-T01" in result.output
    assert "in_progress" in result.output


def test_phase_status_numbered_heading(tmp_path: Path):
    _seed(tmp_path, _NUMBERED_BACKLOG)
    result = _run(tmp_path, "--format", "json", "phase", "status")
    payload = json.loads(result.output)
    assert payload["phase"]["number"] == "2"
    assert payload["phase"]["tasks_rollup"]["ready"] == 1


def test_phase_status_project_complete(tmp_path: Path):
    _seed(tmp_path, _CANONICAL_BACKLOG, current_phase_line="Phase: complete")
    result = _run(tmp_path, "phase", "status")
    assert result.exit_code == 0, result.output
    assert "complete" in result.output.lower()

    jresult = _run(tmp_path, "--format", "json", "phase", "status")
    payload = json.loads(jresult.output)
    assert payload["active_phase"] == "complete"
    assert payload["phase"] is None


# ---------------------------------------------------------------------------
# Folded-in friction fix: phase close --dry-run must report dry_run: true
# ---------------------------------------------------------------------------

def test_phase_close_dry_run_reports_dry_run_flag(tmp_path: Path):
    # All-done phase so close is not blocked; the CLI must thread dry_run: true.
    _seed(
        tmp_path,
        """# Backlog

## 2. Phase 2 — Test Phase
> **Status:** done

### P2-T01 — Only
- **Status:** done
""",
    )
    result = _run(tmp_path, "--format", "json", "phase", "close", "--dry-run")
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["dry_run"] is True
