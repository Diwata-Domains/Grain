"""Tests for phase close auto-archiving task packets (TASK-0214)."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main
from grain.services.archive_service import move_phase_packets


def _run(tmp_path: Path, *args: str):
    runner = CliRunner()
    return runner.invoke(main, ["--repo", str(tmp_path), *args])


def _write(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_repo(tmp_path: Path, phase: str = "15") -> None:
    """Seed the minimum docs + packet dirs needed for phase close tests."""
    (tmp_path / "docs" / "working").mkdir(parents=True)

    (tmp_path / "docs" / "working" / "current_focus.md").write_text(
        f"Phase {phase} — Test Phase\n", encoding="utf-8"
    )
    (tmp_path / "docs" / "working" / "current_task.md").write_text(
        "Task ID: none\nTask Path: none\nStatus: unset\n", encoding="utf-8"
    )
    (tmp_path / "docs" / "working" / "backlog.md").write_text(
        f"## 1. Phase {phase} — Test Phase\n\n"
        f"### P{phase}-T01 — Task one\n- **Status:** done\n\n"
        f"### P{phase}-T02 — Task two\n- **Status:** done\n\n",
        encoding="utf-8",
    )


def _seed_packets(tmp_path: Path, phase: str = "15") -> None:
    for n, tid in ((1, "0001"), (2, "0002")):
        d = tmp_path / "tasks" / f"P{phase}-T0{n}-TASK-{tid}"
        _write(d / "task.md",
               f"# Task: Task {n}\n\n## Metadata\n- **ID:** TASK-{tid}\n- **Status:** done\n")
        _write(d / "results.md", "# Results\nDone.\n")


# ── service: move_phase_packets ─────────────────────────────────────────────────

def test_move_phase_packets_moves_dirs(tmp_path):
    _seed_packets(tmp_path, "15")
    result = move_phase_packets(tmp_path, "15")

    assert result.ok
    assert result.tasks_done == 2
    assert len(result.moved) == 2
    archive = tmp_path / "tasks" / "archive" / "phase-15"
    assert (archive / "P15-T01-TASK-0001" / "task.md").exists()
    assert (archive / "P15-T02-TASK-0002" / "task.md").exists()
    # Active tasks/ is left clean of the moved packets.
    assert not (tmp_path / "tasks" / "P15-T01-TASK-0001").exists()
    assert not (tmp_path / "tasks" / "P15-T02-TASK-0002").exists()


def test_move_phase_packets_updates_metadata(tmp_path):
    # archive_phase_docs has already written the canonical backlog-derived
    # tasks_done; move_phase_packets must record the archive location + packet
    # count WITHOUT clobbering tasks_done.
    _write(tmp_path / "docs/archive/phases/phase-15/metadata.json",
           json.dumps({"phase": 15, "closed_at": "2026-06-24", "tasks_done": 2}))
    _seed_packets(tmp_path, "15")

    result = move_phase_packets(tmp_path, "15")
    assert result.ok

    meta = json.loads(
        (tmp_path / "docs/archive/phases/phase-15/metadata.json").read_text()
    )
    # Canonical completed-task count is preserved, not overwritten.
    assert meta["tasks_done"] == 2
    assert meta["tasks_archive"] == "tasks/archive/phase-15"
    assert meta["packets_archived_count"] == 2


def test_move_phase_packets_keep_tasks_skips(tmp_path):
    _seed_packets(tmp_path, "15")
    result = move_phase_packets(tmp_path, "15", keep_tasks=True)

    assert result.ok
    assert result.skipped
    assert result.moved == []
    assert (tmp_path / "tasks" / "P15-T01-TASK-0001").exists()
    assert not (tmp_path / "tasks" / "archive" / "phase-15").exists()


def test_move_phase_packets_no_match_graceful(tmp_path):
    (tmp_path / "tasks").mkdir()
    result = move_phase_packets(tmp_path, "15")

    assert result.ok
    assert result.moved == []
    assert result.tasks_done == 0


def test_move_phase_packets_idempotent(tmp_path):
    _seed_packets(tmp_path, "15")
    first = move_phase_packets(tmp_path, "15")
    assert first.ok and len(first.moved) == 2

    second = move_phase_packets(tmp_path, "15")
    assert second.ok
    assert second.moved == []
    # tasks_done still reflects the already-archived packets.
    assert second.tasks_done == 2
    archive = tmp_path / "tasks" / "archive" / "phase-15"
    assert (archive / "P15-T01-TASK-0001").exists()


def test_move_phase_packets_dry_run_does_not_move(tmp_path):
    _seed_packets(tmp_path, "15")
    result = move_phase_packets(tmp_path, "15", dry_run=True)

    assert result.ok
    assert result.dry_run
    assert len(result.moved) == 2
    assert (tmp_path / "tasks" / "P15-T01-TASK-0001").exists()
    assert not (tmp_path / "tasks" / "archive" / "phase-15").exists()


def test_move_phase_packets_preserves_backlog_tasks_done(tmp_path):
    # Regression (HIGH): backlog has 3 done tasks (archive_phase_docs wrote
    # tasks_done=3) but only 1 packet dir on disk. move_phase_packets must NOT
    # overwrite tasks_done with the packet count — metrics depends on it.
    _write(tmp_path / "docs/archive/phases/phase-15/metadata.json",
           json.dumps({"phase": 15, "closed_at": "2026-06-24", "tasks_done": 3}))
    d = tmp_path / "tasks" / "P15-T01-TASK-0001"
    _write(d / "task.md", "# Task: Only packet\n")

    result = move_phase_packets(tmp_path, "15")
    assert result.ok
    assert result.packets_archived == 1

    meta = json.loads(
        (tmp_path / "docs/archive/phases/phase-15/metadata.json").read_text()
    )
    # Before the fix this was clobbered to 1; the canonical count must survive.
    assert meta["tasks_done"] == 3
    assert meta["packets_archived_count"] == 1
    assert meta["tasks_archive"] == "tasks/archive/phase-15"


def test_move_phase_packets_collision_reports_only_moved(tmp_path):
    # Regression (LOW): on a mid-loop collision the moved list must contain only
    # packets actually moved, not the unprocessed tail still sitting in tasks/.
    _seed_packets(tmp_path, "15")  # T01, T02
    third = tmp_path / "tasks" / "P15-T03-TASK-0003"
    _write(third / "task.md", "# Task: Third\n")
    # Pre-create a colliding archive entry for T02 (the second in sorted order).
    _write(
        tmp_path / "tasks" / "archive" / "phase-15" / "P15-T02-TASK-0002" / "task.md",
        "# Task: Pre-existing\n",
    )

    result = move_phase_packets(tmp_path, "15")
    assert not result.ok
    assert result.errors
    # T01 was moved before the T02 collision; T03 was never processed.
    assert result.moved == ["tasks/P15-T01-TASK-0001"]
    # T01 really moved out of tasks/; T03 untouched in tasks/.
    assert not (tmp_path / "tasks" / "P15-T01-TASK-0001").exists()
    assert (tmp_path / "tasks" / "P15-T03-TASK-0003").exists()


# ── phase close integration ─────────────────────────────────────────────────────

def test_phase_close_archives_packets(tmp_path):
    _seed_repo(tmp_path, "15")
    _seed_packets(tmp_path, "15")

    result = _run(tmp_path, "phase", "close")
    assert result.exit_code == 0, result.output
    assert "phase close: ok" in result.output

    archive = tmp_path / "tasks" / "archive" / "phase-15"
    assert (archive / "P15-T01-TASK-0001" / "task.md").exists()
    assert (archive / "P15-T02-TASK-0002" / "task.md").exists()
    assert not (tmp_path / "tasks" / "P15-T01-TASK-0001").exists()

    meta = json.loads(
        (tmp_path / "docs/archive/phases/phase-15/metadata.json").read_text()
    )
    assert meta["tasks_done"] == 2
    assert meta["tasks_archive"] == "tasks/archive/phase-15"


def test_phase_close_keep_tasks_leaves_packets(tmp_path):
    _seed_repo(tmp_path, "15")
    _seed_packets(tmp_path, "15")

    result = _run(tmp_path, "phase", "close", "--keep-tasks")
    assert result.exit_code == 0, result.output
    assert "--keep-tasks" in result.output
    assert (tmp_path / "tasks" / "P15-T01-TASK-0001").exists()
    assert not (tmp_path / "tasks" / "archive" / "phase-15").exists()


def test_phase_close_no_packets_graceful(tmp_path):
    _seed_repo(tmp_path, "15")
    (tmp_path / "tasks").mkdir()

    result = _run(tmp_path, "phase", "close")
    assert result.exit_code == 0, result.output
    assert "phase close: ok" in result.output


def test_phase_close_dry_run_does_not_move_packets(tmp_path):
    _seed_repo(tmp_path, "15")
    _seed_packets(tmp_path, "15")

    result = _run(tmp_path, "phase", "close", "--dry-run")
    assert result.exit_code == 0, result.output
    assert (tmp_path / "tasks" / "P15-T01-TASK-0001").exists()
    assert not (tmp_path / "tasks" / "archive" / "phase-15").exists()


def test_phase_close_json_includes_packets(tmp_path):
    _seed_repo(tmp_path, "15")
    _seed_packets(tmp_path, "15")

    result = _run(tmp_path, "--format", "json", "phase", "close")
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["ok"] is True
    assert len(payload["packets_archived"]) == 2
    assert payload["packets_archive_path"] == "tasks/archive/phase-15"


def test_phase_close_metadata_tasks_done_matches_backlog(tmp_path):
    # Regression (HIGH): 3 done tasks in backlog but only 1 packet dir. After
    # phase close, metadata tasks_done must be 3 (backlog-derived), not 1.
    (tmp_path / "docs" / "working").mkdir(parents=True)
    (tmp_path / "docs" / "working" / "current_focus.md").write_text(
        "Phase 15 — Test Phase\n", encoding="utf-8"
    )
    (tmp_path / "docs" / "working" / "current_task.md").write_text(
        "Task ID: none\nTask Path: none\nStatus: unset\n", encoding="utf-8"
    )
    (tmp_path / "docs" / "working" / "backlog.md").write_text(
        "## 1. Phase 15 — Test Phase\n\n"
        "### P15-T01 — Task one\n- **Status:** done\n\n"
        "### P15-T02 — Task two\n- **Status:** done\n\n"
        "### P15-T03 — Task three\n- **Status:** done\n\n",
        encoding="utf-8",
    )
    # Only one packet dir on disk (the other two are doc-only / deleted packets).
    d = tmp_path / "tasks" / "P15-T01-TASK-0001"
    _write(d / "task.md", "# Task: Only packet\n")

    result = _run(tmp_path, "phase", "close")
    assert result.exit_code == 0, result.output

    meta = json.loads(
        (tmp_path / "docs/archive/phases/phase-15/metadata.json").read_text()
    )
    assert meta["tasks_done"] == 3
    assert meta["packets_archived_count"] == 1


def test_phase_close_surfaces_packet_move_failure(tmp_path):
    # Regression (MEDIUM): an archive collision during the packet move must be
    # surfaced as a failed close (exit 1) with the error propagated, not a
    # silent 'phase close: ok' that hides a half-moved workspace.
    _seed_repo(tmp_path, "15")
    _seed_packets(tmp_path, "15")
    # Pre-create a colliding archive entry for one of the packets.
    _write(
        tmp_path / "tasks" / "archive" / "phase-15" / "P15-T01-TASK-0001" / "task.md",
        "# Task: Pre-existing\n",
    )

    result = _run(tmp_path, "phase", "close")
    assert result.exit_code == 1, result.output
    assert "already exists" in result.output


def test_phase_close_packet_move_failure_json(tmp_path):
    # Regression (MEDIUM): JSON form propagates the error and reports ok=False.
    _seed_repo(tmp_path, "16")
    _seed_packets(tmp_path, "16")
    _write(
        tmp_path / "tasks" / "archive" / "phase-16" / "P16-T01-TASK-0001" / "task.md",
        "# Task: Pre-existing\n",
    )
    jresult = _run(tmp_path, "--format", "json", "phase", "close")
    assert jresult.exit_code == 1, jresult.output
    payload = json.loads(jresult.output)
    assert payload["ok"] is False
    assert any("already exists" in e for e in payload["errors"])
