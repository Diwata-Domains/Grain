"""Tests for `grain workflow reconcile` command."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main


def _run(tmp_path: Path, *args: str):
    runner = CliRunner()
    return runner.invoke(main, ["--repo", str(tmp_path), *args])


def _run_json(tmp_path: Path, *args: str):
    runner = CliRunner()
    return runner.invoke(main, ["--repo", str(tmp_path), "--format", "json", *args])


# ---------------------------------------------------------------------------
# Repo builder helpers
# ---------------------------------------------------------------------------

def _seed_working_docs(
    tmp_path: Path,
    phase: str = "15",
    backlog_tasks: dict[str, str] | None = None,
    current_task_id: str = "none",
    current_task_path: str = "none",
    current_task_status: str = "idle",
) -> None:
    (tmp_path / "docs" / "working").mkdir(parents=True)

    (tmp_path / "docs" / "working" / "current_focus.md").write_text(
        f"Phase {phase} — Test Phase\n", encoding="utf-8"
    )

    (tmp_path / "docs" / "working" / "current_task.md").write_text(
        f"# Current Task\n\nTask ID: {current_task_id}\n"
        f"Task Path: {current_task_path}\nStatus: {current_task_status}\n",
        encoding="utf-8",
    )

    tasks_section = f"## 1. Phase {phase} — Test Phase\n\n"
    for ref, status in (backlog_tasks or {}).items():
        tasks_section += f"### {ref} — Task description\n- **Status:** {status}\n\n"
    (tmp_path / "docs" / "working" / "backlog.md").write_text(
        tasks_section, encoding="utf-8"
    )


def _seed_packet(
    tmp_path: Path,
    task_ref: str,
    task_id: str,
    status: str,
) -> Path:
    """Create a minimal packet directory with task.md."""
    packet_dir = tmp_path / "tasks" / f"{task_ref}-{task_id}"
    packet_dir.mkdir(parents=True)
    task_md = (
        f"# Task: Test\n\n"
        f"## Metadata\n"
        f"- **ID:** {task_id}\n"
        f"- **Status:** {status}\n"
    )
    (packet_dir / "task.md").write_text(task_md, encoding="utf-8")
    return packet_dir


# ---------------------------------------------------------------------------
# Clean state — no issues
# ---------------------------------------------------------------------------

def test_reconcile_clean_state_ok(tmp_path: Path):
    _seed_working_docs(
        tmp_path,
        backlog_tasks={"P15-T01": "done", "P15-T02": "ready"},
    )
    _seed_packet(tmp_path, "P15-T01", "TASK-0103", "done")
    result = _run(tmp_path, "workflow", "reconcile")
    assert result.exit_code == 0, result.output
    assert "workflow reconcile: ok" in result.output
    assert "issues            0" in result.output


def test_reconcile_no_packets_clean(tmp_path: Path):
    _seed_working_docs(
        tmp_path,
        backlog_tasks={"P15-T01": "ready"},
    )
    result = _run(tmp_path, "workflow", "reconcile")
    assert result.exit_code == 0, result.output
    assert "issues            0" in result.output


# ---------------------------------------------------------------------------
# Check 1: backlog vs packet status mismatch
# ---------------------------------------------------------------------------

def test_reconcile_detects_backlog_behind_packet(tmp_path: Path):
    """Packet says done but backlog says ready — error-level mismatch."""
    _seed_working_docs(
        tmp_path,
        backlog_tasks={"P15-T01": "ready"},
    )
    _seed_packet(tmp_path, "P15-T01", "TASK-0103", "done")
    result = _run(tmp_path, "workflow", "reconcile")
    assert result.exit_code == 1, result.output
    assert "packet_backlog_mismatch" in result.output
    assert "P15-T01" in result.output
    assert "[error]" in result.output


def test_reconcile_backlog_behind_packet_json(tmp_path: Path):
    _seed_working_docs(
        tmp_path,
        backlog_tasks={"P15-T01": "in_progress"},
    )
    _seed_packet(tmp_path, "P15-T01", "TASK-0103", "done")
    result = _run_json(tmp_path, "workflow", "reconcile")
    data = json.loads(result.output)
    assert data["ok"] is False
    assert len(data["issues"]) >= 1
    issue = data["issues"][0]
    assert issue["check"] == "packet_backlog_mismatch"
    assert issue["fix_available"] is True
    assert "TASK-0103" not in issue["description"] or "P15-T01" in issue["description"]


def test_reconcile_fix_updates_backlog(tmp_path: Path):
    """--fix should update backlog to match done packet."""
    _seed_working_docs(
        tmp_path,
        backlog_tasks={"P15-T01": "ready"},
    )
    _seed_packet(tmp_path, "P15-T01", "TASK-0103", "done")
    result = _run(tmp_path, "workflow", "reconcile", "--fix")
    assert result.exit_code == 0, result.output
    assert "fixed" in result.output
    backlog = (tmp_path / "docs" / "working" / "backlog.md").read_text(encoding="utf-8")
    assert "**Status:** done" in backlog


def test_reconcile_dry_run_does_not_write(tmp_path: Path):
    """--dry-run should show repair but not write."""
    _seed_working_docs(
        tmp_path,
        backlog_tasks={"P15-T01": "ready"},
    )
    _seed_packet(tmp_path, "P15-T01", "TASK-0103", "done")
    result = _run(tmp_path, "workflow", "reconcile", "--dry-run")
    assert "dry-run" in result.output
    # Backlog should still say ready since no write happened
    backlog = (tmp_path / "docs" / "working" / "backlog.md").read_text(encoding="utf-8")
    assert "**Status:** ready" in backlog


# ---------------------------------------------------------------------------
# Check 2: current_task.md stale pointer
# ---------------------------------------------------------------------------

def test_reconcile_detects_stale_current_task(tmp_path: Path):
    """current_task.md points to a done packet — stale pointer."""
    packet_dir = _seed_packet(tmp_path, "P15-T01", "TASK-0103", "done")
    _seed_working_docs(
        tmp_path,
        backlog_tasks={"P15-T01": "done"},
        current_task_id="TASK-0103",
        current_task_path=f"tasks/{packet_dir.name}/",
        current_task_status="in_progress",
    )
    result = _run(tmp_path, "workflow", "reconcile")
    assert result.exit_code == 1, result.output
    assert "current_task_stale" in result.output
    assert "[error]" in result.output


def test_reconcile_fix_clears_stale_current_task(tmp_path: Path):
    """--fix should reset current_task.md to none/idle."""
    packet_dir = _seed_packet(tmp_path, "P15-T01", "TASK-0103", "done")
    _seed_working_docs(
        tmp_path,
        backlog_tasks={"P15-T01": "done"},
        current_task_id="TASK-0103",
        current_task_path=f"tasks/{packet_dir.name}/",
        current_task_status="in_progress",
    )
    result = _run(tmp_path, "workflow", "reconcile", "--fix")
    assert result.exit_code == 0, result.output
    current_task = (tmp_path / "docs" / "working" / "current_task.md").read_text(encoding="utf-8")
    assert "Task ID: none" in current_task
    assert "Status: idle" in current_task


# ---------------------------------------------------------------------------
# Check 3: needs_fix invisible to workflow
# ---------------------------------------------------------------------------

def test_reconcile_detects_needs_fix_invisible(tmp_path: Path):
    """Packet with needs_fix not referenced in current_task.md."""
    _seed_packet(tmp_path, "P15-T01", "TASK-0103", "needs_fix")
    _seed_working_docs(
        tmp_path,
        backlog_tasks={"P15-T01": "in_progress"},
    )
    result = _run(tmp_path, "workflow", "reconcile")
    # Warnings don't cause non-zero exit, but issue is reported
    assert "needs_fix_invisible" in result.output
    assert "[warn]" in result.output


def test_reconcile_needs_fix_not_flagged_when_in_current_task(tmp_path: Path):
    """needs_fix packet that IS referenced in current_task.md should not warn."""
    packet_dir = _seed_packet(tmp_path, "P15-T01", "TASK-0103", "needs_fix")
    _seed_working_docs(
        tmp_path,
        backlog_tasks={"P15-T01": "in_progress"},
        current_task_id="TASK-0103",
        current_task_path=f"tasks/{packet_dir.name}/",
        current_task_status="needs_fix",
    )
    result = _run(tmp_path, "workflow", "reconcile")
    assert "needs_fix_invisible" not in result.output


# ---------------------------------------------------------------------------
# JSON output
# ---------------------------------------------------------------------------

def test_reconcile_json_clean(tmp_path: Path):
    _seed_working_docs(tmp_path, backlog_tasks={"P15-T01": "ready"})
    result = _run_json(tmp_path, "workflow", "reconcile")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["issues"] == []
    assert data["fixed"] == []


def test_reconcile_json_with_issues(tmp_path: Path):
    _seed_working_docs(tmp_path, backlog_tasks={"P15-T01": "ready"})
    _seed_packet(tmp_path, "P15-T01", "TASK-0103", "done")
    result = _run_json(tmp_path, "workflow", "reconcile")
    data = json.loads(result.output)
    assert data["ok"] is False
    assert len(data["issues"]) == 1
    assert data["issues"][0]["severity"] == "error"
    assert data["issues"][0]["fix_available"] is True
