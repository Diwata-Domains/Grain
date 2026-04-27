"""Tests for `forge phase next` command."""

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
        "# Current Focus\n\n## Current Phase\nPhase 8 — Workflow Automation Runner Foundation\n",
    )
    _write(
        repo / "docs" / "working" / "current_task.md",
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: unset\n",
    )


def test_phase_next_reports_no_phase_action_when_task_execution_exists(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T05 — Add `forge phase next`\n"
            "- **Status:** ready\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "phase", "next"])

    assert result.exit_code == 0, result.output
    assert "phase_action      no_phase_action" in result.output


def test_phase_next_reports_phase_planning_when_no_ready_task(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T06 — Add `forge task prepare`\n"
            "- **Status:** draft\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "phase", "next"])

    assert result.exit_code == 0, result.output
    assert "phase_action      phase_planning" in result.output
    assert "next_action       task_planning" in result.output


def test_phase_next_reports_phase_review_close_for_phase_boundary(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T01 — Lock minimal workflow automation slice and stop-condition rules\n"
            "- **Status:** done\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "phase", "next"])

    assert result.exit_code == 0, result.output
    assert "phase_action      phase_review_close" in result.output
    assert "stop_reason       phase_boundary_review_close_required" in result.output


def test_phase_next_json_output_includes_phase_payload(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T05 — Add `forge phase next`\n"
            "- **Status:** ready\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "--format", "json", "phase", "next"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["phase_next"]["phase_action"] == "no_phase_action"
    assert data["phase_next"]["active_phase"] == "8"


def test_phase_next_reports_no_action_for_project_complete_state(tmp_path):
    _write(
        tmp_path / "docs" / "runtime" / "PROJECT_RULES.md",
        "",
    )
    _write(
        tmp_path / "docs" / "working" / "current_focus.md",
        "# Current Focus\n\n## Current Phase\nPhase: complete\n",
    )
    _write(
        tmp_path / "docs" / "working" / "current_task.md",
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: idle\n",
    )
    _write(tmp_path / "docs" / "working" / "backlog.md", "# Backlog\n")

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "phase", "next"])

    assert result.exit_code == 0, result.output
    assert "phase_action      no_phase_action" in result.output
    assert "project is marked complete" in result.output
    assert "stop_reason       project_complete" in result.output
