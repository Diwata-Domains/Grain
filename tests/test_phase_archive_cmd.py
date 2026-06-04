"""Tests for `grain phase archive` command."""

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
# Helpers
# ---------------------------------------------------------------------------

def _seed_repo(
    tmp_path: Path,
    phase: str = "15",
    closed_marker: bool = True,
    packet_refs: list[str] | None = None,
) -> None:
    (tmp_path / "docs" / "working").mkdir(parents=True)

    marker_line = f"\nPhase {phase} closed: 2026-04-17 — 3 tasks done (grain-verified)\n" if closed_marker else ""
    (tmp_path / "docs" / "working" / "current_focus.md").write_text(
        f"# Current Focus\n\nPhase {phase} — Test Phase\n{marker_line}",
        encoding="utf-8",
    )

    # backlog with phase heading
    backlog_lines = [f"## 1. Phase {phase} — Test Phase\n\n"]
    for ref in (packet_refs or [f"P{phase}-T01", f"P{phase}-T02"]):
        backlog_lines.append(f"### {ref} — Task\n- **Status:** done\n\n")
    (tmp_path / "docs" / "working" / "backlog.md").write_text(
        "".join(backlog_lines), encoding="utf-8"
    )

    # create packet dirs
    (tmp_path / "tasks").mkdir(parents=True)
    for ref in (packet_refs or [f"P{phase}-T01", f"P{phase}-T02"]):
        packet_dir = tmp_path / "tasks" / f"{ref}-TASK-0001"
        packet_dir.mkdir()
        (packet_dir / "task.md").write_text("# Task\n- **ID:** TASK-0001\n- **Status:** done\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_archive_moves_packets_to_archive_dir(tmp_path: Path):
    _seed_repo(tmp_path, phase="15")
    result = _run(tmp_path, "phase", "archive", "15")
    assert result.exit_code == 0, result.output
    assert "phase archive: ok" in result.output
    assert "packets_moved   2" in result.output

    # Packets moved
    assert not (tmp_path / "tasks" / "P15-T01-TASK-0001").exists()
    assert (tmp_path / "tasks" / "archive" / "phase-15" / "P15-T01-TASK-0001").exists()
    assert (tmp_path / "tasks" / "archive" / "phase-15" / "P15-T02-TASK-0001").exists()


def test_archive_updates_backlog_heading(tmp_path: Path):
    _seed_repo(tmp_path, phase="15")
    result = _run(tmp_path, "phase", "archive", "15")
    assert result.exit_code == 0, result.output
    backlog = (tmp_path / "docs" / "working" / "backlog.md").read_text(encoding="utf-8")
    assert "archived" in backlog.lower()


def test_archive_json_output(tmp_path: Path):
    _seed_repo(tmp_path, phase="15")
    result = _run_json(tmp_path, "phase", "archive", "15")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["phase"] == "15"
    assert len(data["packets_moved"]) == 2
    assert "archive/phase-15" in data["archive_path"]
    assert data["dry_run"] is False


# ---------------------------------------------------------------------------
# Dry run
# ---------------------------------------------------------------------------

def test_archive_dry_run_does_not_move(tmp_path: Path):
    _seed_repo(tmp_path, phase="15")
    result = _run(tmp_path, "phase", "archive", "15", "--dry-run")
    assert result.exit_code == 0, result.output
    assert "dry_run" in result.output
    assert "packets_moved   2" in result.output
    # Packets still in original location
    assert (tmp_path / "tasks" / "P15-T01-TASK-0001").exists()
    assert not (tmp_path / "tasks" / "archive" / "phase-15").exists()


def test_archive_dry_run_json(tmp_path: Path):
    _seed_repo(tmp_path, phase="15")
    result = _run_json(tmp_path, "phase", "archive", "15", "--dry-run")
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["dry_run"] is True
    assert len(data["packets_moved"]) == 2


# ---------------------------------------------------------------------------
# Blocked states
# ---------------------------------------------------------------------------

def test_archive_blocked_when_phase_not_closed(tmp_path: Path):
    _seed_repo(tmp_path, phase="15", closed_marker=False)
    result = _run(tmp_path, "phase", "archive", "15")
    assert result.exit_code == 1
    assert "grain phase close" in result.output


def test_archive_blocked_when_no_packets(tmp_path: Path):
    _seed_repo(tmp_path, phase="15", packet_refs=[])
    # Remove all packets
    for p in (tmp_path / "tasks").iterdir():
        if p.is_dir():
            import shutil
            shutil.rmtree(p)
    result = _run(tmp_path, "phase", "archive", "15")
    assert result.exit_code == 1
    assert "no packet directories" in result.output or "already archived" in result.output


def test_archive_blocked_when_already_archived(tmp_path: Path):
    _seed_repo(tmp_path, phase="15")
    # First archive succeeds
    _run(tmp_path, "phase", "archive", "15")
    # Second archive should fail — destination exists, no packets left
    result = _run(tmp_path, "phase", "archive", "15")
    assert result.exit_code == 1


def test_archive_blocked_on_invalid_phase_number(tmp_path: Path):
    _seed_repo(tmp_path, phase="15")
    result = _run(tmp_path, "phase", "archive", "abc")
    assert result.exit_code == 1
    assert "invalid phase number" in result.output


# ---------------------------------------------------------------------------
# Multiple phases, only target phase moved
# ---------------------------------------------------------------------------

def test_archive_only_moves_target_phase_packets(tmp_path: Path):
    """Archiving phase 15 must not touch phase 16 packets."""
    _seed_repo(tmp_path, phase="15", packet_refs=["P15-T01", "P15-T02"])
    # Add a phase 16 packet
    p16 = tmp_path / "tasks" / "P16-T01-TASK-0099"
    p16.mkdir()
    (p16 / "task.md").write_text("# Task\n- **Status:** in_progress\n", encoding="utf-8")

    result = _run(tmp_path, "phase", "archive", "15")
    assert result.exit_code == 0, result.output
    # Phase 15 packets moved
    assert not (tmp_path / "tasks" / "P15-T01-TASK-0001").exists()
    # Phase 16 packet untouched
    assert (tmp_path / "tasks" / "P16-T01-TASK-0099").exists()
