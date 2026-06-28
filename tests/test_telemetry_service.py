# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""Tests for the Pulse telemetry foundation (domain, service, instrumentation).

Covers the opt-in gate (off by default → no events / no queue file), the queue
fallback when enabled without a reachable endpoint, the endpoint POST path, and
the strict never-raises contract — plus instrumentation of the four moments
(phase close, task close, suggest accept, workflow next stop reason).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from grain.domain.telemetry import (
    EVENT_PHASE_CLOSE,
    EVENT_SUGGEST_ACCEPT,
    EVENT_TASK_CLOSE,
    EVENT_WORKFLOW_NEXT_STOP,
    TELEMETRY_EVENT_VERSION,
    TelemetryEvent,
)
from grain.services import telemetry_service
from grain.services.telemetry_service import (
    ENDPOINT_ENV_VAR,
    emit,
    emit_built,
    flush,
    is_enabled,
    make_phase_close_event,
    make_suggest_accept_event,
    make_task_close_event,
    make_workflow_next_stop_event,
)


def _write(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _manifest(tmp_path: Path, *, enabled: bool = False, endpoint: str = "") -> None:
    _write(
        tmp_path / "docs/runtime/docs_manifest.yaml",
        "version: 1\n"
        "project:\n  name: test\n"
        "telemetry:\n"
        f"  enabled: {'true' if enabled else 'false'}\n"
        f'  endpoint: "{endpoint}"\n',
    )


def _queue_path(tmp_path: Path) -> Path:
    return tmp_path / ".grain" / "telemetry_queue.jsonl"


def _read_queue(tmp_path: Path) -> list[dict]:
    path = _queue_path(tmp_path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


# ── Gate: off by default ───────────────────────────────────────────────────────

def test_disabled_by_default_emits_nothing(tmp_path, monkeypatch):
    monkeypatch.delenv(ENDPOINT_ENV_VAR, raising=False)
    # No manifest at all → disabled.
    assert is_enabled(tmp_path) is False
    emit(tmp_path, make_phase_close_event("30", 5))
    assert not _queue_path(tmp_path).exists()


def test_manifest_disabled_emits_nothing(tmp_path, monkeypatch):
    monkeypatch.delenv(ENDPOINT_ENV_VAR, raising=False)
    _manifest(tmp_path, enabled=False)
    assert is_enabled(tmp_path) is False
    emit(tmp_path, make_task_close_event("TASK-0001"))
    assert not _queue_path(tmp_path).exists()


# ── Gate: enabled paths ────────────────────────────────────────────────────────

def test_manifest_enabled_no_endpoint_queues(tmp_path, monkeypatch):
    monkeypatch.delenv(ENDPOINT_ENV_VAR, raising=False)
    _manifest(tmp_path, enabled=True)
    assert is_enabled(tmp_path) is True

    emit(tmp_path, make_phase_close_event("31", 7))
    flush()  # delivery is async (daemon thread); drain it for a deterministic read

    queued = _read_queue(tmp_path)
    assert len(queued) == 1
    assert queued[0]["event_type"] == EVENT_PHASE_CLOSE
    assert queued[0]["version"] == TELEMETRY_EVENT_VERSION
    assert queued[0]["payload"] == {"phase": "31", "tasks_done": 7}
    assert queued[0]["timestamp"]  # timestamp populated


def test_env_endpoint_enables_and_falls_back_to_queue(tmp_path, monkeypatch):
    # Unreachable endpoint via env var — enables telemetry, POST fails, queue.
    monkeypatch.setenv(ENDPOINT_ENV_VAR, "http://127.0.0.1:9/none")
    # No manifest block, but env var alone turns telemetry on.
    assert is_enabled(tmp_path) is True

    emit(tmp_path, make_suggest_accept_event("SUG-20260625-001", "pick-up"))
    flush()

    queued = _read_queue(tmp_path)
    assert len(queued) == 1
    assert queued[0]["event_type"] == EVENT_SUGGEST_ACCEPT
    assert queued[0]["payload"]["proposal_id"] == "SUG-20260625-001"


def test_endpoint_post_success_does_not_queue(tmp_path, monkeypatch):
    monkeypatch.delenv(ENDPOINT_ENV_VAR, raising=False)
    _manifest(tmp_path, enabled=True, endpoint="https://pulse.example/ingest")

    posted: list[tuple[str, dict]] = []

    def _fake_post(endpoint, record):
        posted.append((endpoint, record))
        return True

    monkeypatch.setattr(telemetry_service, "_try_post", _fake_post)

    emit(tmp_path, make_task_close_event("TASK-0042", quick=True))
    flush()

    assert len(posted) == 1
    assert posted[0][0] == "https://pulse.example/ingest"
    assert posted[0][1]["event_type"] == EVENT_TASK_CLOSE
    assert posted[0][1]["payload"] == {"task_id": "TASK-0042", "quick": True}
    # Successful POST means no on-disk fallback.
    assert not _queue_path(tmp_path).exists()


def test_endpoint_post_failure_queues(tmp_path, monkeypatch):
    monkeypatch.delenv(ENDPOINT_ENV_VAR, raising=False)
    _manifest(tmp_path, enabled=True, endpoint="https://pulse.example/ingest")

    monkeypatch.setattr(telemetry_service, "_try_post", lambda endpoint, record: False)

    emit(tmp_path, make_workflow_next_stop_event("phase_has_no_tasks", "32"))
    flush()

    queued = _read_queue(tmp_path)
    assert len(queued) == 1
    assert queued[0]["event_type"] == EVENT_WORKFLOW_NEXT_STOP
    assert queued[0]["payload"] == {"stop_reason": "phase_has_no_tasks", "phase": "32"}


def test_env_endpoint_wins_over_manifest_endpoint(tmp_path, monkeypatch):
    monkeypatch.setenv(ENDPOINT_ENV_VAR, "https://env.example/ingest")
    _manifest(tmp_path, enabled=True, endpoint="https://manifest.example/ingest")

    seen: list[str] = []

    def _fake_post(endpoint, record):
        seen.append(endpoint)
        return True

    monkeypatch.setattr(telemetry_service, "_try_post", _fake_post)
    emit(tmp_path, make_phase_close_event("30", 1))
    flush()

    assert seen == ["https://env.example/ingest"]


# ── Never raises ───────────────────────────────────────────────────────────────

def test_emit_never_raises_on_unwritable_root(tmp_path, monkeypatch):
    monkeypatch.delenv(ENDPOINT_ENV_VAR, raising=False)
    _manifest(tmp_path, enabled=True)

    # Force the queue append to blow up — emit must swallow it.
    def _boom(root, record):
        raise OSError("disk full")

    monkeypatch.setattr(telemetry_service, "_append_to_queue", _boom)
    # Must not raise — neither on the caller's thread nor on the dispatch thread.
    emit(tmp_path, make_task_close_event("TASK-0001"))
    flush()


def test_emit_never_raises_when_disabled_and_manifest_broken(tmp_path, monkeypatch):
    monkeypatch.delenv(ENDPOINT_ENV_VAR, raising=False)
    _write(tmp_path / "docs/runtime/docs_manifest.yaml", "key: [\nunclosed\n")
    # Broken manifest → is_enabled falls back to False, emit is a no-op.
    assert is_enabled(tmp_path) is False
    emit(tmp_path, make_phase_close_event("1", 1))
    assert not _queue_path(tmp_path).exists()


# ── Non-blocking: emission never alters caller timing ──────────────────────────

def test_emit_does_not_block_on_slow_endpoint(tmp_path, monkeypatch):
    # Regression for the synchronous-POST timing bug: when telemetry is enabled
    # with a configured endpoint, emit() must return immediately and NOT wait on
    # the network round-trip. A POST that blocks for ~1s must not delay emit().
    monkeypatch.delenv(ENDPOINT_ENV_VAR, raising=False)
    _manifest(tmp_path, enabled=True, endpoint="https://pulse.example/ingest")

    post_started = []

    def _slow_post(endpoint, record):
        post_started.append(True)
        time.sleep(1.0)  # simulate a slow/unreachable endpoint
        return True

    monkeypatch.setattr(telemetry_service, "_try_post", _slow_post)

    start = time.monotonic()
    emit(tmp_path, make_phase_close_event("30", 5))
    elapsed = time.monotonic() - start

    # emit() returns essentially instantly — the slow POST runs off-thread.
    assert elapsed < 0.5, f"emit blocked for {elapsed:.3f}s on a slow endpoint"

    # And the work genuinely happened in the background once we drain it.
    flush()
    assert post_started == [True]


def test_emit_does_not_block_when_queue_write_is_slow(tmp_path, monkeypatch):
    # The on-disk fallback also runs off the caller's thread.
    monkeypatch.delenv(ENDPOINT_ENV_VAR, raising=False)
    _manifest(tmp_path, enabled=True)  # no endpoint → queue path

    def _slow_queue(root, record):
        time.sleep(1.0)

    monkeypatch.setattr(telemetry_service, "_append_to_queue", _slow_queue)

    start = time.monotonic()
    emit(tmp_path, make_task_close_event("TASK-0001"))
    elapsed = time.monotonic() - start

    assert elapsed < 0.5, f"emit blocked for {elapsed:.3f}s on a slow queue write"
    flush()


# ── emit_built guards builder construction (never-raises covers the full path) ──

def test_emit_built_swallows_raising_builder(tmp_path, monkeypatch):
    # Regression: builder construction must be inside the never-raises guard, so
    # a builder that raises does not propagate out of the call site.
    monkeypatch.delenv(ENDPOINT_ENV_VAR, raising=False)
    _manifest(tmp_path, enabled=True)

    def _boom_builder(*args, **kwargs):
        raise ValueError("builder exploded")

    # Must not raise even though the builder raises and telemetry is enabled.
    emit_built(tmp_path, _boom_builder, "x", kind="y")
    flush()
    # Nothing was emitted because the event was never built.
    assert _read_queue(tmp_path) == []


def test_emit_built_emits_built_event(tmp_path, monkeypatch):
    # Happy path: emit_built builds via the passed builder and emits the event.
    monkeypatch.delenv(ENDPOINT_ENV_VAR, raising=False)
    _manifest(tmp_path, enabled=True)

    emit_built(tmp_path, make_task_close_event, "TASK-0099", quick=True)
    flush()

    queued = _read_queue(tmp_path)
    assert len(queued) == 1
    assert queued[0]["event_type"] == EVENT_TASK_CLOSE
    assert queued[0]["payload"] == {"task_id": "TASK-0099", "quick": True}


# ── Event builders are typed + versioned ───────────────────────────────────────

def test_event_builders_are_versioned():
    for event in (
        make_phase_close_event("30", 3),
        make_task_close_event("TASK-0001"),
        make_suggest_accept_event("SUG-1", "new-task"),
        make_workflow_next_stop_event("task_blocked", "30"),
    ):
        assert isinstance(event, TelemetryEvent)
        assert event.version == TELEMETRY_EVENT_VERSION
        assert event.event_type
        assert event.timestamp
