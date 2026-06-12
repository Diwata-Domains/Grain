"""Tests for grain docs audit command and service checks."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main
from grain.services.docs_audit_service import run_audit, AuditFinding


# ── Helpers ────────────────────────────────────────────────────────────────────

def _run(tmp_path: Path, *args: str, fmt: str = "text"):
    runner = CliRunner()
    cmd = ["--repo", str(tmp_path)]
    if fmt == "json":
        cmd += ["--format", "json"]
    cmd += list(args)
    return runner.invoke(main, cmd)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _base(tmp_path: Path) -> None:
    """Write the minimum required files for a valid workspace."""
    _write(tmp_path / "docs/working/current_task.md",
           "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: unset\n")
    _write(tmp_path / "docs/working/backlog.md",
           "# Backlog\n\n## 1. Purpose\n\nTest backlog.\n\n"
           "## 2. Phase 1 — Foundation\n\n### P1-T01 — A task\n- **Status:** done\n")
    _write(tmp_path / "docs/working/current_focus.md",
           "# Current Focus\n\n## Current Phase\nPhase 1 — Foundation\n")
    _write(tmp_path / "docs/runtime/docs_manifest.yaml",
           "version: 1\nproject:\n  name: Test\ncanonical: []\nworking: []\nruntime: []\n")


def _days_ago(n: int) -> str:
    return (datetime.now(tz=timezone.utc) - timedelta(days=n)).strftime("%Y-%m-%d")


def _check_ids(findings: list[AuditFinding]) -> set[str]:
    return {f.check_id for f in findings}


def _failing(findings: list[AuditFinding]) -> list[AuditFinding]:
    return [f for f in findings if f.severity != "pass"]


# ── current_task_stale_pointer ─────────────────────────────────────────────────

def test_current_task_stale_pointer_pass_when_in_progress(tmp_path):
    _base(tmp_path)
    packet_dir = tmp_path / "tasks" / "P1-T01-TASK-0001"
    packet_dir.mkdir(parents=True)
    _write(packet_dir / "task.md",
           "# Task\n\n## Metadata\n- **ID:** TASK-0001\n- **Status:** in_progress\n")
    _write(tmp_path / "docs/working/current_task.md",
           "# Current Task\n\nTask ID: TASK-0001\nTask Path: tasks/P1-T01-TASK-0001/\nStatus: in_progress\n")

    result = run_audit(tmp_path, doc_filter="current_task")
    findings = [f for f in result.findings if f.check_id == "current_task_stale_pointer"]
    assert all(f.severity == "pass" for f in findings)


def test_current_task_stale_pointer_fail_when_done(tmp_path):
    _base(tmp_path)
    packet_dir = tmp_path / "tasks" / "P1-T01-TASK-0001"
    packet_dir.mkdir(parents=True)
    _write(packet_dir / "task.md",
           "# Task\n\n## Metadata\n- **ID:** TASK-0001\n- **Status:** done\n")
    _write(tmp_path / "docs/working/current_task.md",
           "# Current Task\n\nTask ID: TASK-0001\nTask Path: tasks/P1-T01-TASK-0001/\nStatus: in_progress\n")

    result = run_audit(tmp_path, doc_filter="current_task")
    errors = [f for f in result.findings if f.check_id == "current_task_stale_pointer" and f.severity == "error"]
    assert errors


# ── current_task_missing_packet ────────────────────────────────────────────────

def test_current_task_missing_packet_pass_when_packet_exists(tmp_path):
    _base(tmp_path)
    packet_dir = tmp_path / "tasks" / "P1-T01-TASK-0001"
    packet_dir.mkdir(parents=True)
    _write(packet_dir / "task.md",
           "# Task\n\n## Metadata\n- **ID:** TASK-0001\n- **Status:** in_progress\n")
    _write(tmp_path / "docs/working/current_task.md",
           "# Current Task\n\nTask ID: TASK-0001\nTask Path: tasks/P1-T01-TASK-0001/\nStatus: in_progress\n")

    result = run_audit(tmp_path, doc_filter="current_task")
    findings = [f for f in result.findings if f.check_id == "current_task_missing_packet"]
    assert all(f.severity == "pass" for f in findings)


def test_current_task_missing_packet_fail_when_dir_absent(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/working/current_task.md",
           "# Current Task\n\nTask ID: TASK-9999\nTask Path: tasks/P1-T01-TASK-9999/\nStatus: in_progress\n")

    result = run_audit(tmp_path, doc_filter="current_task")
    errors = [f for f in result.findings if f.check_id == "current_task_missing_packet" and f.severity == "error"]
    assert errors


# ── current_task_idle ─────────────────────────────────────────────────────────

def test_current_task_idle_pass_when_task_active(tmp_path):
    _base(tmp_path)
    packet_dir = tmp_path / "tasks" / "P1-T01-TASK-0001"
    packet_dir.mkdir(parents=True)
    _write(packet_dir / "task.md",
           "# Task\n\n## Metadata\n- **ID:** TASK-0001\n- **Status:** in_progress\n")
    _write(tmp_path / "docs/working/current_task.md",
           "# Current Task\n\nTask ID: TASK-0001\nTask Path: tasks/P1-T01-TASK-0001/\nStatus: in_progress\n")

    result = run_audit(tmp_path, doc_filter="current_task")
    findings = [f for f in result.findings if f.check_id == "current_task_idle"]
    assert all(f.severity == "pass" for f in findings)


def test_current_task_idle_pass_when_recently_updated(tmp_path):
    _base(tmp_path)
    # File was just written — less than 14 days ago
    result = run_audit(tmp_path, doc_filter="current_task")
    findings = [f for f in result.findings if f.check_id == "current_task_idle"]
    # Recently created file should pass regardless of N
    assert any(f.severity == "pass" for f in findings)


# ── backlog_inprogress_no_packet ───────────────────────────────────────────────

def test_backlog_inprogress_no_packet_pass_when_packet_open(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/working/backlog.md",
           "# Backlog\n\n## 2. Phase 1 — Foundation\n\n"
           "### P1-T01 — Task\n- **Status:** in_progress\n- **TASK-ID:** TASK-0001\n")
    packet_dir = tmp_path / "tasks" / "P1-T01-TASK-0001"
    packet_dir.mkdir(parents=True)
    _write(packet_dir / "task.md",
           "# Task\n\n## Metadata\n- **ID:** TASK-0001\n- **Status:** in_progress\n")

    result = run_audit(tmp_path, doc_filter="backlog")
    findings = [f for f in result.findings if f.check_id == "backlog_inprogress_no_packet"]
    assert all(f.severity == "pass" for f in findings)


def test_backlog_inprogress_no_packet_fail_when_no_packet(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/working/backlog.md",
           "# Backlog\n\n## 2. Phase 1 — Foundation\n\n"
           "### P1-T01 — Task\n- **Status:** in_progress\n- **TASK-ID:** TASK-0001\n")
    # No packet directory

    result = run_audit(tmp_path, doc_filter="backlog")
    errors = [f for f in result.findings if f.check_id == "backlog_inprogress_no_packet" and f.severity == "error"]
    assert errors


# ── backlog_done_no_results ────────────────────────────────────────────────────

def test_backlog_done_no_results_pass_when_results_exist(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/working/backlog.md",
           "# Backlog\n\n## 2. Phase 1 — Foundation\n\n"
           "### P1-T01 — Task\n- **Status:** done\n- **TASK-ID:** TASK-0001\n")
    packet_dir = tmp_path / "tasks" / "P1-T01-TASK-0001"
    packet_dir.mkdir(parents=True)
    _write(packet_dir / "results.md", "# Results\nAll done.\n")

    result = run_audit(tmp_path, doc_filter="backlog")
    findings = [f for f in result.findings if f.check_id == "backlog_done_no_results"]
    assert all(f.severity == "pass" for f in findings)


def test_backlog_done_no_results_warn_when_no_results(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/working/backlog.md",
           "# Backlog\n\n## 2. Phase 1 — Foundation\n\n"
           "### P1-T01 — Task\n- **Status:** done\n- **TASK-ID:** TASK-0001\n")
    packet_dir = tmp_path / "tasks" / "P1-T01-TASK-0001"
    packet_dir.mkdir(parents=True)
    # No results.md

    result = run_audit(tmp_path, doc_filter="backlog")
    warns = [f for f in result.findings if f.check_id == "backlog_done_no_results" and f.severity == "warning"]
    assert warns


# ── backlog_phase_status_drift ─────────────────────────────────────────────────

def test_backlog_phase_drift_pass_when_not_all_done(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/working/backlog.md",
           "# Backlog\n\n## 2. Phase 1 — Foundation\n\n> **Status:** in_progress\n\n"
           "### P1-T01 — Task\n- **Status:** done\n"
           "### P1-T02 — Task 2\n- **Status:** ready\n")

    result = run_audit(tmp_path, doc_filter="backlog")
    findings = [f for f in result.findings if f.check_id == "backlog_phase_status_drift"]
    assert all(f.severity == "pass" for f in findings)


def test_backlog_phase_drift_warn_when_all_done(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/working/backlog.md",
           "# Backlog\n\n## 2. Phase 1 — Foundation\n\n> **Status:** in_progress\n\n"
           "### P1-T01 — Task\n- **Status:** done\n"
           "### P1-T02 — Task 2\n- **Status:** done\n")

    result = run_audit(tmp_path, doc_filter="backlog")
    warns = [f for f in result.findings if f.check_id == "backlog_phase_status_drift" and f.severity == "warning"]
    assert warns


# ── backlog_phase_closed_with_open_tasks ──────────────────────────────────────

def test_backlog_closed_phase_pass_when_all_done(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/working/backlog.md",
           "# Backlog\n\n## 2. Phase 1 — Foundation ✓ CLOSED\n\n"
           "### P1-T01 — Task\n- **Status:** done\n")

    result = run_audit(tmp_path, doc_filter="backlog")
    findings = [f for f in result.findings if f.check_id == "backlog_phase_closed_with_open_tasks"]
    assert all(f.severity == "pass" for f in findings)


def test_backlog_closed_phase_error_with_open_tasks(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/working/backlog.md",
           "# Backlog\n\n## 2. Phase 1 — Foundation ✓ CLOSED\n\n"
           "### P1-T01 — Task\n- **Status:** done\n"
           "### P1-T02 — Task 2\n- **Status:** ready\n")

    result = run_audit(tmp_path, doc_filter="backlog")
    errors = [f for f in result.findings if f.check_id == "backlog_phase_closed_with_open_tasks" and f.severity == "error"]
    assert errors


# ── current_focus_phase_mismatch ──────────────────────────────────────────────

def test_current_focus_phase_mismatch_pass_when_found(tmp_path):
    _base(tmp_path)
    # _base already writes current_focus pointing to Phase 1 which is in backlog

    result = run_audit(tmp_path, doc_filter="current_focus")
    findings = [f for f in result.findings if f.check_id == "current_focus_phase_mismatch"]
    assert any(f.severity == "pass" for f in findings)


def test_current_focus_phase_mismatch_warn_when_not_found(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/working/current_focus.md",
           "# Current Focus\n\n## Current Phase\nPhase 99 — Nonexistent\n")

    result = run_audit(tmp_path, doc_filter="current_focus")
    warns = [f for f in result.findings if f.check_id == "current_focus_phase_mismatch" and f.severity == "warning"]
    assert warns


# ── current_focus_stale ───────────────────────────────────────────────────────

def test_current_focus_stale_pass_when_recent(tmp_path):
    _base(tmp_path)
    # File was just created

    from grain.services.docs_audit_service import AuditConfig
    config = AuditConfig(current_focus_stale_days=30)
    from grain.services.docs_audit_service import _check_current_focus
    findings = _check_current_focus(tmp_path, config)
    stale = [f for f in findings if f.check_id == "current_focus_stale"]
    assert any(f.severity == "pass" for f in stale)


def test_current_focus_stale_disabled_when_zero(tmp_path):
    _base(tmp_path)

    from grain.services.docs_audit_service import AuditConfig, _check_current_focus
    config = AuditConfig(current_focus_stale_days=0)
    findings = _check_current_focus(tmp_path, config)
    stale = [f for f in findings if f.check_id == "current_focus_stale"]
    assert not stale


# ── current_focus_priorities_done ─────────────────────────────────────────────

def test_current_focus_priorities_done_pass_when_some_active(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/working/current_focus.md",
           "# Current Focus\n\n## Current Phase\nPhase 1 — Foundation\n\n"
           "## Immediate Priorities\n1. P1-T01 first task\n2. P1-T02 second task\n")
    _write(tmp_path / "docs/working/backlog.md",
           "# Backlog\n\n## 2. Phase 1 — Foundation\n\n"
           "### P1-T01 — First\n- **Status:** done\n"
           "### P1-T02 — Second\n- **Status:** ready\n")

    result = run_audit(tmp_path, doc_filter="current_focus")
    findings = [f for f in result.findings if f.check_id == "current_focus_priorities_done"]
    assert any(f.severity == "pass" for f in findings)


def test_current_focus_priorities_done_warn_when_all_done(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/working/current_focus.md",
           "# Current Focus\n\n## Current Phase\nPhase 1 — Foundation\n\n"
           "## Immediate Priorities\n1. P1-T01 first task\n2. P1-T02 second task\n")
    _write(tmp_path / "docs/working/backlog.md",
           "# Backlog\n\n## 2. Phase 1 — Foundation\n\n"
           "### P1-T01 — First\n- **Status:** done\n"
           "### P1-T02 — Second\n- **Status:** done\n")

    result = run_audit(tmp_path, doc_filter="current_focus")
    warns = [f for f in result.findings if f.check_id == "current_focus_priorities_done" and f.severity == "warning"]
    assert warns


# ── oq_blocking_accumulation ──────────────────────────────────────────────────

def test_oq_blocking_pass_within_threshold(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/working/open_questions.md",
           "# Open Questions\n\n"
           "### OQ-001 — Question\n- **Status:** blocking\n- **Raised:** 2026-01-01\n\n"
           "## Resolved Questions\n")

    result = run_audit(tmp_path, doc_filter="open_questions")
    findings = [f for f in result.findings if f.check_id == "oq_blocking_accumulation"]
    assert any(f.severity == "pass" for f in findings)


def test_oq_blocking_warn_over_threshold(tmp_path):
    _base(tmp_path)
    entries = "\n".join(
        f"### OQ-{i:03d} — Q{i}\n- **Status:** blocking\n- **Raised:** 2026-01-01\n"
        for i in range(1, 6)
    )
    _write(tmp_path / "docs/working/open_questions.md",
           f"# Open Questions\n\n{entries}\n\n## Resolved Questions\n")

    result = run_audit(tmp_path, doc_filter="open_questions")
    warns = [f for f in result.findings if f.check_id == "oq_blocking_accumulation" and f.severity == "warning"]
    assert warns


# ── oq_stale_open ─────────────────────────────────────────────────────────────

def test_oq_stale_open_pass_when_recent(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/working/open_questions.md",
           f"# Open Questions\n\n### OQ-001 — Recent\n"
           f"- **Status:** open\n- **Raised:** {_days_ago(5)}\n\n## Resolved Questions\n")

    result = run_audit(tmp_path, doc_filter="open_questions")
    findings = [f for f in result.findings if f.check_id == "oq_stale_open"]
    assert any(f.severity == "pass" for f in findings)


def test_oq_stale_open_warn_when_old(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/working/open_questions.md",
           f"# Open Questions\n\n### OQ-001 — Old one\n"
           f"- **Status:** open\n- **Raised:** {_days_ago(90)}\n\n## Resolved Questions\n")

    result = run_audit(tmp_path, doc_filter="open_questions")
    warns = [f for f in result.findings if f.check_id == "oq_stale_open" and f.severity == "warning"]
    assert warns


# ── tooling_notes_high_severity_aging ─────────────────────────────────────────

def test_tooling_notes_aging_pass_when_recent(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/working/tooling_notes.md",
           f"# Tooling Notes\n\n| Date | Type | Command | Observation | Severity | Status |\n"
           f"|------|------|---------|-------------|----------|--------|\n"
           f"| {_days_ago(1)} | bug | grain | Something | high | open |\n")

    result = run_audit(tmp_path, doc_filter="tooling_notes")
    findings = [f for f in result.findings if f.check_id == "tooling_notes_high_severity_aging"]
    assert any(f.severity == "pass" for f in findings)


def test_tooling_notes_aging_warn_when_old(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/working/tooling_notes.md",
           f"# Tooling Notes\n\n| Date | Type | Command | Observation | Severity | Status |\n"
           f"|------|------|---------|-------------|----------|--------|\n"
           f"| {_days_ago(30)} | bug | grain | Old issue | high | open |\n")

    result = run_audit(tmp_path, doc_filter="tooling_notes")
    warns = [f for f in result.findings if f.check_id == "tooling_notes_high_severity_aging" and f.severity == "warning"]
    assert warns


# ── tooling_notes_overdue_triage ──────────────────────────────────────────────

def test_tooling_notes_triage_pass_within_threshold(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/working/tooling_notes.md",
           "# Tooling Notes\n\n| Date | Type | Command | Observation | Severity | Status |\n"
           "|------|------|---------|-------------|----------|--------|\n"
           + "".join(f"| 2026-01-{i:02d} | bug | grain | Note {i} | low | open |\n" for i in range(1, 4)))

    result = run_audit(tmp_path, doc_filter="tooling_notes")
    findings = [f for f in result.findings if f.check_id == "tooling_notes_overdue_triage"]
    assert any(f.severity == "pass" for f in findings)


def test_tooling_notes_triage_warn_over_threshold(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/working/tooling_notes.md",
           "# Tooling Notes\n\n| Date | Type | Command | Observation | Severity | Status |\n"
           "|------|------|---------|-------------|----------|--------|\n"
           + "".join(f"| 2026-01-{i:02d} | bug | grain | Note {i} | low | open |\n" for i in range(1, 10)))

    result = run_audit(tmp_path, doc_filter="tooling_notes")
    warns = [f for f in result.findings if f.check_id == "tooling_notes_overdue_triage" and f.severity == "warning"]
    assert warns


# ── proposal_aging ────────────────────────────────────────────────────────────

def test_proposal_aging_pass_when_recent(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/working/change_proposals.md",
           f"# Change Proposals\n\n## Active Proposals\n\n"
           f"### CP-001 — A proposal\n- **Status:** proposed\n- **Raised:** {_days_ago(5)}\n")

    result = run_audit(tmp_path, doc_filter="change_proposals")
    findings = [f for f in result.findings if f.check_id == "proposal_aging"]
    assert any(f.severity == "pass" for f in findings)


def test_proposal_aging_warn_when_old(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/working/change_proposals.md",
           f"# Change Proposals\n\n## Active Proposals\n\n"
           f"### CP-001 — An old proposal\n- **Status:** proposed\n- **Raised:** {_days_ago(60)}\n")

    result = run_audit(tmp_path, doc_filter="change_proposals")
    warns = [f for f in result.findings if f.check_id == "proposal_aging" and f.severity == "warning"]
    assert warns


# ── registered_doc_missing ────────────────────────────────────────────────────

def test_registered_doc_missing_pass_when_present(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/runtime/docs_manifest.yaml",
           "version: 1\nproject:\n  name: Test\n"
           "canonical:\n  - id: product_scope\n    path: docs/canonical/product_scope.md\n"
           "    purpose: scope\n    authority: highest\n    editable_by_agents: false\n    read_when: []\n"
           "working: []\nruntime: []\n")
    _write(tmp_path / "docs/canonical/product_scope.md", "# Product Scope\n\nSome real content here.\n")

    result = run_audit(tmp_path, doc_filter="structural")
    findings = [f for f in result.findings if f.check_id == "registered_doc_missing"]
    assert any(f.severity == "pass" for f in findings)


def test_registered_doc_missing_error_when_absent(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/runtime/docs_manifest.yaml",
           "version: 1\nproject:\n  name: Test\n"
           "canonical:\n  - id: product_scope\n    path: docs/canonical/product_scope.md\n"
           "    purpose: scope\n    authority: highest\n    editable_by_agents: false\n    read_when: []\n"
           "working: []\nruntime: []\n")
    # product_scope.md is NOT written

    result = run_audit(tmp_path, doc_filter="structural")
    errors = [f for f in result.findings if f.check_id == "registered_doc_missing" and f.severity == "error"]
    assert errors


# ── registered_doc_empty ──────────────────────────────────────────────────────

def test_registered_doc_empty_pass_when_has_content(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/runtime/docs_manifest.yaml",
           "version: 1\nproject:\n  name: Test\n"
           "canonical:\n  - id: product_scope\n    path: docs/canonical/product_scope.md\n"
           "    purpose: scope\n    authority: highest\n    editable_by_agents: false\n    read_when: []\n"
           "working: []\nruntime: []\n")
    _write(tmp_path / "docs/canonical/product_scope.md",
           "# Product Scope\n\nThis project builds a CLI tool for workflow management.\n")

    result = run_audit(tmp_path, doc_filter="structural")
    findings = [f for f in result.findings if f.check_id == "registered_doc_empty"]
    assert any(f.severity == "pass" for f in findings)


def test_registered_doc_empty_warn_when_heading_only(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/runtime/docs_manifest.yaml",
           "version: 1\nproject:\n  name: Test\n"
           "canonical:\n  - id: product_scope\n    path: docs/canonical/product_scope.md\n"
           "    purpose: scope\n    authority: highest\n    editable_by_agents: false\n    read_when: []\n"
           "working: []\nruntime: []\n")
    _write(tmp_path / "docs/canonical/product_scope.md",
           "# Product Scope\n\n## Overview\n\n## Problem Statement\n")

    result = run_audit(tmp_path, doc_filter="structural")
    warns = [f for f in result.findings if f.check_id == "registered_doc_empty" and f.severity == "warning"]
    assert warns


# ── required_section_missing ──────────────────────────────────────────────────

def test_required_section_missing_pass_when_present(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/runtime/docs_manifest.yaml",
           "version: 1\nproject:\n  name: Test\n"
           "canonical:\n  - id: product_scope\n    path: docs/canonical/product_scope.md\n"
           "    purpose: scope\n    authority: highest\n    editable_by_agents: false\n    read_when: []\n"
           "    required_sections: [Overview]\n"
           "working: []\nruntime: []\n")
    _write(tmp_path / "docs/canonical/product_scope.md",
           "# Product Scope\n\n## Overview\n\nContent.\n")

    result = run_audit(tmp_path, doc_filter="structural")
    findings = [f for f in result.findings if f.check_id == "required_section_missing"]
    assert any(f.severity == "pass" for f in findings)


def test_required_section_missing_warn_when_absent(tmp_path):
    _base(tmp_path)
    _write(tmp_path / "docs/runtime/docs_manifest.yaml",
           "version: 1\nproject:\n  name: Test\n"
           "canonical:\n  - id: product_scope\n    path: docs/canonical/product_scope.md\n"
           "    purpose: scope\n    authority: highest\n    editable_by_agents: false\n    read_when: []\n"
           "    required_sections: [Goals]\n"
           "working: []\nruntime: []\n")
    _write(tmp_path / "docs/canonical/product_scope.md",
           "# Product Scope\n\n## Overview\n\nContent.\n")

    result = run_audit(tmp_path, doc_filter="structural")
    warns = [f for f in result.findings if f.check_id == "required_section_missing" and f.severity == "warning"]
    assert warns


# ── CLI integration tests ──────────────────────────────────────────────────────

def test_audit_cmd_text_output_format(tmp_path):
    _base(tmp_path)
    result = _run(tmp_path, "docs", "audit")
    assert result.exit_code == 0
    assert "grain docs audit" in result.output
    assert "Checks:" in result.output


def test_audit_cmd_json_output_has_contract_fields(tmp_path):
    _base(tmp_path)
    result = _run(tmp_path, "docs", "audit", fmt="json")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "run_at" in data
    assert "summary" in data
    assert "overall" in data
    assert "findings" in data
    assert isinstance(data["findings"], list)


def test_audit_cmd_doc_filter(tmp_path):
    _base(tmp_path)
    result = _run(tmp_path, "docs", "audit", "--doc", "current_task")
    assert result.exit_code == 0
    assert "current_task" in result.output


def test_audit_cmd_severity_filter_high(tmp_path):
    _base(tmp_path)
    result = _run(tmp_path, "docs", "audit", "--severity", "high", fmt="json")
    assert result.exit_code == 0
    data = json.loads(result.output)
    # All findings in output should be error-level only
    for f in data["findings"]:
        assert f["severity"] == "error"


def test_audit_cmd_writes_cache_file(tmp_path):
    _base(tmp_path)
    _run(tmp_path, "docs", "audit")
    cache = tmp_path / ".grain" / "last_docs_audit.json"
    assert cache.exists()
    data = json.loads(cache.read_text(encoding="utf-8"))
    assert "run_at" in data
    assert "overall" in data
