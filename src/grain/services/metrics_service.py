# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Metrics service — per-phase velocity and stop-reason metrics, read-only.

Computes phase duration (open→close from archive metadata), task count, and
closure rate per phase, plus stop-reason frequency from ``.grain`` workflow-state
history. Results are cached to ``.grain/metrics_cache.json`` with a 1-hour TTL.
Everything degrades gracefully on sparse or pre-v0.4.0 data: missing metadata
fields become ``None`` and the coverage note flags partial coverage. The service
never mutates archives and never raises for expected absences.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path

# ── Source roots ───────────────────────────────────────────────────────────────

_PHASES_ROOT = "docs/archive/phases"
_GRAIN_DIR = ".grain"
_CACHE_FILE = "metrics_cache.json"
_BACKLOG = "docs/working/backlog.md"

# Cache time-to-live in seconds (1 hour).
_CACHE_TTL_SECONDS = 3600

# docs/archive/phases/phase-<N> directory name.
_PHASE_DIR_RE = re.compile(r"^phase-(\d+)$")

# backlog.md phase header and task/status lines.
_BACKLOG_PHASE_RE = re.compile(r"^##\s+(?:\d+\.\s+)?Phase\s+(\d+)\b")
_BACKLOG_TASK_RE = re.compile(r"^###\s+P(\d+)-T\d+")
_BACKLOG_STATUS_RE = re.compile(r"^-\s+\*\*Status:\*\*\s*(\S+)")


# ── Result types ──────────────────────────────────────────────────────────────

@dataclass
class PhaseMetrics:
    phase: int
    closed_at: str = ""
    opened_at: str = ""
    duration_days: int | None = None
    tasks_done: int = 0
    tasks_total: int | None = None
    closure_rate: float | None = None
    grain_version: str = ""
    coverage: str = "full"  # "full" | "partial"


@dataclass
class StopReasonCount:
    reason: str
    count: int


@dataclass
class MetricsResult:
    ok: bool
    phases: list[PhaseMetrics] = field(default_factory=list)
    stop_reasons: list[StopReasonCount] = field(default_factory=list)
    phase_count: int = 0
    total_tasks_done: int = 0
    coverage_note: str = ""
    cached: bool = False
    computed_at: str = ""
    errors: list[str] = field(default_factory=list)


# ── Public API ──────────────────────────────────────────────────────────────

def compute_metrics(root: Path, *, use_cache: bool = True) -> MetricsResult:
    """Return workflow metrics for all archived phases plus stop-reason counts.

    Reads from a 1-hour cache at ``.grain/metrics_cache.json`` when ``use_cache``
    is set and the cache is fresh; otherwise recomputes and refreshes the cache.
    Degrades gracefully when metadata/history is sparse — never raises for
    expected absences.
    """
    if use_cache:
        cached = _read_cache(root)
        if cached is not None:
            return cached

    result = _compute(root)
    _write_cache(root, result)
    return result


def phase_metrics(root: Path, phase: int, *, use_cache: bool = True) -> PhaseMetrics | None:
    """Return metrics for a single phase, or None if that phase is not archived."""
    result = compute_metrics(root, use_cache=use_cache)
    for p in result.phases:
        if p.phase == phase:
            return p
    return None


def export_metrics(root: Path) -> dict:
    """Return the full metrics history as a JSON-serializable dict (no cache)."""
    result = compute_metrics(root, use_cache=False)
    return _result_to_dict(result)


# ── Computation ───────────────────────────────────────────────────────────────

def _compute(root: Path) -> MetricsResult:
    phases = _collect_phase_metadata(root)
    backlog_totals = _backlog_task_counts(root)

    phase_metrics_list: list[PhaseMetrics] = []
    partial = False

    # Sort by phase number so duration (open = prior phase close) is deterministic.
    phases.sort(key=lambda m: m.get("phase", 0))
    prev_close = ""

    for meta in phases:
        num = meta.get("phase", 0)
        closed_at = str(meta.get("closed_at") or "")
        tasks_done = int(meta.get("tasks_done") or 0)
        grain_version = str(meta.get("grain_version") or "")

        opened_at = prev_close
        duration = _duration_days(opened_at, closed_at)

        total = backlog_totals.get(num)
        closure_rate = None
        if total:
            closure_rate = round(tasks_done / total, 4) if total else None

        coverage = "full"
        if not closed_at or not grain_version:
            coverage = "partial"
            partial = True

        phase_metrics_list.append(PhaseMetrics(
            phase=num,
            closed_at=closed_at,
            opened_at=opened_at,
            duration_days=duration,
            tasks_done=tasks_done,
            tasks_total=total,
            closure_rate=closure_rate,
            grain_version=grain_version,
            coverage=coverage,
        ))

        if closed_at:
            prev_close = closed_at

    stop_reasons = _collect_stop_reasons(root)
    total_done = sum(p.tasks_done for p in phase_metrics_list)

    coverage_note = ""
    if not phase_metrics_list:
        coverage_note = "no archived phases found — metrics unavailable"
    elif partial:
        coverage_note = (
            "partial coverage — some phases predate v0.4.0 metadata "
            "(missing close date or version); duration/closure may be incomplete"
        )

    return MetricsResult(
        ok=True,
        phases=phase_metrics_list,
        stop_reasons=stop_reasons,
        phase_count=len(phase_metrics_list),
        total_tasks_done=total_done,
        coverage_note=coverage_note,
        cached=False,
        computed_at=datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
    )


def _collect_phase_metadata(root: Path) -> list[dict]:
    """Read every docs/archive/phases/phase-<N>/metadata.json (best effort)."""
    phases_dir = root / _PHASES_ROOT
    if not phases_dir.exists():
        return []

    out: list[dict] = []
    for d in sorted(phases_dir.iterdir()):
        if not d.is_dir():
            continue
        m = _PHASE_DIR_RE.match(d.name)
        if not m:
            continue
        meta = _read_json(d / "metadata.json")
        if not isinstance(meta, dict):
            meta = {}
        # Trust the directory name for the phase number when metadata omits it.
        if "phase" not in meta:
            meta["phase"] = int(m.group(1))
        else:
            try:
                meta["phase"] = int(meta["phase"])
            except (TypeError, ValueError):
                meta["phase"] = int(m.group(1))
        out.append(meta)
    return out


def _backlog_task_counts(root: Path) -> dict[int, int]:
    """Return {phase_number: total_task_count} parsed from backlog.md (best effort)."""
    path = root / _BACKLOG
    if not path.exists():
        return {}
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return {}

    counts: dict[int, int] = {}
    for line in text.splitlines():
        tm = _BACKLOG_TASK_RE.match(line)
        if tm:
            phase = int(tm.group(1))
            counts[phase] = counts.get(phase, 0) + 1
    return counts


def _collect_stop_reasons(root: Path) -> list[StopReasonCount]:
    """Tally stop reasons across workflow-state JSON snapshots in .grain (best effort).

    There is no formal history log, so this reads the canonical
    ``last_workflow_state.json`` plus any ``*workflow_state*.json`` siblings (e.g.
    rotated/archived snapshots a host may keep). Absent history yields an empty
    list rather than an error.
    """
    grain_dir = root / _GRAIN_DIR
    if not grain_dir.exists():
        return []

    counts: dict[str, int] = {}
    seen: set[Path] = set()

    candidates: list[Path] = []
    primary = grain_dir / "last_workflow_state.json"
    if primary.exists():
        candidates.append(primary)
    for p in sorted(grain_dir.glob("*workflow_state*.json")):
        candidates.append(p)
    history_dir = grain_dir / "workflow_history"
    if history_dir.is_dir():
        for p in sorted(history_dir.glob("*.json")):
            candidates.append(p)

    for p in candidates:
        if p in seen or not p.is_file():
            continue
        seen.add(p)
        data = _read_json(p)
        for reason in _extract_stop_reasons(data):
            counts[reason] = counts.get(reason, 0) + 1

    pairs = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [StopReasonCount(reason=r, count=c) for r, c in pairs]


def _extract_stop_reasons(data: object) -> list[str]:
    """Pull stop_reason value(s) out of a workflow-state payload of any known shape."""
    reasons: list[str] = []
    if isinstance(data, dict):
        ev = data.get("evaluation")
        if isinstance(ev, dict):
            reason = ev.get("stop_reason")
            if reason:
                reasons.append(str(reason))
        reason = data.get("stop_reason")
        if reason:
            reasons.append(str(reason))
    elif isinstance(data, list):
        for item in data:
            reasons.extend(_extract_stop_reasons(item))
    return reasons


# ── Cache ─────────────────────────────────────────────────────────────────────

def _read_cache(root: Path) -> MetricsResult | None:
    cache = root / _GRAIN_DIR / _CACHE_FILE
    if not cache.exists():
        return None
    try:
        mtime = datetime.fromtimestamp(cache.stat().st_mtime, tz=timezone.utc)
        age = (datetime.now(tz=timezone.utc) - mtime).total_seconds()
        if age > _CACHE_TTL_SECONDS:
            return None
        # Parse directly (not via _read_json) so a corrupt/truncated cache raises
        # JSONDecodeError → falls through to recompute instead of being served as
        # an empty-but-valid {} result for the full TTL.
        data = json.loads(cache.read_text(encoding="utf-8"))
        # A valid cache is always a dict carrying a "phases" key; anything else
        # (list payload, partially-written object) is treated as corrupt.
        if not isinstance(data, dict) or "phases" not in data:
            return None
        return _dict_to_result(data, cached=True)
    except Exception:
        return None


def _write_cache(root: Path, result: MetricsResult) -> None:
    """Persist the computed result to .grain/metrics_cache.json (best effort).

    Writes to a sibling temp file then atomically ``os.replace``s it onto the
    cache path so a crash/kill/disk-full mid-write can never leave a truncated
    cache for the read path to misinterpret.
    """
    try:
        grain_dir = root / _GRAIN_DIR
        grain_dir.mkdir(exist_ok=True)
        cache = grain_dir / _CACHE_FILE
        tmp = cache.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(_result_to_dict(result), indent=2), encoding="utf-8")
        os.replace(tmp, cache)
    except Exception:
        # Caching is best-effort; never fail the read path on a write error.
        pass


# ── (De)serialization ─────────────────────────────────────────────────────────

def _result_to_dict(result: MetricsResult) -> dict:
    return {
        "ok": result.ok,
        "computed_at": result.computed_at,
        "phase_count": result.phase_count,
        "total_tasks_done": result.total_tasks_done,
        "coverage_note": result.coverage_note,
        "phases": [
            {
                "phase": p.phase,
                "closed_at": p.closed_at,
                "opened_at": p.opened_at,
                "duration_days": p.duration_days,
                "tasks_done": p.tasks_done,
                "tasks_total": p.tasks_total,
                "closure_rate": p.closure_rate,
                "grain_version": p.grain_version,
                "coverage": p.coverage,
            }
            for p in result.phases
        ],
        "stop_reasons": [
            {"reason": s.reason, "count": s.count} for s in result.stop_reasons
        ],
        "errors": result.errors,
    }


def _dict_to_result(data: dict, *, cached: bool) -> MetricsResult:
    phases = [
        PhaseMetrics(
            phase=int(p.get("phase", 0)),
            closed_at=str(p.get("closed_at") or ""),
            opened_at=str(p.get("opened_at") or ""),
            duration_days=p.get("duration_days"),
            tasks_done=int(p.get("tasks_done") or 0),
            tasks_total=p.get("tasks_total"),
            closure_rate=p.get("closure_rate"),
            grain_version=str(p.get("grain_version") or ""),
            coverage=str(p.get("coverage") or "full"),
        )
        for p in (data.get("phases") or [])
        if isinstance(p, dict)
    ]
    stop_reasons = [
        StopReasonCount(reason=str(s.get("reason", "")), count=int(s.get("count") or 0))
        for s in (data.get("stop_reasons") or [])
        if isinstance(s, dict)
    ]
    return MetricsResult(
        ok=bool(data.get("ok", True)),
        phases=phases,
        stop_reasons=stop_reasons,
        phase_count=int(data.get("phase_count") or len(phases)),
        total_tasks_done=int(data.get("total_tasks_done") or 0),
        coverage_note=str(data.get("coverage_note") or ""),
        cached=cached,
        computed_at=str(data.get("computed_at") or ""),
        errors=list(data.get("errors") or []),
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _duration_days(opened_at: str, closed_at: str) -> int | None:
    """Whole-day span from opened_at to closed_at (both ISO dates), else None."""
    start = _parse_date(opened_at)
    end = _parse_date(closed_at)
    if start is None or end is None:
        return None
    delta = (end - start).days
    return delta if delta >= 0 else None


def _parse_date(value: str) -> date | None:
    if not value:
        return None
    raw = value.strip()
    # Tolerate full ISO timestamps by taking the date component.
    if "T" in raw:
        raw = raw.split("T", 1)[0]
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None
