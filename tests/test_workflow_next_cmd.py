"""Tests for `forge workflow next` command."""

import json

from click.testing import CliRunner

from forge.cli import main


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


def test_workflow_next_reports_next_action_for_single_ready_task(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T03 — Add `forge workflow next`\n"
            "- **Status:** ready\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "next"])

    assert result.exit_code == 0, result.output
    assert "workflow next: ok" in result.output
    assert "next_action       task_execute" in result.output
    assert "candidate_tasks" in result.output
    assert "P8-T03 (ready)" in result.output


def test_workflow_next_reports_stop_reason_without_failing(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T03 — Add `forge workflow next`\n"
            "- **Status:** ready\n\n"
            "### P8-T04 — Add `forge task next`\n"
            "- **Status:** ready\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "next"])

    assert result.exit_code == 0, result.output
    assert "workflow next: stopped" in result.output
    assert "stop_reason       conflicting_next_actions" in result.output
    assert "ready task: P8-T03" in result.output
    assert "ready task: P8-T04" in result.output


def test_workflow_next_json_output_includes_evaluation_payload(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T03 — Add `forge workflow next`\n"
            "- **Status:** draft\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "--format", "json", "workflow", "next"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["command"] == "workflow evaluate"
    assert "evaluation" in data
    assert data["evaluation"]["next_action"] == "task_planning"
    assert data["evaluation"]["recommended_prompt"] == "prompts/task.plan.next.md"
