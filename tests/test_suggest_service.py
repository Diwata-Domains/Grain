# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Tests for the grain suggest service (engine, proposal I/O, lifecycle)."""

from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from grain.domain.suggest import SuggestionProposal
from grain.services.suggest_service import (
    accept,
    allocate_proposal_id,
    dismiss,
    generate,
    list_existing_proposals,
    parse_proposal_md,
    prune,
    read_proposal,
    render_proposal_md,
    set_proposal_status,
    top_suggestion,
    write_proposal,
)


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


def _backlog(tmp_path: Path, body: str) -> None:
    _write(tmp_path / "docs/working/backlog.md", "# Backlog\n\n" + body)


# ── Proposal id allocation ──────────────────────────────────────────────────────

def test_proposal_id_allocation_empty_and_incrementing(tmp_path):
    today = "20260625"
    assert allocate_proposal_id(tmp_path, today=today) == "SUG-20260625-001"

    p = SuggestionProposal(id="SUG-20260625-001", kind="pick-up", title="x", created_at="2026-06-25")
    write_proposal(tmp_path, p)
    assert allocate_proposal_id(tmp_path, today=today) == "SUG-20260625-002"

    p2 = SuggestionProposal(id="SUG-20260625-002", kind="pick-up", title="y", created_at="2026-06-25")
    write_proposal(tmp_path, p2)
    assert allocate_proposal_id(tmp_path, today=today) == "SUG-20260625-003"
    # Different day restarts the sequence.
    assert allocate_proposal_id(tmp_path, today="20260626") == "SUG-20260626-001"


# ── Round-trip ──────────────────────────────────────────────────────────────────

def test_proposal_md_roundtrip(tmp_path):
    p = SuggestionProposal(
        id="SUG-20260625-001",
        kind="pick-up",
        title="P30-T08 (TASK-0197) — open as current task",
        rationale="Task is ready in Phase 30 (active phase).",
        signal="Ready task in active phase",
        signal_ref="P30-T08",
        status="pending",
        created_at="2026-06-25",
        source_signals=["backlog.md: P30-T08 status = ready"],
        task_ref="P30-T08",
        task_id="TASK-0197",
        phase="Phase 30 — Build",
    )
    text = render_proposal_md(p)
    parsed = parse_proposal_md(text)
    assert parsed is not None
    assert parsed.id == p.id
    assert parsed.kind == p.kind
    assert parsed.status == "pending"
    assert parsed.signal == p.signal
    assert parsed.signal_ref == "P30-T08"
    assert parsed.task_ref == "P30-T08"
    assert parsed.task_id == "TASK-0197"
    assert parsed.phase == "Phase 30 — Build"
    assert parsed.source_signals == ["backlog.md: P30-T08 status = ready"]


def test_set_status_preserves_body(tmp_path):
    p = SuggestionProposal(
        id="SUG-20260625-001", kind="new-task", title="Resolve open question: X",
        objective="Resolve open question: X", signal="open_questions.md (blocking)",
        signal_ref="OQ-1", rationale="Some rationale", created_at="2026-06-25",
        source_signals=["open_questions.md: OQ-1 status = blocking"], suggested_phase="Phase 30 — Build",
    )
    write_proposal(tmp_path, p)
    assert set_proposal_status(tmp_path, p.id, "dismissed") is True

    reread = read_proposal(tmp_path, p.id)
    assert reread.status == "dismissed"
    assert reread.objective == "Resolve open question: X"
    assert reread.rationale == "Some rationale"
    assert reread.source_signals == ["open_questions.md: OQ-1 status = blocking"]


# ── Pick-up quality bar ──────────────────────────────────────────────────────────

def test_pickup_respects_quality_bar(tmp_path):
    _focus(tmp_path)
    _current_task_none(tmp_path)
    _backlog(tmp_path,
             "## 1. Phase 30 — Build\n\n"
             "### P30-T08 — Spec agent enforcement model\n"
             "- **Status:** ready\n"
             "- **TASK-ID:** TASK-0197\n\n"
             "### P30-T09 — Done thing\n"
             "- **Status:** done\n"
             "- **TASK-ID:** TASK-0198\n")

    result = generate(tmp_path)
    pickups = [p for p in result.proposals if p.kind == "pick-up"]
    assert len(pickups) == 1
    assert pickups[0].task_ref == "P30-T08"
    assert pickups[0].task_id == "TASK-0197"
    # File written
    assert any("P30-T08" in s for s in pickups[0].source_signals)
    assert (tmp_path / "docs/working/proposals" / f"{pickups[0].id}.md").exists()


def test_pickup_excludes_inprogress_current_task(tmp_path):
    _focus(tmp_path)
    _write(
        tmp_path / "docs/working/current_task.md",
        "# Current Task\n\nTask ID: TASK-0197\nTask Path: tasks/P30-T08-TASK-0197/\nStatus: in_progress\n",
    )
    _backlog(tmp_path,
             "## 1. Phase 30 — Build\n\n"
             "### P30-T08 — Spec agent enforcement model\n"
             "- **Status:** ready\n"
             "- **TASK-ID:** TASK-0197\n")
    result = generate(tmp_path)
    assert [p for p in result.proposals if p.kind == "pick-up"] == []


def test_pickup_excludes_recently_committed_task(tmp_path, monkeypatch):
    _focus(tmp_path)
    _current_task_none(tmp_path)
    _backlog(tmp_path,
             "## 1. Phase 30 — Build\n\n"
             "### P30-T08 — Recently shipped\n"
             "- **Status:** ready\n"
             "- **TASK-ID:** TASK-0197\n")

    import grain.services.suggest_service as svc
    monkeypatch.setattr(
        svc, "read_recent_commits",
        lambda root, count=3: [{"sha": "abc1234", "subject": "feat(grain): do P30-T08 work", "files": []}],
    )
    result = generate(tmp_path)
    assert [p for p in result.proposals if p.kind == "pick-up"] == []


# ── New-task from signals ────────────────────────────────────────────────────────

def test_newtask_from_blocking_oq_has_signal_ref(tmp_path):
    _focus(tmp_path)
    _current_task_none(tmp_path)
    _backlog(tmp_path, "## 1. Phase 30 — Build\n\n")
    _write(
        tmp_path / "docs/working/open_questions.md",
        "# Open Questions\n\n"
        "### Should we adopt X?\n"
        "- **ID:** OQ-7\n"
        "- **Status:** blocking\n",
    )
    result = generate(tmp_path)
    newtasks = [p for p in result.proposals if p.kind == "new-task"]
    assert len(newtasks) == 1
    assert newtasks[0].signal_ref == "OQ-7"
    assert "Should we adopt X?" in newtasks[0].objective


def test_newtask_from_aging_high_tooling_note(tmp_path):
    _focus(tmp_path)
    _current_task_none(tmp_path)
    _backlog(tmp_path, "## 1. Phase 30 — Build\n\n")
    old = (date.today() - timedelta(days=40)).isoformat()
    _write(
        tmp_path / "docs/working/tooling_notes.md",
        "# Tooling Notes\n\n"
        "| Date | Type | Severity | Command | Message | Status |\n"
        "|------|------|----------|---------|---------|--------|\n"
        f"| {old} | bug | high | grain workflow next | crashes on empty backlog | open |\n",
    )
    result = generate(tmp_path)
    newtasks = [p for p in result.proposals if p.kind == "new-task"]
    assert len(newtasks) == 1
    assert old in newtasks[0].signal_ref
    assert "grain workflow next" in newtasks[0].signal_ref


def test_newtask_dedupe_token_similarity(tmp_path):
    _focus(tmp_path)
    _current_task_none(tmp_path)
    # An existing backlog task that is >=70% token-similar to the derived objective.
    _backlog(tmp_path,
             "## 1. Phase 30 — Build\n\n"
             "### P30-T01 — Resolve open question: Should we adopt X?\n"
             "- **Status:** done\n")
    _write(
        tmp_path / "docs/working/open_questions.md",
        "# Open Questions\n\n"
        "### Should we adopt X?\n"
        "- **ID:** OQ-7\n"
        "- **Status:** blocking\n",
    )
    result = generate(tmp_path)
    assert [p for p in result.proposals if p.kind == "new-task"] == []


# ── Determinism / offline ────────────────────────────────────────────────────────

def test_generation_offline_no_git(tmp_path, monkeypatch):
    _focus(tmp_path)
    _current_task_none(tmp_path)
    _backlog(tmp_path,
             "## 1. Phase 30 — Build\n\n"
             "### P30-T08 — Ready thing\n"
             "- **Status:** ready\n"
             "- **TASK-ID:** TASK-0197\n")
    # Simulate git being absent — the commit reader returns empty.
    import grain.services.suggest_service as svc

    monkeypatch.setattr(svc, "read_recent_commits", lambda root, count=3: [])
    # commit signal simply empty → pick-up still produced
    result = generate(tmp_path)
    assert any(p.kind == "pick-up" for p in result.proposals)


def test_generation_is_deterministic_and_idempotent(tmp_path):
    _focus(tmp_path)
    _current_task_none(tmp_path)
    _backlog(tmp_path,
             "## 1. Phase 30 — Build\n\n"
             "### P30-T08 — Ready thing\n"
             "- **Status:** ready\n"
             "- **TASK-ID:** TASK-0197\n")
    r1 = generate(tmp_path)
    # Second run must not re-create a proposal for the same signal.
    r2 = generate(tmp_path)
    assert len(r1.written) == 1
    assert r2.written == []


# ── Expiry ───────────────────────────────────────────────────────────────────────

def test_expire_pickup_when_task_done(tmp_path):
    _focus(tmp_path)
    _current_task_none(tmp_path)
    _backlog(tmp_path,
             "## 1. Phase 30 — Build\n\n"
             "### P30-T08 — Ready thing\n"
             "- **Status:** ready\n"
             "- **TASK-ID:** TASK-0197\n")
    r1 = generate(tmp_path)
    pid = [p for p in r1.proposals if p.kind == "pick-up"][0].id

    # Task becomes done → next generate should expire the proposal.
    _backlog(tmp_path,
             "## 1. Phase 30 — Build\n\n"
             "### P30-T08 — Ready thing\n"
             "- **Status:** done\n"
             "- **TASK-ID:** TASK-0197\n")
    generate(tmp_path, auto_prune=False)
    assert read_proposal(tmp_path, pid).status == "expired"


def test_expire_newtask_when_oq_resolved(tmp_path):
    _focus(tmp_path)
    _current_task_none(tmp_path)
    _backlog(tmp_path, "## 1. Phase 30 — Build\n\n")
    _write(
        tmp_path / "docs/working/open_questions.md",
        "# Open Questions\n\n### Q?\n- **ID:** OQ-7\n- **Status:** blocking\n",
    )
    r1 = generate(tmp_path)
    pid = [p for p in r1.proposals if p.kind == "new-task"][0].id

    # OQ resolved (moved to Resolved section).
    _write(
        tmp_path / "docs/working/open_questions.md",
        "# Open Questions\n\n## Resolved\n\n### Q?\n- **ID:** OQ-7\n- **Status:** blocking\n",
    )
    generate(tmp_path, auto_prune=False)
    assert read_proposal(tmp_path, pid).status == "expired"


def test_tooling_note_blank_command_not_prematurely_expired(packet_repo):
    """Regression (LOW): a blank Command column must not break the expiry key.

    The generated signal_ref falls back to '<date> tooling' for a blank command;
    _tooling_note_still_open must build the same key so a still-open note is NOT
    reported resolved (which would prematurely expire / clobber-on-accept).
    """
    root = packet_repo
    _focus(root)
    _current_task_none(root)
    _backlog(root, "## 1. Phase 30 — Build\n\n")
    old = (date.today() - timedelta(days=40)).isoformat()
    _write(
        root / "docs/working/tooling_notes.md",
        "# Tooling Notes\n\n"
        "| Date | Type | Severity | Command | Message | Status |\n"
        "|------|------|----------|---------|---------|--------|\n"
        f"| {old} | bug | high |  | something broke | open |\n",
    )
    r = generate(root, auto_prune=False)
    newtasks = [p for p in r.proposals if p.kind == "new-task"]
    assert len(newtasks) == 1
    pid = newtasks[0].id
    assert newtasks[0].signal_ref == f"{old} tooling"

    # The note is still open → re-generation must keep the proposal pending.
    generate(root, auto_prune=False)
    assert read_proposal(root, pid).status == "pending"

    # Accept must act on the still-open note (not expire it).
    res = accept(root, pid, confirmed=True)
    assert res.ok, res.errors
    assert res.expired is False
    assert read_proposal(root, pid).status == "accepted"


# ── Accept / dismiss ─────────────────────────────────────────────────────────────

def test_accept_pickup_opens_task(packet_repo):
    root = packet_repo
    _focus(root)
    _current_task_none(root)
    _backlog(root,
             "## 1. Phase 30 — Build\n\n"
             "### P30-T01 — Build the thing\n"
             "- **Status:** ready\n")
    r = generate(root, auto_prune=False)
    pid = [p for p in r.proposals if p.kind == "pick-up"][0].id

    res = accept(root, pid)
    assert res.ok, res.errors
    # Packet created and activated.
    packets = [d.name for d in (root / "tasks").iterdir() if d.is_dir()]
    assert any(name.startswith("P30-T01-") for name in packets)
    current = (root / "docs/working/current_task.md").read_text()
    assert "Status: in_progress" in current
    assert read_proposal(root, pid).status == "accepted"


def _current_task_active(root: Path, task_id: str, task_path: str) -> None:
    _write(
        root / "docs/working/current_task.md",
        f"# Current Task\n\nTask ID: {task_id}\nTask Path: {task_path}\nStatus: in_progress\n",
    )


def test_accept_pickup_refuses_when_another_task_in_progress(packet_repo):
    """Regression (HIGH): accepting a pick-up must NOT clobber an active task.

    With TASK-9999 already in_progress, accepting the pick-up for a different
    ready task must refuse (needs_confirm) and leave current_task.md / backlog
    untouched instead of silently switching the active task.
    """
    root = packet_repo
    _focus(root)
    _current_task_active(root, "TASK-9999", "tasks/P30-T99-TASK-9999/")
    _backlog(root,
             "## 1. Phase 30 — Build\n\n"
             "### P30-T01 — Build the thing\n"
             "- **Status:** ready\n")
    r = generate(root, auto_prune=False)
    pid = [p for p in r.proposals if p.kind == "pick-up"][0].id

    current_before = (root / "docs/working/current_task.md").read_text()
    backlog_before = (root / "docs/working/backlog.md").read_text()

    res = accept(root, pid)
    assert res.ok is False
    assert res.needs_confirm is True
    assert "TASK-9999" in " ".join(res.errors)
    # Active task pointer and backlog are untouched — no state corruption.
    assert (root / "docs/working/current_task.md").read_text() == current_before
    assert (root / "docs/working/backlog.md").read_text() == backlog_before
    # No packet was created for the refused pick-up.
    assert not any(d.name.startswith("P30-T01-") for d in (root / "tasks").iterdir())
    # Proposal stays pending (not accepted).
    assert read_proposal(root, pid).status == "pending"


def test_accept_pickup_switches_when_confirmed(packet_repo):
    """An explicit confirm allows switching the active task to the pick-up."""
    root = packet_repo
    _focus(root)
    _current_task_active(root, "TASK-9999", "tasks/P30-T99-TASK-9999/")
    _backlog(root,
             "## 1. Phase 30 — Build\n\n"
             "### P30-T01 — Build the thing\n"
             "- **Status:** ready\n")
    r = generate(root, auto_prune=False)
    pid = [p for p in r.proposals if p.kind == "pick-up"][0].id

    res = accept(root, pid, confirmed=True)
    assert res.ok, res.errors
    current = (root / "docs/working/current_task.md").read_text()
    assert "P30-T01-" in current
    assert "TASK-9999" not in current
    assert read_proposal(root, pid).status == "accepted"


def test_accept_newtask_requires_confirm(packet_repo):
    root = packet_repo
    _focus(root)
    _current_task_none(root)
    _backlog(root, "## 1. Phase 30 — Build\n\n")
    _write(
        root / "docs/working/open_questions.md",
        "# Open Questions\n\n### Q?\n- **ID:** OQ-7\n- **Status:** blocking\n",
    )
    r = generate(root, auto_prune=False)
    pid = [p for p in r.proposals if p.kind == "new-task"][0].id

    # Without confirm: no packet created, needs_confirm flagged, preview shown.
    res = accept(root, pid, confirmed=False)
    assert res.ok is False
    assert res.needs_confirm is True
    assert "# Task:" in res.proposed_task_md
    assert read_proposal(root, pid).status == "pending"

    # With confirm: packet created.
    res2 = accept(root, pid, confirmed=True)
    assert res2.ok, res2.errors
    assert res2.task_id
    assert read_proposal(root, pid).status == "accepted"


def test_accept_expired_signal_is_noop(tmp_path):
    _focus(tmp_path)
    _current_task_none(tmp_path)
    _backlog(tmp_path,
             "## 1. Phase 30 — Build\n\n"
             "### P30-T01 — Ready thing\n"
             "- **Status:** ready\n")
    r = generate(tmp_path, auto_prune=False)
    pid = [p for p in r.proposals if p.kind == "pick-up"][0].id

    # The task becomes done before accept — signal resolved.
    _backlog(tmp_path,
             "## 1. Phase 30 — Build\n\n"
             "### P30-T01 — Ready thing\n"
             "- **Status:** done\n")
    res = accept(tmp_path, pid)
    assert res.ok is False
    assert res.expired is True
    assert read_proposal(tmp_path, pid).status == "expired"
    # No packet was created.
    assert not (tmp_path / "tasks").exists() or not any((tmp_path / "tasks").iterdir())


def test_dismiss_suppresses_resurface(tmp_path):
    _focus(tmp_path)
    _current_task_none(tmp_path)
    _backlog(tmp_path,
             "## 1. Phase 30 — Build\n\n"
             "### P30-T01 — Ready thing\n"
             "- **Status:** ready\n")
    r = generate(tmp_path, auto_prune=False)
    pid = [p for p in r.proposals if p.kind == "pick-up"][0].id
    dismiss(tmp_path, pid)
    assert read_proposal(tmp_path, pid).status == "dismissed"

    # Next generate must not re-create a proposal for the same signal.
    r2 = generate(tmp_path, auto_prune=False)
    assert r2.written == []


# ── Prune ────────────────────────────────────────────────────────────────────────

def test_prune_moves_expired_and_old_dismissed(tmp_path):
    proposals_dir = tmp_path / "docs/working/proposals"
    # expired (always eligible)
    p_exp = SuggestionProposal(id="SUG-20260101-001", kind="pick-up", title="x",
                               status="expired", created_at="2026-01-01")
    write_proposal(tmp_path, p_exp)
    # dismissed but recent (not eligible)
    p_recent = SuggestionProposal(id="SUG-20260101-002", kind="pick-up", title="y",
                                  status="dismissed", created_at="2026-01-01")
    write_proposal(tmp_path, p_recent)
    # dismissed and old (eligible)
    p_old = SuggestionProposal(id="SUG-20260101-003", kind="pick-up", title="z",
                               status="dismissed", created_at="2026-01-01")
    write_proposal(tmp_path, p_old)
    old_time = (datetime.now(tz=timezone.utc) - timedelta(days=40)).timestamp()
    os.utime(proposals_dir / "SUG-20260101-003.md", (old_time, old_time))
    # pending (never eligible)
    p_pending = SuggestionProposal(id="SUG-20260101-004", kind="pick-up", title="w",
                                   status="pending", created_at="2026-01-01")
    write_proposal(tmp_path, p_pending)

    result = prune(tmp_path)
    moved_names = {Path(m).name for m in result.moved}
    assert "SUG-20260101-001.md" in moved_names
    assert "SUG-20260101-003.md" in moved_names
    assert "SUG-20260101-002.md" not in moved_names
    assert "SUG-20260101-004.md" not in moved_names
    # Pending stays in working dir.
    assert (proposals_dir / "SUG-20260101-004.md").exists()
    assert (tmp_path / "docs/archive/proposals/SUG-20260101-001.md").exists()


# ── Top suggestion (surface-only) ────────────────────────────────────────────────

def test_top_suggestion_writes_nothing(tmp_path):
    _focus(tmp_path)
    _current_task_none(tmp_path)
    _backlog(tmp_path,
             "## 1. Phase 30 — Build\n\n"
             "### P30-T01 — Ready thing\n"
             "- **Status:** ready\n")
    top = top_suggestion(tmp_path)
    assert top is not None
    assert top.kind == "pick-up"
    assert top.task_ref == "P30-T01"
    # No proposals were persisted.
    assert list_existing_proposals(tmp_path) == []


def test_top_suggestion_suppresses_dismissed_signal(tmp_path):
    """Regression (MEDIUM): top_suggestion must not re-surface a dismissed signal.

    `grain workflow next` uses top_suggestion; after dismissing the only pick-up,
    it must stop surfacing that same signal (the dismiss-not-resurfaced contract).
    """
    _focus(tmp_path)
    _current_task_none(tmp_path)
    _backlog(tmp_path,
             "## 1. Phase 30 — Build\n\n"
             "### P30-T01 — Ready thing\n"
             "- **Status:** ready\n")
    r = generate(tmp_path, auto_prune=False)
    pid = [p for p in r.proposals if p.kind == "pick-up"][0].id

    # Before dismiss, the pick-up is the top suggestion.
    assert top_suggestion(tmp_path).task_ref == "P30-T01"

    dismiss(tmp_path, pid)
    # After dismiss, the same signal must not be surfaced again.
    assert top_suggestion(tmp_path) is None


def test_top_suggestion_suppresses_accepted_signal(tmp_path):
    """An accepted signal must also not be re-surfaced by top_suggestion."""
    _focus(tmp_path)
    _current_task_none(tmp_path)
    _backlog(tmp_path,
             "## 1. Phase 30 — Build\n\n"
             "### P30-T01 — Ready thing\n"
             "- **Status:** ready\n")
    r = generate(tmp_path, auto_prune=False)
    pid = [p for p in r.proposals if p.kind == "pick-up"][0].id
    # Mark the proposal accepted directly (avoid packet machinery).
    set_proposal_status(tmp_path, pid, "accepted")
    assert top_suggestion(tmp_path) is None
