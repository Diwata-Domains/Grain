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


def _seed_malformed_focus(tmp_path: Path, phase_line: str) -> Path:
    working = tmp_path / "docs" / "working"
    working.mkdir(parents=True, exist_ok=True)
    (working / "current_focus.md").write_text(
        f"# Current Focus\n\n## Current Phase\n{phase_line}\n", encoding="utf-8"
    )
    (working / "current_task.md").write_text(
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: idle\n", encoding="utf-8"
    )
    (working / "backlog.md").write_text(
        "# Backlog\n\n## Phase 1 — Foundation\n\n### P1-T01 — A task\n- **Status:** done\n",
        encoding="utf-8",
    )
    (tmp_path / "tasks").mkdir(exist_ok=True)
    return tmp_path


def test_reconcile_flags_unparseable_current_phase(tmp_path):
    # A hand-edited hyphen separator: the evaluator cannot parse this.
    root = _seed_malformed_focus(tmp_path, "Phase 1 - Foundation")

    result = reconcile(root)

    issues = [i for i in result.issues if i.check == "focus_phase_parseable"]
    assert issues, [i.check for i in result.issues]
    assert issues[0].fix_available


def test_reconcile_fix_normalizes_current_phase_separator(tmp_path):
    root = _seed_malformed_focus(tmp_path, "Phase 1 - Foundation")

    result = reconcile(root, fix=True)

    focus_text = (root / "docs" / "working" / "current_focus.md").read_text(encoding="utf-8")
    assert "Phase 1 — Foundation" in focus_text
    assert any("focus_phase_parseable" in f for f in result.fixed) or any(
        i.check == "focus_phase_parseable" for i in result.issues
    )
    # After the fix, a re-run is clean of this check.
    assert not [i for i in reconcile(root).issues if i.check == "focus_phase_parseable"]


def test_reconcile_clean_when_current_phase_uses_em_dash(tmp_path):
    root = _seed_malformed_focus(tmp_path, "Phase 1 — Foundation")

    result = reconcile(root)

    assert not [i for i in result.issues if i.check == "focus_phase_parseable"]


def test_reconcile_does_not_flag_archived_packets_as_missing(tmp_path):
    # `grain phase close` moves packets to tasks/archive/phase-N/. A closed phase's
    # done tasks are not orphans just because they are no longer under tasks/.
    from grain.services.reconcile_service import reconcile

    working = tmp_path / "docs" / "working"
    working.mkdir(parents=True)
    (working / "current_focus.md").write_text(
        "# Current Focus\n\n## Current Phase\nPhase 3 — Now\n\n"
        "Phase 2 closed: 2026-01-01 — 1 tasks done (grain-verified)\n",
        encoding="utf-8",
    )
    (working / "current_task.md").write_text(
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: idle\n", encoding="utf-8"
    )
    (working / "backlog.md").write_text(
        "# Backlog\n\n## Phase 2 — Sealed\n\n### P2-T01 — Archived work\n- **Status:** done\n\n"
        "## Phase 3 — Now\n\n### P3-T01 — Current\n- **Status:** draft\n",
        encoding="utf-8",
    )
    # Suffixless packet dirs exist in the wild (Phase 34 of grain's own repo).
    archived = tmp_path / "tasks" / "archive" / "phase-2" / "P2-T01"
    archived.mkdir(parents=True)
    (archived / "task.md").write_text(
        "# Task\n\n## Metadata\n- **ID:** TASK-0001\n- **Status:** done\n", encoding="utf-8"
    )

    result = reconcile(tmp_path)

    orphans = [i for i in result.issues if i.check == "missing_packet"]
    assert orphans == [], [i.description for i in orphans]


def test_reconcile_still_flags_a_genuinely_missing_packet(tmp_path):
    from grain.services.reconcile_service import reconcile

    working = tmp_path / "docs" / "working"
    working.mkdir(parents=True)
    (working / "current_focus.md").write_text(
        "# Current Focus\n\n## Current Phase\nPhase 3 — Now\n", encoding="utf-8"
    )
    (working / "current_task.md").write_text(
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: idle\n", encoding="utf-8"
    )
    (working / "backlog.md").write_text(
        "# Backlog\n\n## Phase 3 — Now\n\n### P3-T01 — Claimed done, no packet anywhere\n"
        "- **Status:** done\n",
        encoding="utf-8",
    )
    (tmp_path / "tasks").mkdir()

    result = reconcile(tmp_path)

    orphans = [i for i in result.issues if i.check == "missing_packet"]
    assert len(orphans) == 1
    assert "P3-T01" in orphans[0].description
