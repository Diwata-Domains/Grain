"""Tests for archive show listing archived task packets (TASK-0215)."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main
from grain.services.archive_service import show_archive


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


def _seed_phase_archive(tmp_path: Path, phase: str = "15", with_packets: bool = True) -> None:
    """Seed a phase doc archive + (optionally) an archived packet set."""
    meta = {
        "phase": int(phase),
        "closed_at": "2026-06-24",
        "tasks_done": 2 if with_packets else 0,
        "grain_version": "0.4.0",
    }
    if with_packets:
        meta["tasks_archive"] = f"tasks/archive/phase-{phase}"
    _write(tmp_path / f"docs/archive/phases/phase-{phase}/metadata.json",
           json.dumps(meta, indent=2))
    _write(tmp_path / f"docs/archive/phases/phase-{phase}/backlog.md", "# Backlog\n")

    if with_packets:
        for n, tid, title in ((1, "0001", "First task"), (2, "0002", "Second task")):
            d = tmp_path / "tasks" / "archive" / f"phase-{phase}" / f"P{phase}-T0{n}-TASK-{tid}"
            _write(d / "task.md",
                   f"# Task: {title}\n\n## Metadata\n- **ID:** TASK-{tid}\n- **Status:** done\n")


# ── service: show_archive packets ───────────────────────────────────────────────

def test_show_archive_lists_packets(tmp_path):
    _seed_phase_archive(tmp_path, "15")
    result = show_archive(tmp_path, "phase-15")

    assert result.ok
    assert result.archive_type == "phase"
    ids = {p.task_id for p in result.packets}
    assert ids == {"TASK-0001", "TASK-0002"}
    titles = {p.title for p in result.packets}
    assert titles == {"First task", "Second task"}
    paths = {p.path for p in result.packets}
    assert "tasks/archive/phase-15/P15-T01-TASK-0001" in paths


def test_show_archive_no_task_archive_graceful(tmp_path):
    _seed_phase_archive(tmp_path, "15", with_packets=False)
    result = show_archive(tmp_path, "phase-15")

    assert result.ok
    assert result.packets == []
    assert result.packets_note
    assert "before" in result.packets_note


def test_show_archive_missing_task_archive_dir(tmp_path):
    # metadata references a tasks_archive path that does not exist on disk.
    _write(tmp_path / "docs/archive/phases/phase-15/metadata.json",
           json.dumps({"phase": 15, "tasks_archive": "tasks/archive/phase-15"}))
    result = show_archive(tmp_path, "phase-15")

    assert result.ok
    assert result.packets == []
    assert "not found" in result.packets_note


# ── CLI: archive show ───────────────────────────────────────────────────────────

def test_archive_show_cmd_lists_packets(tmp_path):
    _seed_phase_archive(tmp_path, "15")
    result = _run(tmp_path, "archive", "show", "phase-15")

    assert result.exit_code == 0, result.output
    assert "packets" in result.output
    assert "TASK-0001" in result.output
    assert "First task" in result.output


def test_archive_show_cmd_json_packets_array(tmp_path):
    _seed_phase_archive(tmp_path, "15")
    result = _run(tmp_path, "archive", "show", "phase-15", fmt="json")

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert "packets" in data
    assert isinstance(data["packets"], list)
    assert {p["task_id"] for p in data["packets"]} == {"TASK-0001", "TASK-0002"}
    assert any(p["title"] == "First task" for p in data["packets"])


def test_archive_show_cmd_no_archive_note(tmp_path):
    _seed_phase_archive(tmp_path, "15", with_packets=False)
    result = _run(tmp_path, "archive", "show", "phase-15", fmt="json")

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["packets"] == []
    assert data["packets_note"]


def test_archive_show_cmd_no_archive_text(tmp_path):
    _seed_phase_archive(tmp_path, "15", with_packets=False)
    result = _run(tmp_path, "archive", "show", "phase-15")

    assert result.exit_code == 0, result.output
    assert "packets" in result.output
