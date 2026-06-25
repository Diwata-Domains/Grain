"""Tests for the metrics service: duration, counts, closure, stop reasons, cache."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from grain.services.metrics_service import (
    compute_metrics,
    export_metrics,
    phase_metrics,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _write(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _phase_meta(root: Path, num: int, meta: dict) -> None:
    _write(
        root / "docs/archive/phases" / f"phase-{num}" / "metadata.json",
        json.dumps(meta),
    )


def _workflow_state(root: Path, stop_reason: str, name: str = "last_workflow_state.json") -> None:
    _write(
        root / ".grain" / name,
        json.dumps({"evaluation": {"stop_reason": stop_reason}}),
    )


# ── Phase metadata collection + duration ───────────────────────────────────────

def test_no_archive_returns_ok_with_empty_phases(tmp_path):
    result = compute_metrics(tmp_path, use_cache=False)
    assert result.ok
    assert result.phases == []
    assert result.phase_count == 0
    assert "no archived phases" in result.coverage_note


def test_phase_metadata_is_read_and_counted(tmp_path):
    _phase_meta(tmp_path, 5, {"phase": 5, "closed_at": "2026-01-10", "tasks_done": 9, "grain_version": "0.4.0"})
    _phase_meta(tmp_path, 6, {"phase": 6, "closed_at": "2026-01-20", "tasks_done": 7, "grain_version": "0.4.0"})

    result = compute_metrics(tmp_path, use_cache=False)
    assert result.phase_count == 2
    assert result.total_tasks_done == 16
    nums = [p.phase for p in result.phases]
    assert nums == [5, 6]


def test_duration_uses_prior_phase_close_as_open(tmp_path):
    _phase_meta(tmp_path, 5, {"phase": 5, "closed_at": "2026-01-10", "tasks_done": 9, "grain_version": "0.4.0"})
    _phase_meta(tmp_path, 6, {"phase": 6, "closed_at": "2026-01-20", "tasks_done": 7, "grain_version": "0.4.0"})

    result = compute_metrics(tmp_path, use_cache=False)
    p5, p6 = result.phases
    # First phase has no prior close → unknown duration.
    assert p5.opened_at == ""
    assert p5.duration_days is None
    # Phase 6 opens at phase 5 close; 10-day span.
    assert p6.opened_at == "2026-01-10"
    assert p6.duration_days == 10


def test_missing_close_date_yields_partial_coverage(tmp_path):
    # Pre-v0.4.0 style metadata: no closed_at / grain_version.
    _phase_meta(tmp_path, 16, {"phase": 16, "tasks_done": 8, "note": "pre-archive"})

    result = compute_metrics(tmp_path, use_cache=False)
    p = result.phases[0]
    assert p.coverage == "partial"
    assert p.duration_days is None
    assert "partial coverage" in result.coverage_note


def test_phase_number_inferred_from_dir_when_absent(tmp_path):
    _phase_meta(tmp_path, 9, {"tasks_done": 3})  # no "phase" key
    result = compute_metrics(tmp_path, use_cache=False)
    assert result.phases[0].phase == 9


# ── Closure rate ────────────────────────────────────────────────────────────────

def test_closure_rate_from_backlog_totals(tmp_path):
    _phase_meta(tmp_path, 7, {"phase": 7, "closed_at": "2026-02-01", "tasks_done": 3, "grain_version": "0.4.0"})
    _write(
        tmp_path / "docs/working/backlog.md",
        "## Phase 7 — Demo\n\n"
        "### P7-T01 — a\n- **Status:** done\n"
        "### P7-T02 — b\n- **Status:** done\n"
        "### P7-T03 — c\n- **Status:** done\n"
        "### P7-T04 — d\n- **Status:** ready\n",
    )
    result = compute_metrics(tmp_path, use_cache=False)
    p = result.phases[0]
    assert p.tasks_total == 4
    assert p.closure_rate == 0.75


def test_closure_rate_none_without_backlog(tmp_path):
    _phase_meta(tmp_path, 7, {"phase": 7, "closed_at": "2026-02-01", "tasks_done": 3, "grain_version": "0.4.0"})
    result = compute_metrics(tmp_path, use_cache=False)
    p = result.phases[0]
    assert p.tasks_total is None
    assert p.closure_rate is None


# ── Stop-reason frequency ───────────────────────────────────────────────────────

def test_stop_reasons_tallied_from_workflow_state(tmp_path):
    _phase_meta(tmp_path, 1, {"phase": 1, "tasks_done": 1})
    _workflow_state(tmp_path, "packet_required")
    result = compute_metrics(tmp_path, use_cache=False)
    assert any(s.reason == "packet_required" and s.count == 1 for s in result.stop_reasons)


def test_stop_reasons_empty_without_history(tmp_path):
    _phase_meta(tmp_path, 1, {"phase": 1, "tasks_done": 1})
    result = compute_metrics(tmp_path, use_cache=False)
    assert result.stop_reasons == []


def test_stop_reasons_from_history_dir_and_top_level_key(tmp_path):
    _phase_meta(tmp_path, 1, {"phase": 1, "tasks_done": 1})
    # A rotated snapshot in a history dir, top-level stop_reason shape.
    _write(
        tmp_path / ".grain/workflow_history/run-1.json",
        json.dumps({"stop_reason": "execution_in_flight"}),
    )
    _write(
        tmp_path / ".grain/workflow_history/run-2.json",
        json.dumps({"evaluation": {"stop_reason": "execution_in_flight"}}),
    )
    result = compute_metrics(tmp_path, use_cache=False)
    reasons = {s.reason: s.count for s in result.stop_reasons}
    assert reasons.get("execution_in_flight") == 2


# ── Single-phase lookup ─────────────────────────────────────────────────────────

def test_phase_metrics_returns_match_or_none(tmp_path):
    _phase_meta(tmp_path, 5, {"phase": 5, "closed_at": "2026-01-10", "tasks_done": 9, "grain_version": "0.4.0"})
    found = phase_metrics(tmp_path, 5, use_cache=False)
    assert found is not None and found.phase == 5
    assert phase_metrics(tmp_path, 99, use_cache=False) is None


# ── Cache TTL ───────────────────────────────────────────────────────────────────

def test_cache_is_written_and_reused(tmp_path):
    _phase_meta(tmp_path, 5, {"phase": 5, "closed_at": "2026-01-10", "tasks_done": 9, "grain_version": "0.4.0"})
    first = compute_metrics(tmp_path, use_cache=True)
    cache = tmp_path / ".grain/metrics_cache.json"
    assert cache.exists()
    assert first.cached is False

    # A fresh cache should be served on the next read (cached flag flips True).
    second = compute_metrics(tmp_path, use_cache=True)
    assert second.cached is True
    assert second.phase_count == first.phase_count


def test_cache_serves_stale_source_until_expiry(tmp_path):
    _phase_meta(tmp_path, 5, {"phase": 5, "closed_at": "2026-01-10", "tasks_done": 9, "grain_version": "0.4.0"})
    compute_metrics(tmp_path, use_cache=True)  # seed cache (1 phase)

    # Add a new phase but keep the fresh cache: cached read must NOT see it.
    _phase_meta(tmp_path, 6, {"phase": 6, "closed_at": "2026-01-20", "tasks_done": 7, "grain_version": "0.4.0"})
    cached = compute_metrics(tmp_path, use_cache=True)
    assert cached.cached is True
    assert cached.phase_count == 1


def test_expired_cache_is_recomputed(tmp_path):
    _phase_meta(tmp_path, 5, {"phase": 5, "closed_at": "2026-01-10", "tasks_done": 9, "grain_version": "0.4.0"})
    compute_metrics(tmp_path, use_cache=True)  # seed cache
    cache = tmp_path / ".grain/metrics_cache.json"

    # Age the cache beyond the 1-hour TTL.
    old = time.time() - 4000
    os.utime(cache, (old, old))

    _phase_meta(tmp_path, 6, {"phase": 6, "closed_at": "2026-01-20", "tasks_done": 7, "grain_version": "0.4.0"})
    result = compute_metrics(tmp_path, use_cache=True)
    assert result.cached is False
    assert result.phase_count == 2


def test_use_cache_false_bypasses_fresh_cache(tmp_path):
    _phase_meta(tmp_path, 5, {"phase": 5, "closed_at": "2026-01-10", "tasks_done": 9, "grain_version": "0.4.0"})
    compute_metrics(tmp_path, use_cache=True)  # seed fresh cache
    _phase_meta(tmp_path, 6, {"phase": 6, "closed_at": "2026-01-20", "tasks_done": 7, "grain_version": "0.4.0"})
    result = compute_metrics(tmp_path, use_cache=False)
    assert result.cached is False
    assert result.phase_count == 2


# ── Export ──────────────────────────────────────────────────────────────────────

def test_export_returns_full_history_dict(tmp_path):
    _phase_meta(tmp_path, 5, {"phase": 5, "closed_at": "2026-01-10", "tasks_done": 9, "grain_version": "0.4.0"})
    _workflow_state(tmp_path, "packet_required")
    data = export_metrics(tmp_path)
    assert data["ok"] is True
    assert data["phase_count"] == 1
    assert data["phases"][0]["phase"] == 5
    assert {"reason": "packet_required", "count": 1} in data["stop_reasons"]
