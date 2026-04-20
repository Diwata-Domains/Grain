"""Tests for `grain phase close` command and bypass-prevention evaluator check."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main


def _run(tmp_path: Path, *args: str):
    runner = CliRunner()
    return runner.invoke(main, ["--repo", str(tmp_path), *args])


# ---------------------------------------------------------------------------
# Helpers to build minimal valid repo state
# ---------------------------------------------------------------------------

def _seed_repo(
    tmp_path: Path,
    phase: str = "15",
    task_statuses: dict[str, str] | None = None,
    active_task_id: str = "none",
    phase_closed_marker: str | None = None,
) -> None:
    """Seed the minimum docs needed for phase close tests."""
    if task_statuses is None:
        task_statuses = {"P15-T01": "done", "P15-T02": "done"}

    (tmp_path / "docs" / "working").mkdir(parents=True)

    # current_focus.md
    focus_lines = [f"Phase {phase} — Test Phase\n"]
    if phase_closed_marker:
        focus_lines.append(f"\n{phase_closed_marker}\n")
    (tmp_path / "docs" / "working" / "current_focus.md").write_text(
        "".join(focus_lines), encoding="utf-8"
    )

    # current_task.md
    (tmp_path / "docs" / "working" / "current_task.md").write_text(
        f"Task ID: {active_task_id}\nTask Path: none\nStatus: unset\n",
        encoding="utf-8",
    )

    # backlog.md — one phase section with the given tasks
    task_lines = [f"## 1. Phase {phase} — Test Phase\n\n"]
    for task_ref, status in task_statuses.items():
        task_lines.append(f"### {task_ref} — Task description\n")
        task_lines.append(f"- **Status:** {status}\n\n")
    (tmp_path / "docs" / "working" / "backlog.md").write_text(
        "".join(task_lines), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_phase_close_ok_when_all_tasks_done(tmp_path: Path):
    _seed_repo(tmp_path, phase="15", task_statuses={"P15-T01": "done", "P15-T02": "done"})
    result = _run(tmp_path, "phase", "close")
    assert result.exit_code == 0, result.output
    assert "phase close: ok" in result.output
    assert "closed_phase    15" in result.output
    assert "tasks_done      2" in result.output
    assert "marker_written" in result.output

    # Marker is written to current_focus.md
    focus = (tmp_path / "docs" / "working" / "current_focus.md").read_text(encoding="utf-8")
    assert "Phase 15 closed:" in focus
    assert "grain-verified" in focus


def test_phase_close_dry_run_writes_nothing(tmp_path: Path):
    _seed_repo(tmp_path)
    result = _run(tmp_path, "phase", "close", "--dry-run")
    assert result.exit_code == 0, result.output
    assert "dry_run" in result.output
    assert "(no changes written)" in result.output

    focus = (tmp_path / "docs" / "working" / "current_focus.md").read_text(encoding="utf-8")
    assert "grain-verified" not in focus


def test_phase_close_json_output(tmp_path: Path):
    _seed_repo(tmp_path)
    result = _run(tmp_path, "--format", "json", "phase", "close")
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["ok"] is True
    assert payload["closed_phase"] == "15"
    assert payload["tasks_done"] == 2
    assert payload["dry_run"] is False
    assert payload["errors"] == []


def test_phase_close_json_dry_run(tmp_path: Path):
    _seed_repo(tmp_path)
    result = _run(tmp_path, "--format", "json", "phase", "close", "--dry-run")
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["ok"] is True
    assert payload["dry_run"] is True
    assert payload["marker_written"] == ""


# ---------------------------------------------------------------------------
# Blocked — open tasks
# ---------------------------------------------------------------------------

def test_phase_close_blocked_when_open_tasks(tmp_path: Path):
    _seed_repo(
        tmp_path,
        task_statuses={"P15-T01": "done", "P15-T02": "ready", "P15-T03": "in_progress"},
    )
    result = _run(tmp_path, "phase", "close")
    assert result.exit_code != 0
    assert "blocked" in result.output
    # Check that marker was NOT written
    focus = (tmp_path / "docs" / "working" / "current_focus.md").read_text(encoding="utf-8")
    assert "grain-verified" not in focus


def test_phase_close_blocked_when_open_tasks_json(tmp_path: Path):
    _seed_repo(tmp_path, task_statuses={"P15-T01": "done", "P15-T02": "ready"})
    result = _run(tmp_path, "--format", "json", "phase", "close")
    assert result.exit_code != 0
    payload = json.loads(result.output)
    assert payload["ok"] is False
    assert payload["errors"]


# ---------------------------------------------------------------------------
# Blocked — active task in flight
# ---------------------------------------------------------------------------

def test_phase_close_blocked_when_active_task(tmp_path: Path):
    _seed_repo(tmp_path, active_task_id="P15-T01")
    result = _run(tmp_path, "phase", "close")
    assert result.exit_code != 0
    assert "P15-T01" in result.output


# ---------------------------------------------------------------------------
# Blocked — already closed
# ---------------------------------------------------------------------------

def test_phase_close_blocked_when_already_closed(tmp_path: Path):
    _seed_repo(
        tmp_path,
        phase_closed_marker="Phase 15 closed: 2026-04-16 — 2 tasks done (grain-verified)",
    )
    result = _run(tmp_path, "phase", "close")
    assert result.exit_code != 0
    assert "already sealed" in result.output


# ---------------------------------------------------------------------------
# Blocked — no tasks in backlog for phase
# ---------------------------------------------------------------------------

def test_phase_close_blocked_when_no_tasks(tmp_path: Path):
    _seed_repo(tmp_path, task_statuses={})
    result = _run(tmp_path, "phase", "close")
    assert result.exit_code != 0
    assert "no tasks found" in result.output


# ---------------------------------------------------------------------------
# Blocked — workflow_metrics.md missing Phase N entry
# ---------------------------------------------------------------------------

def _seed_metrics(tmp_path: Path, phase: str | None = None) -> None:
    """Write a workflow_metrics.md; include a Phase entry if phase is given."""
    lines = ["# Workflow Metrics\n\n"]
    if phase:
        lines.append(f"### Phase {phase}\n\n* Tasks completed: 2\n")
    (tmp_path / "docs" / "working" / "workflow_metrics.md").write_text(
        "".join(lines), encoding="utf-8"
    )


def test_phase_close_blocked_when_metrics_missing_entry(tmp_path: Path):
    _seed_repo(tmp_path, phase="15")
    _seed_metrics(tmp_path)  # file exists but no Phase 15 entry
    result = _run(tmp_path, "phase", "close")
    assert result.exit_code != 0
    assert "workflow_metrics.md" in result.output
    assert "Phase 15" in result.output


def test_phase_close_ok_when_metrics_has_entry(tmp_path: Path):
    _seed_repo(tmp_path, phase="15")
    _seed_metrics(tmp_path, phase="15")
    result = _run(tmp_path, "phase", "close")
    assert result.exit_code == 0, result.output
    assert "phase close: ok" in result.output


def test_phase_close_ok_when_no_metrics_file(tmp_path: Path):
    """No workflow_metrics.md at all — gate does not fire."""
    _seed_repo(tmp_path, phase="15")
    result = _run(tmp_path, "phase", "close")
    assert result.exit_code == 0, result.output


def test_phase_close_dry_run_blocked_when_metrics_missing(tmp_path: Path):
    """Dry-run validates the same gates — blocked if metrics entry absent."""
    _seed_repo(tmp_path, phase="15")
    _seed_metrics(tmp_path)
    result = _run(tmp_path, "phase", "close", "--dry-run")
    assert result.exit_code != 0
    assert "workflow_metrics.md" in result.output


def test_phase_close_metrics_blocked_json(tmp_path: Path):
    _seed_repo(tmp_path, phase="15")
    _seed_metrics(tmp_path)
    result = _run(tmp_path, "--format", "json", "phase", "close")
    assert result.exit_code != 0
    payload = json.loads(result.output)
    assert payload["ok"] is False
    assert any("workflow_metrics.md" in e for e in payload["errors"])


# ---------------------------------------------------------------------------
# Bypass protection: workflow evaluator blocks on previous_phase_not_closed
# ---------------------------------------------------------------------------

def _seed_evaluator_repo(tmp_path: Path, current_phase: str, prev_closed: bool) -> None:
    """Seed a repo in phase N with/without a closed marker for phase N-1."""
    (tmp_path / "docs" / "working").mkdir(parents=True)

    focus_text = f"Phase {current_phase} — Next Phase\n"
    if prev_closed:
        prev = str(int(current_phase) - 1)
        focus_text += f"\nPhase {prev} closed: 2026-04-16 — 2 tasks done (grain-verified)\n"
    (tmp_path / "docs" / "working" / "current_focus.md").write_text(focus_text, encoding="utf-8")

    (tmp_path / "docs" / "working" / "current_task.md").write_text(
        "Task ID: none\nTask Path: none\nStatus: unset\n", encoding="utf-8"
    )
    (tmp_path / "docs" / "working" / "backlog.md").write_text(
        f"## 1. Phase {current_phase} — Next Phase\n\n"
        f"### P{current_phase}-T01 — Some task\n"
        f"- **Status:** ready\n\n",
        encoding="utf-8",
    )


def test_workflow_evaluator_allows_phase_16_when_15_closed(tmp_path: Path):
    _seed_evaluator_repo(tmp_path, current_phase="16", prev_closed=True)
    result = _run(tmp_path, "workflow", "next")
    assert result.exit_code == 0, result.output
    assert "previous_phase_not_closed" not in result.output


def test_workflow_evaluator_blocks_phase_16_when_15_not_closed(tmp_path: Path):
    _seed_evaluator_repo(tmp_path, current_phase="16", prev_closed=False)
    result = _run(tmp_path, "--format", "json", "workflow", "next")
    payload = json.loads(result.output)
    assert payload["evaluation"]["stop_reason"] == "previous_phase_not_closed"
    assert "grain phase close" in payload["evaluation"]["blocking_reasons"][0]


def test_workflow_evaluator_does_not_block_phase_15(tmp_path: Path):
    """Phase 15 is the first enforced phase — no check on Phase 14 (grandfathered)."""
    _seed_evaluator_repo(tmp_path, current_phase="15", prev_closed=False)
    result = _run(tmp_path, "--format", "json", "workflow", "next")
    payload = json.loads(result.output)
    assert payload["evaluation"]["stop_reason"] != "previous_phase_not_closed"


def test_workflow_evaluator_does_not_block_low_phase(tmp_path: Path):
    """Phases well below the enforcement threshold are never blocked."""
    _seed_evaluator_repo(tmp_path, current_phase="8", prev_closed=False)
    result = _run(tmp_path, "--format", "json", "workflow", "next")
    payload = json.loads(result.output)
    assert payload["evaluation"]["stop_reason"] != "previous_phase_not_closed"
