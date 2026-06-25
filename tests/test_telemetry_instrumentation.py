# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Instrumentation tests — the four moments emit telemetry only when enabled.

Each moment (phase close, task close, suggest accept, workflow next stop reason)
must emit a typed, versioned event when telemetry is on, and emit nothing when it
is off (the default). Emission is side-band: it never changes the command's
result or control flow.
"""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main
from grain.domain.telemetry import (
    EVENT_PHASE_CLOSE,
    EVENT_SUGGEST_ACCEPT,
    EVENT_TASK_CLOSE,
    EVENT_WORKFLOW_NEXT_STOP,
)
from grain.services.phase_close_service import close_phase
from grain.services.suggest_service import accept, generate
from grain.services.task_service import create_packet_directory, quick_close_packet


def _write(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _enable_telemetry(tmp_path: Path) -> None:
    _write(
        tmp_path / "docs/runtime/docs_manifest.yaml",
        "version: 1\nproject:\n  name: test\ntelemetry:\n  enabled: true\n  endpoint: \"\"\n",
    )


def _queue(tmp_path: Path) -> list[dict]:
    path = tmp_path / ".grain" / "telemetry_queue.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


# ── Phase close ────────────────────────────────────────────────────────────────

def _seed_phase_repo(tmp_path: Path, phase: str = "15") -> None:
    (tmp_path / "docs/working").mkdir(parents=True, exist_ok=True)
    _write(tmp_path / "docs/working/current_focus.md", f"Phase {phase} — Test Phase\n")
    _write(
        tmp_path / "docs/working/current_task.md",
        "Task ID: none\nTask Path: none\nStatus: unset\n",
    )
    _write(
        tmp_path / "docs/working/backlog.md",
        f"## 1. Phase {phase} — Test Phase\n\n"
        "### P15-T01 — A\n- **Status:** done\n\n"
        "### P15-T02 — B\n- **Status:** done\n\n",
    )


def test_phase_close_emits_when_enabled(tmp_path):
    _seed_phase_repo(tmp_path)
    _enable_telemetry(tmp_path)

    result = close_phase(tmp_path)
    assert result.ok, result.errors  # control flow unchanged

    queued = _queue(tmp_path)
    assert len(queued) == 1
    assert queued[0]["event_type"] == EVENT_PHASE_CLOSE
    assert queued[0]["payload"] == {"phase": "15", "tasks_done": 2}


def test_phase_close_emits_nothing_when_disabled(tmp_path):
    _seed_phase_repo(tmp_path)  # no telemetry manifest → off

    result = close_phase(tmp_path)
    assert result.ok, result.errors

    assert _queue(tmp_path) == []


def test_phase_close_dry_run_does_not_emit(tmp_path):
    _seed_phase_repo(tmp_path)
    _enable_telemetry(tmp_path)

    result = close_phase(tmp_path, dry_run=True)
    assert result.ok, result.errors

    assert _queue(tmp_path) == []


# ── Task close ─────────────────────────────────────────────────────────────────

def test_task_close_emits_when_enabled(packet_repo):
    root = packet_repo
    _enable_telemetry(root)
    create = create_packet_directory(root, phase=3, task_num=1)
    assert create.ok, create.errors

    result = quick_close_packet(root, create.task_id, "done")
    assert result.ok, result.errors
    assert result.status == "done"  # control flow unchanged

    queued = _queue(root)
    assert len(queued) == 1
    assert queued[0]["event_type"] == EVENT_TASK_CLOSE
    assert queued[0]["payload"]["task_id"] == create.task_id


def test_task_close_emits_nothing_when_disabled(packet_repo):
    root = packet_repo  # no telemetry manifest → off
    create = create_packet_directory(root, phase=3, task_num=1)
    assert create.ok, create.errors

    result = quick_close_packet(root, create.task_id, "done")
    assert result.ok, result.errors

    assert _queue(root) == []


# ── Suggest accept ──────────────────────────────────────────────────────────────

def _seed_suggest_repo(root: Path) -> str:
    _write(
        root / "docs/working/current_focus.md",
        "# Current Focus\n\n## Current Phase\nPhase 30 — Build\n",
    )
    _write(
        root / "docs/working/current_task.md",
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: unset\n",
    )
    _write(
        root / "docs/working/backlog.md",
        "# Backlog\n\n## 1. Phase 30 — Build\n\n"
        "### P30-T01 — Build the thing\n- **Status:** ready\n",
    )
    r = generate(root, auto_prune=False)
    return [p for p in r.proposals if p.kind == "pick-up"][0].id


def test_suggest_accept_emits_when_enabled(packet_repo):
    root = packet_repo
    pid = _seed_suggest_repo(root)
    _enable_telemetry(root)

    res = accept(root, pid)
    assert res.ok, res.errors  # control flow unchanged

    queued = _queue(root)
    assert len(queued) == 1
    assert queued[0]["event_type"] == EVENT_SUGGEST_ACCEPT
    assert queued[0]["payload"] == {"proposal_id": pid, "kind": "pick-up"}


def test_suggest_accept_emits_nothing_when_disabled(packet_repo):
    root = packet_repo
    pid = _seed_suggest_repo(root)  # no telemetry manifest → off

    res = accept(root, pid)
    assert res.ok, res.errors

    assert _queue(root) == []


# ── Workflow next stop reason ────────────────────────────────────────────────────

def _seed_stop_reason_repo(tmp_path: Path) -> None:
    # Missing current_task.md fields produce a stop reason via `workflow next`.
    _write(
        tmp_path / "docs/working/current_focus.md",
        "# Current Focus\n\n## Current Phase\nPhase 30 — Build\n",
    )
    _write(
        tmp_path / "docs/working/backlog.md",
        "# Backlog\n\n## 1. Phase 30 — Build\n\n",
    )
    _write(
        tmp_path / "docs/working/current_task.md",
        "Task ID: none\nTask Path: none\nStatus: unset\n",
    )


def test_workflow_next_emits_stop_reason_when_enabled(tmp_path):
    _seed_stop_reason_repo(tmp_path)
    _enable_telemetry(tmp_path)

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "--format", "json", "workflow", "next"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    stop_reason = data["evaluation"]["stop_reason"]
    assert stop_reason  # the command produced a stop reason

    queued = _queue(tmp_path)
    assert len(queued) == 1
    assert queued[0]["event_type"] == EVENT_WORKFLOW_NEXT_STOP
    assert queued[0]["payload"]["stop_reason"] == stop_reason


def test_workflow_next_emits_nothing_when_disabled(tmp_path):
    _seed_stop_reason_repo(tmp_path)  # no telemetry manifest → off

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "next"])
    assert result.exit_code == 0, result.output

    assert _queue(tmp_path) == []
