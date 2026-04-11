"""Tests for `forge workflow run` command."""

import json
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _base_repo(repo: Path) -> None:
    _write(repo / "docs" / "runtime" / "PROJECT_RULES.md", "")
    _write(
        repo / "docs" / "working" / "current_focus.md",
        "# Current Focus\n\n## Current Phase\nPhase 8 — Workflow Automation Runner Foundation\n",
    )
    _write(
        repo / "docs" / "working" / "current_task.md",
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: unset\n",
    )


def _ready_backlog(repo: Path, task_ref: str = "P8-T08") -> None:
    _write(
        repo / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            f"### {task_ref} — Example task\n"
            "- **Status:** ready\n"
        ),
    )


def _packet(
    repo: Path,
    task_ref: str,
    task_id: str,
    status: str,
    with_results: bool = False,
    with_handoff: bool = False,
) -> Path:
    dir_name = f"{task_ref}-{task_id}"
    packet_dir = repo / "tasks" / dir_name
    packet_dir.mkdir(parents=True, exist_ok=True)
    _write(
        packet_dir / "task.md",
        (
            "# Task: Example\n\n## Metadata\n"
            f"- **ID:** {task_id}\n"
            f"- **Status:** {status}\n"
            "- **Phase:** Phase 8 — Workflow Automation Runner Foundation\n"
        ),
    )
    _write(packet_dir / "context.md", "# Context\n")
    _write(packet_dir / "plan.md", "# Plan\n")
    _write(packet_dir / "deliverable_spec.md", "# Deliverable\n")
    if with_results:
        _write(packet_dir / "results.md", "# Results\nComplete.\n")
    if with_handoff:
        _write(packet_dir / "handoff.md", "# Handoff\nReady.\n")
    return packet_dir


def _active_task(repo: Path, task_id: str, task_ref: str, status: str) -> None:
    dir_name = f"{task_ref}-{task_id}"
    _write(
        repo / "docs" / "working" / "current_task.md",
        (
            "# Current Task\n\n"
            f"Task ID: {task_id}\n"
            f"Task Path: tasks/{dir_name}/\n"
            f"Status: {status}\n"
        ),
    )


def test_workflow_run_activates_ready_task(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path, "P8-T08")
    _packet(tmp_path, "P8-T08", "TASK-0068", "ready")

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    assert result.exit_code == 0, result.output
    assert "workflow run: ok" in result.output
    assert "action_taken      activate_task" in result.output
    assert "task_activated    TASK-0068" in result.output

    current_task = (tmp_path / "docs" / "working" / "current_task.md").read_text()
    assert "Task ID: TASK-0068" in current_task
    assert "Status: in_progress" in current_task
    assert "tasks/P8-T08-TASK-0068/" in current_task


def test_workflow_run_gates_on_in_progress_task(tmp_path):
    _base_repo(tmp_path)
    _packet(tmp_path, "P8-T08", "TASK-0068", "in_progress")
    _active_task(tmp_path, "TASK-0068", "P8-T08", "in_progress")
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T08 — Example task\n"
            "- **Status:** in_progress\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    assert result.exit_code == 0, result.output
    assert "workflow run: gated" in result.output
    assert "execution_in_flight" in result.output


def test_workflow_run_gates_on_blocked_task(tmp_path):
    _base_repo(tmp_path)
    _packet(tmp_path, "P8-T08", "TASK-0068", "blocked")
    _active_task(tmp_path, "TASK-0068", "P8-T08", "blocked")
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T08 — Example task\n"
            "- **Status:** blocked\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    assert result.exit_code == 0, result.output
    assert "workflow run: gated" in result.output
    assert "task_blocked" in result.output


def test_workflow_run_gates_on_review_ready_packet(tmp_path):
    _base_repo(tmp_path)
    _packet(tmp_path, "P8-T08", "TASK-0068", "review", with_results=True, with_handoff=True)
    _active_task(tmp_path, "TASK-0068", "P8-T08", "review")
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T08 — Example task\n"
            "- **Status:** review\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    assert result.exit_code == 0, result.output
    assert "workflow run: gated" in result.output
    assert "human_review_required" in result.output


def test_workflow_run_gates_on_planning_required(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T08 — Example task\n"
            "- **Status:** draft\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    assert result.exit_code == 0, result.output
    assert "workflow run: gated" in result.output
    assert "planning_required" in result.output


def test_workflow_run_gates_on_phase_boundary(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T01 — Lock minimal workflow automation slice\n"
            "- **Status:** done\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    assert result.exit_code == 0, result.output
    assert "workflow run: gated" in result.output
    assert "phase_boundary" in result.output


def test_workflow_run_gates_on_conflicting_ready_tasks(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T08 — Example task A\n"
            "- **Status:** ready\n\n"
            "### P8-T09 — Example task B\n"
            "- **Status:** ready\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    assert result.exit_code == 0, result.output
    assert "workflow run: gated" in result.output
    assert "ambiguous_next_action" in result.output


def test_workflow_run_json_output_includes_payload(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path, "P8-T08")
    _packet(tmp_path, "P8-T08", "TASK-0068", "ready")

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "--format", "json", "workflow", "run"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["command"] == "workflow run"
    assert "workflow_run" in data
    payload = data["workflow_run"]
    assert payload["action_taken"] == "activate_task"
    assert payload["task_activated"] == "TASK-0068"
    assert payload["gate_reason"] == ""
    assert payload["gate_condition"] == ""
    assert "recommended_prompt" in payload
    assert "active_phase" in payload
    assert "blocking_reasons" in payload
    assert "affected_artifacts" in payload


def test_workflow_run_json_output_gated_shape(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T08 — Example task\n"
            "- **Status:** draft\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "--format", "json", "workflow", "run"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    payload = data["workflow_run"]
    assert payload["action_taken"] == "none"
    assert payload["gate_reason"] == "planning_required"
    assert payload["task_activated"] == ""


def test_workflow_run_fails_when_required_docs_missing(tmp_path):
    # No docs at all — evaluate_workflow_state will return ok=False with stop_reason
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    # Should gate (exit 0) with required_docs_missing, not crash
    assert result.exit_code == 0, result.output
    assert "workflow run: gated" in result.output
    assert "required_docs_missing" in result.output


def test_workflow_run_does_not_mutate_state_on_gate(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T08 — Example task\n"
            "- **Status:** draft\n"
        ),
    )

    original = (tmp_path / "docs" / "working" / "current_task.md").read_text()

    runner = CliRunner()
    runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    after = (tmp_path / "docs" / "working" / "current_task.md").read_text()
    assert original == after, "current_task.md must not be mutated on a gate"
