"""Tests for grain archive command group and archive service."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main
from grain.services.archive_service import (
    archive_phase_docs,
    archive_milestone,
    snapshot_working_docs,
    list_archives,
    show_archive,
    prune_archived_proposals,
    move_working_proposals_to_archive,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _run(tmp_path: Path, *args: str, fmt: str = "text"):
    runner = CliRunner()
    cmd = ["--repo", str(tmp_path)]
    if fmt == "json":
        cmd += ["--format", "json"]
    cmd += list(args)
    return runner.invoke(main, cmd)


def _write(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _base_working(tmp_path: Path) -> None:
    _write(tmp_path / "docs/working/backlog.md", "# Backlog\n\nContent.\n")
    _write(tmp_path / "docs/working/current_focus.md", "# Current Focus\n\nContent.\n")
    _write(tmp_path / "docs/working/open_questions.md", "# Open Questions\n\nContent.\n")
    _write(tmp_path / "docs/working/tooling_notes.md", "# Tooling Notes\n\nContent.\n")


# ── Phase archive (called by phase close) ────────────────────────────────────

def test_archive_phase_docs_creates_snapshot(tmp_path):
    _base_working(tmp_path)
    result = archive_phase_docs(tmp_path, "31", 8)

    assert result.ok
    archive_dir = tmp_path / "docs/archive/phases/phase-31"
    assert archive_dir.is_dir()
    assert (archive_dir / "backlog.md").exists()
    assert (archive_dir / "current_focus.md").exists()
    assert (archive_dir / "open_questions.md").exists()
    assert (archive_dir / "tooling_notes.md").exists()
    assert (archive_dir / "metadata.json").exists()


def test_archive_phase_docs_metadata_content(tmp_path):
    _base_working(tmp_path)
    archive_phase_docs(tmp_path, "31", 8)

    meta = json.loads((tmp_path / "docs/archive/phases/phase-31/metadata.json").read_text())
    assert meta["phase"] == 31
    assert meta["tasks_done"] == 8
    assert "closed_at" in meta
    assert "grain_version" in meta


def test_archive_phase_docs_dry_run_does_not_write(tmp_path):
    _base_working(tmp_path)
    result = archive_phase_docs(tmp_path, "31", 8, dry_run=True)

    assert result.ok
    assert result.dry_run
    assert not (tmp_path / "docs/archive/phases/phase-31").exists()


def test_archive_phase_docs_skips_missing_source(tmp_path):
    # Only create some working docs
    _write(tmp_path / "docs/working/backlog.md", "# Backlog\n")
    result = archive_phase_docs(tmp_path, "31", 5)

    assert result.ok
    archive_dir = tmp_path / "docs/archive/phases/phase-31"
    assert (archive_dir / "backlog.md").exists()
    assert not (archive_dir / "current_focus.md").exists()


# ── phase close integration ───────────────────────────────────────────────────

def test_phase_close_creates_archive(tmp_path):
    """grain phase close should produce docs/archive/phases/phase-N/."""
    _base_working(tmp_path)
    _write(tmp_path / "docs/runtime/docs_manifest.yaml",
           "version: 1\nproject:\n  name: Test\n")
    _write(tmp_path / "docs/working/workflow_metrics.md",
           "# Workflow Metrics\n\n### Phase 1\n\nContent.\n")
    _write(tmp_path / "docs/working/backlog.md",
           "# Backlog\n\n## 2. Phase 1 — Foundation\n\n"
           "### P1-T01 — Task\n- **Status:** done\n")
    _write(tmp_path / "docs/working/current_focus.md",
           "# Current Focus\n\n## Current Phase\nPhase 1 — Foundation\n")
    _write(tmp_path / "docs/working/current_task.md",
           "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: unset\n")

    result = _run(tmp_path, "phase", "close")
    assert result.exit_code == 0
    assert (tmp_path / "docs/archive/phases/phase-1").is_dir()
    assert (tmp_path / "docs/archive/phases/phase-1/backlog.md").exists()
    assert (tmp_path / "docs/archive/phases/phase-1/metadata.json").exists()


# ── Snapshot ──────────────────────────────────────────────────────────────────

def test_snapshot_creates_archive_dir(tmp_path):
    _base_working(tmp_path)
    result = snapshot_working_docs(tmp_path, label="pre-refactor")

    assert result.ok
    snapshots = list((tmp_path / "docs/archive/snapshots").iterdir())
    assert len(snapshots) == 1
    assert "pre-refactor" in snapshots[0].name
    assert (snapshots[0] / "backlog.md").exists()


def test_snapshot_auto_label_increments(tmp_path):
    _base_working(tmp_path)
    r1 = snapshot_working_docs(tmp_path)
    r2 = snapshot_working_docs(tmp_path)

    assert r1.ok and r2.ok
    assert r1.archive_path != r2.archive_path
    snapshots = list((tmp_path / "docs/archive/snapshots").iterdir())
    assert len(snapshots) == 2


def test_snapshot_dry_run_does_not_write(tmp_path):
    _base_working(tmp_path)
    result = snapshot_working_docs(tmp_path, dry_run=True)

    assert result.ok
    assert result.dry_run
    assert not (tmp_path / "docs/archive/snapshots").exists()


# ── Milestone ─────────────────────────────────────────────────────────────────

def test_milestone_creates_archive(tmp_path):
    _base_working(tmp_path)
    _write(tmp_path / "docs/canonical/product_scope.md", "# Product Scope\n\nContent.\n")
    (tmp_path / "tasks").mkdir(exist_ok=True)

    result = archive_milestone(tmp_path, "v0.4.0")

    assert result.ok
    archive_dir = tmp_path / "docs/archive/milestones/v0.4.0"
    assert archive_dir.is_dir()
    assert (archive_dir / "working/backlog.md").exists()
    assert (archive_dir / "canonical/product_scope.md").exists()
    assert (archive_dir / "tasks_index.json").exists()
    assert (archive_dir / "metadata.json").exists()


def test_milestone_tasks_index_populated(tmp_path):
    _base_working(tmp_path)
    packet_dir = tmp_path / "tasks/P1-T01-TASK-0001"
    packet_dir.mkdir(parents=True)
    _write(packet_dir / "task.md",
           "# Task\n\n## Metadata\n- **ID:** TASK-0001\n- **Status:** done\n")
    _write(packet_dir / "results.md", "# Results\nDone.\n")

    result = archive_milestone(tmp_path, "v0.4.0")

    assert result.ok
    index = json.loads((tmp_path / "docs/archive/milestones/v0.4.0/tasks_index.json").read_text())
    assert any(t["task_id"] == "TASK-0001" for t in index)
    assert any(t["has_results"] is True for t in index)


def test_milestone_errors_if_already_exists(tmp_path):
    _base_working(tmp_path)
    archive_milestone(tmp_path, "v0.4.0")
    result = archive_milestone(tmp_path, "v0.4.0")

    assert not result.ok
    assert "already exists" in result.errors[0]


def test_milestone_dry_run_does_not_write(tmp_path):
    _base_working(tmp_path)
    result = archive_milestone(tmp_path, "v0.4.0", dry_run=True)

    assert result.ok
    assert result.dry_run
    assert not (tmp_path / "docs/archive/milestones/v0.4.0").exists()


# ── List ──────────────────────────────────────────────────────────────────────

def test_list_archives_empty_when_no_archives(tmp_path):
    entries = list_archives(tmp_path)
    assert entries == []


def test_list_archives_returns_phase_entries(tmp_path):
    _base_working(tmp_path)
    archive_phase_docs(tmp_path, "30", 14)
    archive_phase_docs(tmp_path, "31", 8)

    entries = list_archives(tmp_path)
    names = {e.name for e in entries}
    assert "phase-30" in names
    assert "phase-31" in names


def test_list_archives_type_filter(tmp_path):
    _base_working(tmp_path)
    archive_phase_docs(tmp_path, "30", 14)
    snapshot_working_docs(tmp_path, label="test")

    phase_entries = list_archives(tmp_path, type_filter="phase")
    assert all(e.type == "phase" for e in phase_entries)

    snap_entries = list_archives(tmp_path, type_filter="snapshot")
    assert all(e.type == "snapshot" for e in snap_entries)


# ── Show ──────────────────────────────────────────────────────────────────────

def test_show_archive_phase(tmp_path):
    _base_working(tmp_path)
    archive_phase_docs(tmp_path, "31", 8)

    result = show_archive(tmp_path, "phase-31")
    assert result.ok
    assert result.archive_type == "phase"
    assert "metadata.json" in result.files
    assert result.metadata["tasks_done"] == 8


def test_show_archive_not_found(tmp_path):
    result = show_archive(tmp_path, "phase-99")
    assert not result.ok
    assert "not found" in result.errors[0]


# ── Prune ─────────────────────────────────────────────────────────────────────

def test_prune_archived_proposals_removes_old_files(tmp_path):
    proposals_dir = tmp_path / "docs/archive/proposals"
    proposals_dir.mkdir(parents=True)
    old_file = proposals_dir / "SUG-old.md"
    _write(old_file, "content")
    # Set mtime to 100 days ago
    import os
    old_time = (datetime.now(tz=timezone.utc) - timedelta(days=100)).timestamp()
    os.utime(old_file, (old_time, old_time))

    result = prune_archived_proposals(tmp_path, older_than_days=90)
    assert result.ok
    assert len(result.pruned) == 1
    assert not old_file.exists()


def test_prune_archived_proposals_keeps_recent_files(tmp_path):
    proposals_dir = tmp_path / "docs/archive/proposals"
    proposals_dir.mkdir(parents=True)
    recent_file = proposals_dir / "SUG-recent.md"
    _write(recent_file, "content")

    result = prune_archived_proposals(tmp_path, older_than_days=90)
    assert result.ok
    assert len(result.pruned) == 0
    assert recent_file.exists()


def test_prune_dry_run_does_not_delete(tmp_path):
    proposals_dir = tmp_path / "docs/archive/proposals"
    proposals_dir.mkdir(parents=True)
    old_file = proposals_dir / "SUG-old.md"
    _write(old_file, "content")
    import os
    old_time = (datetime.now(tz=timezone.utc) - timedelta(days=100)).timestamp()
    os.utime(old_file, (old_time, old_time))

    result = prune_archived_proposals(tmp_path, older_than_days=90, dry_run=True)
    assert result.ok
    assert result.dry_run
    assert len(result.pruned) == 1
    assert old_file.exists()  # not deleted


def test_move_working_proposals_to_archive(tmp_path):
    proposals_dir = tmp_path / "docs/working/proposals"
    proposals_dir.mkdir(parents=True)
    old_dismissed = proposals_dir / "SUG-001.md"
    _write(old_dismissed, "# Proposal\n\nStatus: dismissed\n")
    import os
    old_time = (datetime.now(tz=timezone.utc) - timedelta(days=35)).timestamp()
    os.utime(old_dismissed, (old_time, old_time))

    result = move_working_proposals_to_archive(tmp_path, older_than_days=30)
    assert result.ok
    assert len(result.pruned) == 1
    assert not old_dismissed.exists()
    assert (tmp_path / "docs/archive/proposals/SUG-001.md").exists()


# ── CLI integration ───────────────────────────────────────────────────────────

def test_archive_snapshot_cmd_text(tmp_path):
    _base_working(tmp_path)
    result = _run(tmp_path, "archive", "snapshot", "--label", "test")
    assert result.exit_code == 0
    assert "archive snapshot: ok" in result.output


def test_archive_snapshot_cmd_dry_run(tmp_path):
    _base_working(tmp_path)
    result = _run(tmp_path, "archive", "snapshot", "--dry-run")
    assert result.exit_code == 0
    assert "dry-run" in result.output


def test_archive_milestone_cmd(tmp_path):
    _base_working(tmp_path)
    result = _run(tmp_path, "archive", "milestone", "v0.4.0")
    assert result.exit_code == 0
    assert "archive milestone: ok" in result.output
    assert "v0.4.0" in result.output


def test_archive_list_cmd_empty(tmp_path):
    result = _run(tmp_path, "archive", "list")
    assert result.exit_code == 0
    assert "empty" in result.output


def test_archive_list_cmd_with_entries(tmp_path):
    _base_working(tmp_path)
    archive_phase_docs(tmp_path, "30", 14)
    result = _run(tmp_path, "archive", "list")
    assert result.exit_code == 0
    assert "phase-30" in result.output


def test_archive_list_cmd_json(tmp_path):
    _base_working(tmp_path)
    archive_phase_docs(tmp_path, "30", 14)
    result = _run(tmp_path, "archive", "list", fmt="json")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert any(e["name"] == "phase-30" for e in data)


def test_archive_show_cmd(tmp_path):
    _base_working(tmp_path)
    archive_phase_docs(tmp_path, "31", 8)
    result = _run(tmp_path, "archive", "show", "phase-31")
    assert result.exit_code == 0
    assert "phase-31" in result.output
    assert "tasks_done" in result.output or "8" in result.output


def test_archive_show_not_found_exits_nonzero(tmp_path):
    result = _run(tmp_path, "archive", "show", "phase-99")
    assert result.exit_code != 0


def test_archive_prune_cmd(tmp_path):
    result = _run(tmp_path, "archive", "prune", "--older-than", "90d")
    assert result.exit_code == 0
    assert "archive prune" in result.output


def test_archive_cmd_json_snapshot(tmp_path):
    _base_working(tmp_path)
    result = _run(tmp_path, "archive", "snapshot", "--label", "x", fmt="json")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "ok" in data
    assert "archive_path" in data
    assert "files_written" in data
