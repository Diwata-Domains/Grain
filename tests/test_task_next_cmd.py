"""Tests for `forge task next` command."""

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


def test_task_next_reports_ready_candidate(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T04 — Add `forge task next`\n"
            "- **Status:** ready\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "task", "next"])

    assert result.exit_code == 0, result.output
    assert "task next: ok" in result.output
    assert "next_task         P8-T04" in result.output
    assert "next_action       task_execute" in result.output


def test_task_next_reports_planning_required_when_no_ready_task(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T05 — Add `forge phase next`\n"
            "- **Status:** draft\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "task", "next"])

    assert result.exit_code == 0, result.output
    assert "task next: planning_required" in result.output
    assert "recommended_prompt  prompts/task.plan.next.md" in result.output


def test_task_next_json_output_includes_selection_payload(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T04 — Add `forge task next`\n"
            "- **Status:** ready\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "--format", "json", "task", "next"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["task_next"]["next_task"] == "P8-T04"
    assert data["task_next"]["planning_required"] is False
