# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Telemetry service — opt-in, fire-and-forget event emission for Pulse.

``emit(root, event)`` is the single entry point. It is strictly side-band: it
NEVER raises and NEVER changes caller control flow. Emission only happens when
telemetry is explicitly enabled (``telemetry.enabled: true`` in
docs_manifest.yaml OR the ``GRAIN_TELEMETRY_ENDPOINT`` environment variable is
set). Default off → nothing is emitted and no queue file is written.

When enabled, the event is POSTed to the configured Pulse endpoint. If no
endpoint is configured, or the endpoint is unreachable, the event is appended to
``.grain/telemetry_queue.jsonl`` so a later Pulse drain can pick it up. Building
events for the four instrumented moments goes through the ``make_*_event``
helpers so the typed, versioned contract stays in one place.
"""

from __future__ import annotations

import dataclasses
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from grain.adapters.manifest import load_telemetry_config
from grain.domain.telemetry import (
    EVENT_PHASE_CLOSE,
    EVENT_SUGGEST_ACCEPT,
    EVENT_TASK_CLOSE,
    EVENT_WORKFLOW_NEXT_STOP,
    TELEMETRY_EVENT_VERSION,
    TelemetryEvent,
)

# Environment override for the Pulse ingest URL. Setting it also turns telemetry
# on (opt-in via env), independent of the manifest block.
ENDPOINT_ENV_VAR = "GRAIN_TELEMETRY_ENDPOINT"

_QUEUE_FILE = "telemetry_queue.jsonl"
_GRAIN_DIR = ".grain"
_POST_TIMEOUT_SECONDS = 2.0


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _resolve_endpoint(root: Path) -> str:
    """Return the configured Pulse endpoint (env wins over manifest)."""
    env_endpoint = os.environ.get(ENDPOINT_ENV_VAR, "").strip()
    if env_endpoint:
        return env_endpoint
    return load_telemetry_config(root).endpoint


def is_enabled(root: Path) -> bool:
    """Return True when telemetry is opt-in enabled for this repo.

    Enabled when ``telemetry.enabled: true`` in docs_manifest.yaml OR the
    ``GRAIN_TELEMETRY_ENDPOINT`` env var is set. Never raises.
    """
    try:
        if os.environ.get(ENDPOINT_ENV_VAR, "").strip():
            return True
        return load_telemetry_config(root).enabled
    except Exception:
        return False


def emit(root: Path, event: TelemetryEvent) -> None:
    """Emit one telemetry event. Fire-and-forget; NEVER raises.

    No-op when telemetry is disabled (the default). When enabled, POSTs the event
    to the configured endpoint; on any failure (no endpoint, transport error)
    the event is appended to ``.grain/telemetry_queue.jsonl`` for later drain.
    """
    try:
        if not is_enabled(root):
            return

        if not event.timestamp:
            event.timestamp = _now_iso()

        record = dataclasses.asdict(event)
        endpoint = _resolve_endpoint(root)

        if endpoint and _try_post(endpoint, record):
            return

        _append_to_queue(root, record)
    except Exception:
        # Telemetry is strictly side-band — never propagate any failure.
        return


def _try_post(endpoint: str, record: dict) -> bool:
    """POST the event JSON to the Pulse endpoint. Return True on success.

    Dependency-free (stdlib urllib) and best-effort: any transport/HTTP error
    returns False so the caller falls back to the on-disk queue.
    """
    try:
        data = json.dumps(record).encode("utf-8")
        request = urllib.request.Request(endpoint, data=data, method="POST")
        request.add_header("Content-Type", "application/json")
        request.add_header("User-Agent", "grain-cli")
        with urllib.request.urlopen(request, timeout=_POST_TIMEOUT_SECONDS):  # noqa: S310
            return True
    except Exception:
        return False


def _append_to_queue(root: Path, record: dict) -> None:
    """Append one JSON line to ``.grain/telemetry_queue.jsonl`` (best effort)."""
    grain_dir = root / _GRAIN_DIR
    grain_dir.mkdir(exist_ok=True)
    queue_path = grain_dir / _QUEUE_FILE
    with queue_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


# ── Typed event builders (versioned contract lives here) ───────────────────────

def make_phase_close_event(phase: str, tasks_done: int) -> TelemetryEvent:
    """Build a versioned phase.close event."""
    return TelemetryEvent(
        event_type=EVENT_PHASE_CLOSE,
        version=TELEMETRY_EVENT_VERSION,
        timestamp=_now_iso(),
        payload={"phase": phase, "tasks_done": tasks_done},
    )


def make_task_close_event(task_id: str, *, quick: bool = False) -> TelemetryEvent:
    """Build a versioned task.close event."""
    return TelemetryEvent(
        event_type=EVENT_TASK_CLOSE,
        version=TELEMETRY_EVENT_VERSION,
        timestamp=_now_iso(),
        payload={"task_id": task_id, "quick": quick},
    )


def make_suggest_accept_event(proposal_id: str, kind: str) -> TelemetryEvent:
    """Build a versioned suggest.accept event."""
    return TelemetryEvent(
        event_type=EVENT_SUGGEST_ACCEPT,
        version=TELEMETRY_EVENT_VERSION,
        timestamp=_now_iso(),
        payload={"proposal_id": proposal_id, "kind": kind},
    )


def make_workflow_next_stop_event(stop_reason: str, phase: str) -> TelemetryEvent:
    """Build a versioned workflow.next.stop_reason event."""
    return TelemetryEvent(
        event_type=EVENT_WORKFLOW_NEXT_STOP,
        version=TELEMETRY_EVENT_VERSION,
        timestamp=_now_iso(),
        payload={"stop_reason": stop_reason, "phase": phase},
    )
