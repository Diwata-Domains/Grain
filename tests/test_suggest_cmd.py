# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Tests for the grain suggest command group (text + JSON)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main
from grain.domain.suggest import SuggestionProposal
from grain.services.suggest_service import read_proposal, write_proposal


def _run(tmp_path: Path, *args: str, fmt: str = "text", input: str | None = None):
    runner = CliRunner()
    cmd = ["--repo", str(tmp_path)]
    if fmt == "json":
        cmd += ["--format", "json"]
    cmd += list(args)
    return runner.invoke(main, cmd, input=input)


def _write(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _focus(tmp_path: Path, phase: int = 30) -> None:
    _write(
        tmp_path / "docs/working/current_focus.md",
        f"# Current Focus\n\n## Current Phase\nPhase {phase} — Build\n",
    )


def _current_task_none(tmp_path: Path) -> None:
    _write(
        tmp_path / "docs/working/current_task.md",
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: unset\n",
    )


def _ready_backlog(tmp_path: Path) -> None:
    _write(
        tmp_path / "docs/working/backlog.md",
        "# Backlog\n\n## 1. Phase 30 — Build\n\n"
        "### P30-T01 — Build the thing\n"
        "- **Status:** ready\n",
    )


# ── generate (group default) ─────────────────────────────────────────────────────

def test_generate_writes_proposals_text(tmp_path):
    _focus(tmp_path)
    _current_task_none(tmp_path)
    _ready_backlog(tmp_path)

    result = _run(tmp_path, "suggest")
    assert result.exit_code == 0, result.output
    assert "grain suggest —" in result.output
    assert "SUGGESTION SUG-" in result.output
    assert "pick-up" in result.output
    assert "P30-T01" in result.output
    assert "grain suggest accept" in result.output
    # File persisted.
    proposals = list((tmp_path / "docs/working/proposals").glob("SUG-*.md"))
    assert len(proposals) == 1


def test_generate_json_shape(tmp_path):
    _focus(tmp_path)
    _current_task_none(tmp_path)
    _ready_backlog(tmp_path)

    result = _run(tmp_path, "suggest", fmt="json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert isinstance(data["proposals"], list)
    assert len(data["proposals"]) == 1
    p = data["proposals"][0]
    assert p["kind"] == "pick-up"
    assert p["task_ref"] == "P30-T01"
    assert p["id"].startswith("SUG-")
    assert "written" in data


def test_generate_empty_when_no_signals(tmp_path):
    _focus(tmp_path)
    _current_task_none(tmp_path)
    _write(tmp_path / "docs/working/backlog.md", "# Backlog\n\n## 1. Phase 30 — Build\n\n")
    result = _run(tmp_path, "suggest")
    assert result.exit_code == 0, result.output
    assert "No suggestions" in result.output


# ── list / show ──────────────────────────────────────────────────────────────────

def test_list_and_show(tmp_path):
    _focus(tmp_path)
    _current_task_none(tmp_path)
    _ready_backlog(tmp_path)
    _run(tmp_path, "suggest")  # generate

    list_res = _run(tmp_path, "suggest", "list")
    assert list_res.exit_code == 0, list_res.output
    assert "suggest list:" in list_res.output
    assert "pick-up" in list_res.output

    # JSON list
    list_json = _run(tmp_path, "suggest", "list", fmt="json")
    data = json.loads(list_json.output)
    assert isinstance(data, list) and len(data) == 1
    pid = data[0]["id"]

    show_res = _run(tmp_path, "suggest", "show", pid)
    assert show_res.exit_code == 0, show_res.output
    assert pid in show_res.output
    assert "task_ref   P30-T01" in show_res.output


def test_show_unknown_id_errors(tmp_path):
    result = _run(tmp_path, "suggest", "show", "SUG-20260101-999")
    assert result.exit_code != 0


def test_list_status_filter(tmp_path):
    # Write a dismissed proposal directly.
    p = SuggestionProposal(id="SUG-20260101-001", kind="pick-up", title="x",
                           task_ref="P30-T01", status="dismissed", created_at="2026-01-01")
    write_proposal(tmp_path, p)
    # default (pending) → empty
    res = _run(tmp_path, "suggest", "list")
    assert "empty" in res.output
    # dismissed filter → shows it
    res2 = _run(tmp_path, "suggest", "list", "--status", "dismissed")
    assert "SUG-20260101-001" in res2.output


# ── accept pick-up ───────────────────────────────────────────────────────────────

def test_accept_pickup_opens_task(packet_repo):
    root = packet_repo
    _focus(root)
    _current_task_none(root)
    _ready_backlog(root)
    gen = _run(root, "suggest", fmt="json")
    pid = json.loads(gen.output)["proposals"][0]["id"]

    res = _run(root, "suggest", "accept", pid)
    assert res.exit_code == 0, res.output
    assert "accepted" in res.output
    current = (root / "docs/working/current_task.md").read_text()
    assert "Status: in_progress" in current
    assert read_proposal(root, pid).status == "accepted"


def _current_task_active(root: Path, task_id: str, task_path: str) -> None:
    _write(
        root / "docs/working/current_task.md",
        f"# Current Task\n\nTask ID: {task_id}\nTask Path: {task_path}\nStatus: in_progress\n",
    )


def test_accept_pickup_gate_text_cancel_then_switch(packet_repo):
    """Regression (HIGH): accepting a pick-up while another task is in_progress
    must prompt rather than clobber; 'n' cancels, 'y' switches."""
    root = packet_repo
    _focus(root)
    _current_task_active(root, "TASK-9999", "tasks/P30-T99-TASK-9999/")
    _ready_backlog(root)
    gen = _run(root, "suggest", fmt="json")
    pid = json.loads(gen.output)["proposals"][0]["id"]

    current_before = (root / "docs/working/current_task.md").read_text()

    # Decline the switch → active task unchanged, nothing accepted.
    res = _run(root, "suggest", "accept", pid, input="n\n")
    assert res.exit_code == 0, res.output
    assert "cancelled" in res.output
    assert (root / "docs/working/current_task.md").read_text() == current_before
    assert read_proposal(root, pid).status == "pending"

    # Confirm the switch → active task changes, proposal accepted.
    res2 = _run(root, "suggest", "accept", pid, input="y\n")
    assert res2.exit_code == 0, res2.output
    assert "accepted" in res2.output
    current_after = (root / "docs/working/current_task.md").read_text()
    assert "TASK-9999" not in current_after
    assert "P30-T01-" in current_after
    assert read_proposal(root, pid).status == "accepted"


def test_accept_pickup_gate_no_confirm_switches(packet_repo):
    """--no-confirm auto-confirms switching the active task for a pick-up."""
    root = packet_repo
    _focus(root)
    _current_task_active(root, "TASK-9999", "tasks/P30-T99-TASK-9999/")
    _ready_backlog(root)
    gen = _run(root, "suggest", fmt="json")
    pid = json.loads(gen.output)["proposals"][0]["id"]

    res = _run(root, "suggest", "accept", pid, "--no-confirm")
    assert res.exit_code == 0, res.output
    assert "accepted" in res.output
    assert "TASK-9999" not in (root / "docs/working/current_task.md").read_text()
    assert read_proposal(root, pid).status == "accepted"


def test_accept_pickup_gate_json_refuses_without_clobber(packet_repo):
    """JSON mode refuses the pick-up (needs_confirm, exit 1) without clobbering."""
    root = packet_repo
    _focus(root)
    _current_task_active(root, "TASK-9999", "tasks/P30-T99-TASK-9999/")
    _ready_backlog(root)
    gen = _run(root, "suggest", fmt="json")
    pid = json.loads(gen.output)["proposals"][0]["id"]

    current_before = (root / "docs/working/current_task.md").read_text()
    res = _run(root, "suggest", "accept", pid, fmt="json")
    assert res.exit_code == 1
    data = json.loads(res.output)
    assert data["needs_confirm"] is True
    assert data["ok"] is False
    assert (root / "docs/working/current_task.md").read_text() == current_before
    assert read_proposal(root, pid).status == "pending"


# ── accept new-task requires confirm (D4) ────────────────────────────────────────

def test_accept_newtask_requires_confirm_even_no_confirm(packet_repo):
    root = packet_repo
    _focus(root)
    _current_task_none(root)
    _write(root / "docs/working/backlog.md", "# Backlog\n\n## 1. Phase 30 — Build\n\n")
    _write(
        root / "docs/working/open_questions.md",
        "# Open Questions\n\n### Should we adopt X?\n- **ID:** OQ-7\n- **Status:** blocking\n",
    )
    gen = _run(root, "suggest", fmt="json")
    proposals = json.loads(gen.output)["proposals"]
    pid = [p for p in proposals if p["kind"] == "new-task"][0]["id"]

    # --no-confirm still shows content and still requires the confirm step (D4).
    # Answer "n" → no packet created.
    res = _run(root, "suggest", "accept", pid, "--no-confirm", input="n\n")
    assert res.exit_code == 0, res.output
    assert "confirmation required" in res.output
    assert "# Task:" in res.output
    assert "cancelled" in res.output
    assert read_proposal(root, pid).status == "pending"
    # No new packet was created.
    assert list((root / "tasks").iterdir()) == []

    # Answer "y" → packet created, accepted.
    res2 = _run(root, "suggest", "accept", pid, input="y\n")
    assert res2.exit_code == 0, res2.output
    assert "accepted" in res2.output
    assert read_proposal(root, pid).status == "accepted"
    assert any(d.name.startswith("P30-") for d in (root / "tasks").iterdir())


def test_accept_newtask_json_needs_confirm(packet_repo):
    root = packet_repo
    _focus(root)
    _current_task_none(root)
    _write(root / "docs/working/backlog.md", "# Backlog\n\n## 1. Phase 30 — Build\n\n")
    _write(
        root / "docs/working/open_questions.md",
        "# Open Questions\n\n### Adopt Y?\n- **ID:** OQ-8\n- **Status:** decision_needed\n",
    )
    gen = _run(root, "suggest", fmt="json")
    pid = [p for p in json.loads(gen.output)["proposals"] if p["kind"] == "new-task"][0]["id"]

    res = _run(root, "suggest", "accept", pid, fmt="json")
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)
    assert data["needs_confirm"] is True
    assert data["ok"] is False
    assert "# Task:" in data["proposed_task_md"]


# ── dismiss ──────────────────────────────────────────────────────────────────────

def test_dismiss_suppresses_resurface(tmp_path):
    _focus(tmp_path)
    _current_task_none(tmp_path)
    _ready_backlog(tmp_path)
    gen = _run(tmp_path, "suggest", fmt="json")
    pid = json.loads(gen.output)["proposals"][0]["id"]

    res = _run(tmp_path, "suggest", "dismiss", pid)
    assert res.exit_code == 0, res.output
    assert "dismissed" in res.output
    assert read_proposal(tmp_path, pid).status == "dismissed"

    # Re-generate must not re-surface the same signal.
    gen2 = _run(tmp_path, "suggest", fmt="json")
    assert json.loads(gen2.output)["written"] == []


# ── prune ────────────────────────────────────────────────────────────────────────

def test_prune_moves_expired_and_old_dismissed(tmp_path):
    proposals_dir = tmp_path / "docs/working/proposals"
    p_exp = SuggestionProposal(id="SUG-20260101-001", kind="pick-up", title="x",
                               status="expired", created_at="2026-01-01")
    write_proposal(tmp_path, p_exp)
    p_old = SuggestionProposal(id="SUG-20260101-002", kind="pick-up", title="y",
                               status="dismissed", created_at="2026-01-01")
    write_proposal(tmp_path, p_old)
    old_time = (datetime.now(tz=timezone.utc) - timedelta(days=40)).timestamp()
    os.utime(proposals_dir / "SUG-20260101-002.md", (old_time, old_time))

    res = _run(tmp_path, "suggest", "--prune")
    assert res.exit_code == 0, res.output
    assert "suggest prune: ok" in res.output
    assert not (proposals_dir / "SUG-20260101-001.md").exists()
    assert not (proposals_dir / "SUG-20260101-002.md").exists()
    assert (tmp_path / "docs/archive/proposals/SUG-20260101-001.md").exists()


# ── command registered ───────────────────────────────────────────────────────────

def test_suggest_group_registered():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "suggest" in result.output
