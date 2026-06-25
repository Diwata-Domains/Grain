"""Tests for the grain metrics command group (summary, --phase, export, JSON)."""

from __future__ import annotations

import json
from pathlib import Path

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


def _write(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _phase_meta(root: Path, num: int, meta: dict) -> None:
    _write(
        root / "docs/archive/phases" / f"phase-{num}" / "metadata.json",
        json.dumps(meta),
    )


def _seed(tmp_path: Path) -> None:
    _phase_meta(tmp_path, 5, {"phase": 5, "closed_at": "2026-01-10", "tasks_done": 9, "grain_version": "0.4.0"})
    _phase_meta(tmp_path, 6, {"phase": 6, "closed_at": "2026-01-20", "tasks_done": 7, "grain_version": "0.4.0"})
    _write(
        tmp_path / ".grain/last_workflow_state.json",
        json.dumps({"evaluation": {"stop_reason": "packet_required"}}),
    )


# ── Summary ──────────────────────────────────────────────────────────────────

def test_metrics_summary_text(tmp_path):
    _seed(tmp_path)
    result = _run(tmp_path, "metrics")
    assert result.exit_code == 0, result.output
    assert "grain metrics" in result.output
    assert "phases" in result.output
    assert "packet_required" in result.output


def test_metrics_summary_empty(tmp_path):
    result = _run(tmp_path, "metrics")
    assert result.exit_code == 0, result.output
    assert "no archived phases" in result.output


def test_metrics_summary_json(tmp_path):
    _seed(tmp_path)
    result = _run(tmp_path, "metrics", fmt="json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["phase_count"] == 2
    assert data["total_tasks_done"] == 16
    assert {"reason": "packet_required", "count": 1} in data["stop_reasons"]
    # Phase 6 duration derives from phase 5 close.
    p6 = next(p for p in data["phases"] if p["phase"] == 6)
    assert p6["duration_days"] == 10


def test_metrics_no_cache_flag(tmp_path):
    _seed(tmp_path)
    result = _run(tmp_path, "metrics", "--no-cache", fmt="json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["cached"] is False


# ── Single-phase detail ────────────────────────────────────────────────────────

def test_metrics_phase_detail_text(tmp_path):
    _seed(tmp_path)
    result = _run(tmp_path, "metrics", "--phase", "6")
    assert result.exit_code == 0, result.output
    assert "phase 6" in result.output
    assert "duration" in result.output


def test_metrics_phase_detail_json(tmp_path):
    _seed(tmp_path)
    result = _run(tmp_path, "metrics", "--phase", "6", fmt="json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["phase"] == 6
    assert data["closed_at"] == "2026-01-20"
    assert data["duration_days"] == 10


def test_metrics_phase_not_found_text_exits_two(tmp_path):
    _seed(tmp_path)
    result = _run(tmp_path, "metrics", "--phase", "99")
    assert result.exit_code == 2, result.output


def test_metrics_phase_not_found_json(tmp_path):
    _seed(tmp_path)
    result = _run(tmp_path, "metrics", "--phase", "99", fmt="json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is False
    assert data["phase"] == 99


# ── Export ──────────────────────────────────────────────────────────────────────

def test_metrics_export_dumps_full_history(tmp_path):
    _seed(tmp_path)
    result = _run(tmp_path, "metrics", "export")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["phase_count"] == 2
    assert len(data["phases"]) == 2
    assert "stop_reasons" in data


def test_metrics_export_json_flag(tmp_path):
    _seed(tmp_path)
    result = _run(tmp_path, "metrics", "export", fmt="json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["phase_count"] == 2
