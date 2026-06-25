# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Telemetry service — opt-in, fire-and-forget event emission for Pulse.

``emit(root, event)`` is the single entry point. It is strictly side-band: it
NEVER raises, NEVER changes caller control flow, and NEVER alters the caller's
timing. Emission only happens when telemetry is explicitly enabled
(``telemetry.enabled: true`` in docs_manifest.yaml OR the
``GRAIN_TELEMETRY_ENDPOINT`` environment variable is set). Default off → nothing
is emitted and no queue file is written.

Non-blocking by construction: the only work ``emit`` does on the caller's thread
is the cheap, local gate check and event serialization. The network POST (and
its on-disk queue fallback) run on a short-lived daemon thread, so close /
accept / next / suggest-accept return without ever waiting on the network — even
when a configured endpoint is slow or unreachable.

When enabled, the event is POSTed to the configured Pulse endpoint. If no
endpoint is configured, or the endpoint is unreachable, the event is appended to
``.grain/telemetry_queue.jsonl`` so a later Pulse drain can pick it up. Building
events for the four instrumented moments goes through the ``make_*_event``
helpers so the typed, versioned contract stays in one place. ``flush(timeout)``
joins any in-flight dispatch threads — used by tests (and available to a drain)
to make the otherwise-async path deterministic; production callers never call it.
"""

from __future__ import annotations

import dataclasses
import json
import os
import threading
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
# Kept short so even a stalled drain thread tears down quickly; it runs off the
# hot path so this timeout never affects the instrumented operation's latency.
_POST_TIMEOUT_SECONDS = 2.0

# Tracks in-flight dispatch threads so ``flush`` can join them. A daemon thread
# never blocks interpreter exit, so this is only consulted by ``flush``.
_PENDING_LOCK = threading.Lock()
_PENDING: list[threading.Thread] = []


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
    """Emit one telemetry event. Fire-and-forget; NEVER raises; NEVER blocks.

    No-op when telemetry is disabled (the default). When enabled, the network
    POST (and its on-disk queue fallback) are dispatched on a short-lived daemon
    thread so the caller returns immediately — instrumentation never alters the
    timing of the instrumented operation. On any POST failure (no endpoint,
    transport error) the event is appended to ``.grain/telemetry_queue.jsonl``
    for a later Pulse drain.
    """
    try:
        if not is_enabled(root):
            return

        if not event.timestamp:
            event.timestamp = _now_iso()

        record = dataclasses.asdict(event)
        endpoint = _resolve_endpoint(root)

        _dispatch(root, endpoint, record)
    except Exception:
        # Telemetry is strictly side-band — never propagate any failure.
        return


def emit_built(root: Path, builder, *args, **kwargs) -> None:
    """Build an event via ``builder(*args, **kwargs)`` and emit it, guarded.

    Wraps event-builder construction inside the same never-raises guarantee as
    ``emit`` so the full path (build + emit) is covered at every call site, even
    if a builder were to raise. Use this at instrumentation points instead of
    evaluating the builder as an unguarded argument to ``emit``.
    """
    try:
        event = builder(*args, **kwargs)
    except Exception:
        return
    emit(root, event)


def _dispatch(root: Path, endpoint: str, record: dict) -> None:
    """Run the POST-or-queue work on a short-lived daemon thread (never blocks)."""
    thread = threading.Thread(
        target=_deliver,
        args=(root, endpoint, record),
        name="grain-telemetry",
        daemon=True,
    )
    with _PENDING_LOCK:
        _PENDING.append(thread)
    thread.start()


def _deliver(root: Path, endpoint: str, record: dict) -> None:
    """Off-thread delivery: POST, falling back to the on-disk queue. Never raises."""
    try:
        if endpoint and _try_post(endpoint, record):
            return
        _append_to_queue(root, record)
    except Exception:
        # Strictly side-band — swallow everything on the background thread too.
        return
    finally:
        current = threading.current_thread()
        with _PENDING_LOCK:
            if current in _PENDING:
                _PENDING.remove(current)


def flush(timeout: float | None = 5.0) -> None:
    """Join any in-flight dispatch threads. Never raises.

    Makes the otherwise-async emission path deterministic (tests, or a future
    drain that wants to wait for delivery). Production instrumentation never
    calls this — the dispatch threads are daemons and clean up on their own.
    """
    with _PENDING_LOCK:
        pending = list(_PENDING)
    for thread in pending:
        try:
            thread.join(timeout)
        except Exception:
            continue


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
