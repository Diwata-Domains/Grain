"""Tests for `grain workflow explain`."""

import json

from click.testing import CliRunner

from grain.cli import main


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _base_repo(repo):
    _write(repo / "docs" / "runtime" / "PROJECT_RULES.md", "")
    _write(
        repo / "docs" / "working" / "current_focus.md",
        (
            "# Current Focus\n\n## Current Phase\n"
            "Phase 29 — Workflow Compliance Hardening\n\n"
            "Phase 28 closed: 2026-05-07 (grain-verified)\n"
        ),
    )
    _write(
        repo / "docs" / "working" / "current_task.md",
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: unset\n",
    )


def test_workflow_explain_reports_actionable_ready_task(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 32. Phase 29 — Workflow Compliance Hardening\n\n"
            "### P29-T04 — Add operator-facing workflow diagnostics\n"
            "- **Status:** ready\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "explain"])

    assert result.exit_code == 0, result.output
    assert "workflow explain: actionable" in result.output
    assert "A task is ready to execute." in result.output
    assert "grain workflow run" in result.output


def test_workflow_explain_reports_doc_drift_resolution_steps(tmp_path):
    _write(tmp_path / "docs" / "runtime" / "PROJECT_RULES.md", "")
    _write(
        tmp_path / "docs" / "working" / "current_focus.md",
        (
            "# Current Focus\n\n## Current Phase\n"
            "Phase 29 — Workflow Compliance Hardening\n\n"
            "Phase 28 closed: 2026-05-07 (grain-verified)\n"
        ),
    )
    _write(
        tmp_path / "docs" / "working" / "current_task.md",
        "# Current Task\n\nTask ID:\nTask Path:\nStatus:\n",
    )
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 32. Phase 29 — Workflow Compliance Hardening\n\n"
            "### P29-T04 — Add operator-facing workflow diagnostics\n"
            "- **Status:** ready\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "explain"])

    assert result.exit_code == 0, result.output
    assert "workflow explain: blocked" in result.output
    assert "Workflow metadata is incomplete or malformed." in result.output
    assert "grain workflow reconcile --dry-run" in result.output


def test_workflow_explain_json_includes_diagnostic_payload(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 32. Phase 29 — Workflow Compliance Hardening\n\n"
            "### P29-T03 — Reduce runner packet/template drift on activation\n"
            "- **Status:** review\n"
        ),
    )
    packet_dir = tmp_path / "tasks" / "P29-T03-TASK-0001"
    packet_dir.mkdir(parents=True, exist_ok=True)
    _write(
        packet_dir / "task.md",
        (
            "# Task: Runner drift\n\n## Metadata\n"
            "- **ID:** TASK-0001\n"
            "- **Status:** review\n"
            "- **Phase:** Phase 29 — Workflow Compliance Hardening\n"
        ),
    )
    _write(packet_dir / "context.md", "# Context\n")
    _write(packet_dir / "plan.md", "# Plan\n")
    _write(packet_dir / "deliverable_spec.md", "# Deliverable\n")
    _write(
        packet_dir / "results.md",
        (
            "# Results\n\n## User Review\n"
            "- **State:** pending\n"
        ),
    )
    _write(packet_dir / "handoff.md", "# Handoff\n")
    _write(
        tmp_path / "docs" / "working" / "current_task.md",
        "# Current Task\n\nTask ID: TASK-0001\nTask Path: tasks/P29-T03-TASK-0001/\nStatus: review\n",
    )

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "--format", "json", "workflow", "explain"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["diagnostic"]["status"] == "blocked"
    assert data["diagnostic"]["stop_reason"] == "review_close_blocked"
    assert "grain review check --id TASK-0001" in data["diagnostic"]["suggested_commands"]
