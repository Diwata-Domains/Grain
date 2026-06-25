# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Tests for the Pulse telemetry foundation (domain, service, instrumentation).

Covers the opt-in gate (off by default → no events / no queue file), the queue
fallback when enabled without a reachable endpoint, the endpoint POST path, and
the strict never-raises contract — plus instrumentation of the four moments
(phase close, task close, suggest accept, workflow next stop reason).
"""

from __future__ import annotations

import json
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

    assert seen == ["https://env.example/ingest"]


# ── Never raises ───────────────────────────────────────────────────────────────

def test_emit_never_raises_on_unwritable_root(tmp_path, monkeypatch):
    monkeypatch.delenv(ENDPOINT_ENV_VAR, raising=False)
    _manifest(tmp_path, enabled=True)

    # Force the queue append to blow up — emit must swallow it.
    def _boom(root, record):
        raise OSError("disk full")

    monkeypatch.setattr(telemetry_service, "_append_to_queue", _boom)
    # Must not raise.
    emit(tmp_path, make_task_close_event("TASK-0001"))


def test_emit_never_raises_when_disabled_and_manifest_broken(tmp_path, monkeypatch):
    monkeypatch.delenv(ENDPOINT_ENV_VAR, raising=False)
    _write(tmp_path / "docs/runtime/docs_manifest.yaml", "key: [\nunclosed\n")
    # Broken manifest → is_enabled falls back to False, emit is a no-op.
    assert is_enabled(tmp_path) is False
    emit(tmp_path, make_phase_close_event("1", 1))
    assert not _queue_path(tmp_path).exists()


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
