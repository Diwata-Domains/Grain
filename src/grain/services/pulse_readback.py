# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Pulse readback — optional, read-only cross-run/cross-machine metrics view.

``grain metrics --source pulse`` pulls the SAME per-phase + stop-reason rollups
that ``grain metrics`` computes locally, but from a running Pulse instance — so a
single command can show velocity aggregated across every run and machine that has
reported to that Pulse, not just the local repo's archive.

This is strictly **additive and opt-in**: the default ``--source local`` path is
untouched, and Pulse is never a hot-path dependency. Nothing here runs unless the
operator explicitly asks for ``--source pulse``.

Endpoint resolution (first match wins):

1. ``GRAIN_PULSE_ENDPOINT`` — a dedicated base URL, e.g. ``http://127.0.0.1:8006``.
2. ``GRAIN_TELEMETRY_ENDPOINT`` with its trailing ``/v1/events`` ingest suffix
   stripped — so an operator who already points Grain's telemetry at a Pulse gets
   readback for free, against the same host.

When ``--source pulse`` is requested but no endpoint is configured, or Pulse is
unreachable, the caller raises a clear, non-zero error — never a stack trace, and
the local path is never affected.

The reads are L0 read-only HTTP ``GET``s over stdlib ``urllib`` (the same
dependency-free transport Grain already uses for telemetry), with a short timeout.
This module never mutates anything, local or remote.

The Pulse → Grain shape mapping is intentionally lossy: Pulse's history has no
backlog totals or per-phase grain_version, so closure-rate / version / duration
fields that the local view fills in stay empty here and the phase is marked
``partial`` coverage. The fields Pulse *does* carry (phase, tasks_done, closed-at,
stop-reason counts) map straight onto the local result so both render identically.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from grain.services.metrics_service import (
    MetricsResult,
    PhaseMetrics,
    StopReasonCount,
)
from grain.services.telemetry_service import ENDPOINT_ENV_VAR as _TELEMETRY_ENV_VAR

# Dedicated base URL for Pulse readback (wins over the telemetry-derived one).
PULSE_ENDPOINT_ENV_VAR = "GRAIN_PULSE_ENDPOINT"

# Ingest suffix on a telemetry endpoint; stripped to recover the Pulse base URL.
_TELEMETRY_INGEST_SUFFIX = "/v1/events"

# Read-only metric rollup paths on Pulse (must match pulse.api.read).
_PHASES_PATH = "/v1/metrics/phases"
_STOP_REASONS_PATH = "/v1/metrics/stop-reasons"

# Short read timeout — readback is interactive but must not hang on a dead host.
_READ_TIMEOUT_SECONDS = 5.0


class PulseReadbackError(Exception):
    """Readback could not be served (no endpoint, or Pulse unreachable/bad reply).

    Carries a human-readable message the CLI turns into a clean non-zero error.
    Never surfaced as a stack trace.
    """


# ── Endpoint resolution ─────────────────────────────────────────────────────────

def resolve_endpoint() -> str | None:
    """Return the Pulse base URL (no trailing slash), or ``None`` if unconfigured.

    ``GRAIN_PULSE_ENDPOINT`` wins; otherwise ``GRAIN_TELEMETRY_ENDPOINT`` has its
    ``/v1/events`` ingest suffix stripped to recover the base URL. Returns ``None``
    when neither yields a usable value (the CLI turns that into a clear error).
    """
    dedicated = os.environ.get(PULSE_ENDPOINT_ENV_VAR, "").strip()
    if dedicated:
        return dedicated.rstrip("/")

    telemetry = os.environ.get(_TELEMETRY_ENV_VAR, "").strip()
    if telemetry:
        base = telemetry.rstrip("/")
        if base.endswith(_TELEMETRY_INGEST_SUFFIX):
            base = base[: -len(_TELEMETRY_INGEST_SUFFIX)]
        base = base.rstrip("/")
        if base:
            return base

    return None


# ── Public API ──────────────────────────────────────────────────────────────────

def fetch_metrics(root: Path | None = None) -> MetricsResult:
    """Fetch phase + stop-reason rollups from Pulse and shape them like the local view.

    ``root`` is accepted for call-site symmetry with the local path and is unused.
    Raises :class:`PulseReadbackError` (clean, non-zero in the CLI) when no endpoint
    is configured or Pulse is unreachable / returns an unusable reply.
    """
    endpoint = resolve_endpoint()
    if not endpoint:
        raise PulseReadbackError(
            "no Pulse endpoint configured for --source pulse — set "
            f"{PULSE_ENDPOINT_ENV_VAR} (e.g. http://127.0.0.1:8006), or "
            f"{_TELEMETRY_ENV_VAR} to your Pulse ingest URL"
        )

    phases_doc = _get_json(endpoint, _PHASES_PATH)
    stop_doc = _get_json(endpoint, _STOP_REASONS_PATH)

    return _to_result(phases_doc, stop_doc, endpoint)


# ── HTTP (read-only GET) ─────────────────────────────────────────────────────────

def _get_json(endpoint: str, path: str) -> dict:
    """Read-only HTTP GET returning a parsed JSON object. Raises on any failure."""
    url = f"{endpoint}{path}"
    request = urllib.request.Request(url, method="GET")
    request.add_header("Accept", "application/json")
    request.add_header("User-Agent", "grain-cli")
    try:
        with urllib.request.urlopen(request, timeout=_READ_TIMEOUT_SECONDS) as resp:  # noqa: S310
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        raise PulseReadbackError(
            f"Pulse returned HTTP {exc.code} for {url} — is this a Pulse endpoint?"
        ) from exc
    except (urllib.error.URLError, OSError, ValueError) as exc:
        reason = getattr(exc, "reason", exc)
        raise PulseReadbackError(
            f"could not reach Pulse at {url}: {reason} — is Pulse running and "
            "the endpoint correct?"
        ) from exc

    try:
        doc = json.loads(raw)
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise PulseReadbackError(
            f"Pulse reply at {url} was not valid JSON — is this a Pulse endpoint?"
        ) from exc
    if not isinstance(doc, dict):
        raise PulseReadbackError(
            f"Pulse reply at {url} had an unexpected shape (expected a JSON object)"
        )
    return doc


# ── Pulse → Grain shape mapping ──────────────────────────────────────────────────

def _to_result(phases_doc: dict, stop_doc: dict, endpoint: str) -> MetricsResult:
    """Map Pulse's ``/metrics/phases`` + ``/metrics/stop-reasons`` onto a MetricsResult.

    Pulse phase entry: ``{phase, closes, tasks_done, task_closes,
    first_closed_at, last_closed_at}``. Pulse has no backlog totals or per-phase
    version, so ``tasks_total`` / ``closure_rate`` / ``grain_version`` / duration
    stay empty and the phase is marked ``partial``.
    """
    phases: list[PhaseMetrics] = []
    for entry in phases_doc.get("phases") or []:
        if not isinstance(entry, dict):
            continue
        phases.append(
            PhaseMetrics(
                phase=_coerce_phase(entry.get("phase")),
                closed_at=str(entry.get("last_closed_at") or ""),
                opened_at=str(entry.get("first_closed_at") or ""),
                duration_days=None,
                tasks_done=_as_int(entry.get("tasks_done")),
                tasks_total=None,
                closure_rate=None,
                grain_version="",
                coverage="partial",
            )
        )

    stop_reasons: list[StopReasonCount] = []
    for entry in stop_doc.get("stop_reasons") or []:
        if not isinstance(entry, dict):
            continue
        reason = str(entry.get("reason", "") or "")
        if not reason:
            continue
        stop_reasons.append(
            StopReasonCount(reason=reason, count=_as_int(entry.get("count")))
        )

    phase_count = _as_int(phases_doc.get("phase_count")) or len(phases)
    total_done = phases_doc.get("total_tasks_done")
    if total_done is None:
        total_done = sum(p.tasks_done for p in phases)
    else:
        total_done = _as_int(total_done)

    note = (
        f"source: pulse ({endpoint}) — cross-run/cross-machine history; "
        "closure rate, version, and duration are local-only and omitted here"
    )

    return MetricsResult(
        ok=True,
        phases=phases,
        stop_reasons=stop_reasons,
        phase_count=phase_count,
        total_tasks_done=total_done,
        coverage_note=note,
        cached=False,
        computed_at="",
    )


def _coerce_phase(value: object) -> int:
    """Pulse phase keys are strings; render as int when numeric, else 0.

    Non-numeric phase keys (e.g. Pulse's catch-all ``""`` bucket) collapse to 0 so
    the int-typed local field stays well-formed; such rows are rare and benign.
    """
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return 0


def _as_int(value: object) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0
