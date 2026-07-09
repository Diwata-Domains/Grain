# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""P38-T08: per-repo phase-close gate + orphan-packet (missing_packet) detection.

DEFECT A: the phase-close gate was hard-disabled below phase 16 via a module
constant, so every project in phases 1..14 could hand-edit current_focus.md past
an unclosed phase with no gate. The threshold is now per-repo, stamped at
`grain init` as `phase_close_enforced_from: 1`, falling back to 15 when absent.

DEFECT B: reconcile skipped backlog tasks marked done/in_progress that had no
packet directory, so an orphaned status (deleted packet, or a status advanced
ahead of any packet) went unreported. It now surfaces a `missing_packet` warning.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from grain.services.init_service import init_repo
from grain.services.reconcile_service import reconcile
from grain.services.workflow_service import (
    STOP_PREVIOUS_PHASE_NOT_CLOSED,
    _PHASE_CLOSE_MIN_ENFORCED,
    evaluate_workflow_state,
    phase_close_enforced_threshold,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────


def _seed_manifest(root: Path, *, phase_close_enforced_from: int | str | bool | None) -> None:
    """Write a minimal docs_manifest.yaml, optionally stamping the gate key."""
    manifest: dict = {"version": 1, "project": {"name": "T", "type": "cli_tool"}}
    if phase_close_enforced_from is not None:
        manifest["phase_close_enforced_from"] = phase_close_enforced_from
    manifest_path = root / "docs" / "runtime" / "docs_manifest.yaml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(yaml.safe_dump(manifest), encoding="utf-8")


def _seed_phase2_focus(root: Path, *, phase1_closed: bool) -> None:
    """current_focus.md at Phase 2, with or without a `Phase 1 closed:` marker."""
    marker = "\nPhase 1 closed: 2026-01-01 (grain phase close)\n" if phase1_closed else ""
    (root / "docs" / "working").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "working" / "current_focus.md").write_text(
        f"# Current Focus\n\n## Current Phase\nPhase 2 — Second Phase\n{marker}",
        encoding="utf-8",
    )


def _seed_working_docs(root: Path) -> None:
    working = root / "docs" / "working"
    working.mkdir(parents=True, exist_ok=True)
    (working / "backlog.md").write_text(
        "## Phase 1 — Foundation\n\n"
        "### P1-T01 — Starter\n- **Status:** done\n\n"
        "## Phase 2 — Second Phase\n\n"
        "### P2-T01 — Do the thing\n- **Status:** ready\n",
        encoding="utf-8",
    )
    (working / "current_task.md").write_text(
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: idle\n",
        encoding="utf-8",
    )


# ── phase_close_enforced_threshold ────────────────────────────────────────────


def test_threshold_reads_stamped_key(tmp_path: Path):
    _seed_manifest(tmp_path, phase_close_enforced_from=1)
    assert phase_close_enforced_threshold(tmp_path) == 1


def test_threshold_falls_back_when_key_absent(tmp_path: Path):
    _seed_manifest(tmp_path, phase_close_enforced_from=None)
    assert phase_close_enforced_threshold(tmp_path) == _PHASE_CLOSE_MIN_ENFORCED


def test_threshold_falls_back_when_manifest_missing(tmp_path: Path):
    assert phase_close_enforced_threshold(tmp_path) == _PHASE_CLOSE_MIN_ENFORCED


def test_threshold_rejects_bool_and_garbage(tmp_path: Path):
    _seed_manifest(tmp_path, phase_close_enforced_from=True)
    assert phase_close_enforced_threshold(tmp_path) == _PHASE_CLOSE_MIN_ENFORCED
    _seed_manifest(tmp_path, phase_close_enforced_from="not-a-number")
    assert phase_close_enforced_threshold(tmp_path) == _PHASE_CLOSE_MIN_ENFORCED


# ── grain init stamps the gate ────────────────────────────────────────────────


def test_init_stamps_phase_close_enforced_from(tmp_path: Path):
    init_repo(tmp_path)
    manifest_path = tmp_path / "docs" / "runtime" / "docs_manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert manifest["phase_close_enforced_from"] == 1
    # And the reader agrees.
    assert phase_close_enforced_threshold(tmp_path) == 1


# ── DEFECT A: evaluator gate fires below phase 16 for new workspaces ───────────


def test_evaluator_blocks_unclosed_prev_phase_when_enforced_from_1(tmp_path: Path):
    _seed_manifest(tmp_path, phase_close_enforced_from=1)
    _seed_working_docs(tmp_path)
    _seed_phase2_focus(tmp_path, phase1_closed=False)

    _result, evaluation = evaluate_workflow_state(tmp_path)
    assert evaluation is not None
    assert evaluation.stop_reason == STOP_PREVIOUS_PHASE_NOT_CLOSED


def test_evaluator_allows_phase2_when_prev_phase_sealed(tmp_path: Path):
    _seed_manifest(tmp_path, phase_close_enforced_from=1)
    _seed_working_docs(tmp_path)
    _seed_phase2_focus(tmp_path, phase1_closed=True)

    _result, evaluation = evaluate_workflow_state(tmp_path)
    assert evaluation is not None
    assert evaluation.stop_reason != STOP_PREVIOUS_PHASE_NOT_CLOSED


def test_evaluator_grandfathers_phase2_when_key_absent(tmp_path: Path):
    # Legacy workspace: no stamp → fallback 15 → phase 2 not gated.
    _seed_manifest(tmp_path, phase_close_enforced_from=None)
    _seed_working_docs(tmp_path)
    _seed_phase2_focus(tmp_path, phase1_closed=False)

    _result, evaluation = evaluate_workflow_state(tmp_path)
    assert evaluation is not None
    assert evaluation.stop_reason != STOP_PREVIOUS_PHASE_NOT_CLOSED


# ── reconcile phase_close_chain honours the per-repo threshold ─────────────────


def test_reconcile_phase_close_chain_fires_when_enforced_from_1(tmp_path: Path):
    _seed_manifest(tmp_path, phase_close_enforced_from=1)
    _seed_working_docs(tmp_path)
    _seed_phase2_focus(tmp_path, phase1_closed=False)

    result = reconcile(tmp_path)
    assert any(i.check == "phase_close_chain" for i in result.issues)


def test_reconcile_phase_close_chain_silent_when_key_absent(tmp_path: Path):
    _seed_manifest(tmp_path, phase_close_enforced_from=None)
    _seed_working_docs(tmp_path)
    _seed_phase2_focus(tmp_path, phase1_closed=False)

    result = reconcile(tmp_path)
    assert not any(i.check == "phase_close_chain" for i in result.issues)


# ── DEFECT B: missing_packet ──────────────────────────────────────────────────


def _seed_backlog_only(root: Path, task_ref: str, status: str) -> None:
    working = root / "docs" / "working"
    working.mkdir(parents=True, exist_ok=True)
    (working / "current_focus.md").write_text(
        "# Current Focus\n\n## Current Phase\nPhase 1 — Foundation\n",
        encoding="utf-8",
    )
    (working / "backlog.md").write_text(
        f"## Phase 1 — Foundation\n\n### {task_ref} — Task\n- **Status:** {status}\n",
        encoding="utf-8",
    )
    (working / "current_task.md").write_text(
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: idle\n",
        encoding="utf-8",
    )


def test_reconcile_reports_missing_packet_for_done_task(tmp_path: Path):
    _seed_backlog_only(tmp_path, "P1-T01", "done")
    result = reconcile(tmp_path)
    missing = [i for i in result.issues if i.check == "missing_packet"]
    assert len(missing) == 1
    assert missing[0].severity == "warning"
    assert missing[0].fix_available is False
    assert "P1-T01" in missing[0].description


def test_reconcile_reports_missing_packet_for_in_progress_task(tmp_path: Path):
    _seed_backlog_only(tmp_path, "P1-T01", "in_progress")
    result = reconcile(tmp_path)
    assert any(i.check == "missing_packet" for i in result.issues)


def test_reconcile_no_missing_packet_for_ready_task(tmp_path: Path):
    _seed_backlog_only(tmp_path, "P1-T01", "ready")
    result = reconcile(tmp_path)
    assert not any(i.check == "missing_packet" for i in result.issues)
