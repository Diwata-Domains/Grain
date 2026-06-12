"""Tests for `forge workflow next` command."""

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
    assert "stop_reason       packet_required" in result.output
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


def test_workflow_next_surfaces_active_task_observability(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T03 — Add `forge workflow next`\n"
            "- **Status:** in_progress\n"
        ),
    )
    packet_dir = tmp_path / "tasks" / "P8-T03-TASK-0001"
    packet_dir.mkdir(parents=True, exist_ok=True)
    _write(
        packet_dir / "task.md",
        (
            "# Task: Workflow next\n\n## Metadata\n"
            "- **ID:** TASK-0001\n"
            "- **Status:** in_progress\n"
            "- **Phase:** Phase 8 — Workflow Automation Runner Foundation\n"
        ),
    )
    _write(packet_dir / "context.md", "# Context\n")
    _write(packet_dir / "plan.md", "# Plan\n")
    _write(packet_dir / "deliverable_spec.md", "# Deliverable\n")
    _write(
        tmp_path / "docs" / "working" / "current_task.md",
        "# Current Task\n\nTask ID: TASK-0001\nTask Path: tasks/P8-T03-TASK-0001/\nStatus: in_progress\n",
    )
    _write(
        packet_dir / "observability.json",
        json.dumps(
            {
                "task_id": "TASK-0001",
                "packet_dir": "tasks/P8-T03-TASK-0001",
                "executor_identity": "codex",
                "model_class": "frontier_model",
                "last_stage": "execute",
                "last_stage_at": "2026-05-06T12:00:00Z",
                "last_workflow_action": "manual_execute",
                "last_workflow_action_at": "2026-05-06T12:00:00Z",
                "started_at": "2026-05-06T11:00:00Z",
                "updated_at": "2026-05-06T12:00:00Z",
                "stage_timestamps": {"execute_at": "2026-05-06T11:00:00Z"},
            },
            indent=2,
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "next"])

    assert result.exit_code == 0, result.output
    assert "observability" in result.output
    assert "executor_identity  codex" in result.output
    assert "last_action        manual_execute" in result.output
