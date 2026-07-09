# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""`grain workflow reconcile` detects phase-level drift, not just packet drift.

Before this check existed, reconcile reported `issues 0` on a workspace where
`grain workflow next` refused to route with `workflow_state_drift`, because
every reconcile check was packet-scoped. The README tells agents to run
reconcile when they hit drift, so the two must agree.
"""

from pathlib import Path

from grain.services.reconcile_service import reconcile


def _seed(tmp_path: Path, *, focus_phase: str, backlog_phases: list[str], ledger: list[str]) -> Path:
    working = tmp_path / "docs" / "working"
    working.mkdir(parents=True, exist_ok=True)

    marker_lines = "\n".join(f"Phase {n} closed: 2026-01-01 — 1 tasks done (grain-verified)" for n in ledger)
    (working / "current_focus.md").write_text(
        f"# Current Focus\n\n## Current Phase\nPhase {focus_phase} — Test Phase\n\n{marker_lines}\n",
        encoding="utf-8",
    )
    (working / "current_task.md").write_text(
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: idle\n", encoding="utf-8"
    )

    blocks = []
    for n in backlog_phases:
        blocks.append(f"## Phase {n} — Test Phase\n\n### P{n}-T01 — A task\n- **Status:** done\n")
    (working / "backlog.md").write_text("# Backlog\n\n" + "\n".join(blocks), encoding="utf-8")

    (tmp_path / "tasks").mkdir(exist_ok=True)
    return tmp_path


def test_reconcile_flags_current_focus_phase_absent_from_backlog(tmp_path):
    # current_focus claims Phase 36; the backlog has no such phase block.
    root = _seed(tmp_path, focus_phase="36", backlog_phases=["34", "35"], ledger=["34", "35"])

    result = reconcile(root)

    assert any(i.check == "phase_consistency" for i in result.issues), [i.check for i in result.issues]
    assert any("36" in i.description for i in result.issues)


def test_reconcile_flags_unsealed_previous_phase(tmp_path):
    # Phase 36 is active but Phase 35 carries no close marker.
    root = _seed(tmp_path, focus_phase="36", backlog_phases=["35", "36"], ledger=["34"])

    result = reconcile(root)

    issues = [i for i in result.issues if i.check == "phase_close_chain"]
    assert issues, [i.check for i in result.issues]
    assert "35" in issues[0].description


def test_reconcile_clean_when_phase_chain_is_sound(tmp_path):
    root = _seed(tmp_path, focus_phase="36", backlog_phases=["35", "36"], ledger=["34", "35"])

    result = reconcile(root)

    assert not [i for i in result.issues if i.check in ("phase_consistency", "phase_close_chain")]


def test_reconcile_skips_phase_close_chain_below_enforced_floor(tmp_path):
    # The evaluator only enforces close markers above phase 15.
    root = _seed(tmp_path, focus_phase="3", backlog_phases=["3"], ledger=[])

    result = reconcile(root)

    assert not [i for i in result.issues if i.check == "phase_close_chain"]
