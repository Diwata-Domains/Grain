"""Integration tests for the Phase 8 runner command chain.

Tests here cover cross-command state agreement and state transitions rather than
individual command behavior (which is covered by unit tests in test_workflow_*.py,
test_task_*.py, test_phase_*.py, test_prompt_show_cmd.py).
"""

import json
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main


# ── Helpers ───────────────────────────────────────────────────────────────────


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


def _ready_backlog(repo: Path, task_ref: str = "P8-T09") -> None:
    _write(
        repo / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            f"### {task_ref} — Integration test task\n"
            "- **Status:** ready\n"
        ),
    )


def _draft_backlog(repo: Path, task_ref: str = "P8-T09") -> None:
    _write(
        repo / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            f"### {task_ref} — Integration test task\n"
            "- **Status:** draft\n"
        ),
    )


def _done_backlog(repo: Path, task_ref: str = "P8-T09") -> None:
    _write(
        repo / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            f"### {task_ref} — Integration test task\n"
            "- **Status:** done\n"
        ),
    )


def _packet(repo: Path, task_ref: str, task_id: str, status: str) -> Path:
    dir_name = f"{task_ref}-{task_id}"
    packet_dir = repo / "tasks" / dir_name
    packet_dir.mkdir(parents=True, exist_ok=True)
    _write(
        packet_dir / "task.md",
        (
            "# Task: Integration test\n\n## Metadata\n"
            f"- **ID:** {task_id}\n"
            f"- **Status:** {status}\n"
            "- **Phase:** Phase 8 — Workflow Automation Runner Foundation\n"
        ),
    )
    _write(packet_dir / "context.md", "# Context\n")
    _write(packet_dir / "plan.md", "# Plan\n")
    _write(packet_dir / "deliverable_spec.md", "# Deliverable\n")
    return packet_dir


def _invoke(repo: Path, *args: str, fmt: str = "text") -> tuple[int, str]:
    runner = CliRunner()
    cmd = ["--repo", str(repo)]
    if fmt == "json":
        cmd += ["--format", "json"]
    cmd += list(args)
    result = runner.invoke(main, cmd)
    return result.exit_code, result.output


def _invoke_json(repo: Path, *args: str) -> dict:
    exit_code, output = _invoke(repo, *args, fmt="json")
    assert exit_code == 0, f"Command failed (exit {exit_code}): {output}"
    return json.loads(output)


# ── Scenario A: Task activation chain ─────────────────────────────────────────


def test_activation_chain_workflow_next_sees_activation(tmp_path):
    """State written by `workflow run` is immediately visible to `workflow next`."""
    _base_repo(tmp_path)
    _ready_backlog(tmp_path, "P8-T09")
    _packet(tmp_path, "P8-T09", "TASK-0069", "ready")

    # Before activation: workflow next reports task_execute with no active task
    data_before = _invoke_json(tmp_path, "workflow", "next")
    assert data_before["evaluation"]["next_action"] == "task_execute"
    assert data_before["evaluation"]["active_task_id"] == ""

    # Activate via workflow run
    exit_code, output = _invoke(tmp_path, "workflow", "run")
    assert exit_code == 0
    assert "workflow run: ok" in output

    # After activation: workflow next gates until results.md is written
    # (in_progress without results.md means execution is still in flight)
    data_after = _invoke_json(tmp_path, "workflow", "next")
    assert data_after["evaluation"]["ok"] is False
    assert data_after["evaluation"]["stop_reason"] == "execution_in_flight"
    assert data_after["evaluation"]["active_task_id"] == "TASK-0069"


def test_activation_chain_second_run_gates(tmp_path):
    """Second `workflow run` after activation gates with execution_in_flight."""
    _base_repo(tmp_path)
    _ready_backlog(tmp_path, "P8-T09")
    _packet(tmp_path, "P8-T09", "TASK-0069", "ready")

    # First run: activates
    exit_code, output = _invoke(tmp_path, "workflow", "run")
    assert exit_code == 0
    assert "workflow run: ok" in output

    # Second run: gates because task is now in_progress
    exit_code, output = _invoke(tmp_path, "workflow", "run")
    assert exit_code == 0
    assert "workflow run: gated" in output
    assert "execution_in_flight" in output


def test_activation_chain_current_task_written_correctly(tmp_path):
    """current_task.md has correct content after activation."""
    _base_repo(tmp_path)
    _ready_backlog(tmp_path, "P8-T09")
    _packet(tmp_path, "P8-T09", "TASK-0069", "ready")

    _invoke(tmp_path, "workflow", "run")

    content = (tmp_path / "docs" / "working" / "current_task.md").read_text()
    assert "Task ID: TASK-0069" in content
    assert "Task Path: tasks/P8-T09-TASK-0069/" in content
    assert "Status: in_progress" in content


# ── Scenario B: Cross-command agreement on ready task ─────────────────────────


def test_cross_command_agreement_ready_task_workflow_next(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path, "P8-T09")

    data = _invoke_json(tmp_path, "workflow", "next")
    assert data["evaluation"]["next_action"] == "task_execute"
    assert data["evaluation"]["ok"] is True


def test_cross_command_agreement_ready_task_task_next(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path, "P8-T09")

    data = _invoke_json(tmp_path, "task", "next")
    assert data["task_next"]["next_action"] == "task_execute"
    assert data["task_next"]["planning_required"] is False
    assert data["task_next"]["next_task"] == "P8-T09"


def test_cross_command_agreement_ready_task_phase_next(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path, "P8-T09")

    data = _invoke_json(tmp_path, "phase", "next")
    assert data["phase_next"]["phase_action"] == "no_phase_action"
    assert data["phase_next"]["next_action"] == "task_execute"


def test_activation_chain_results_written_routes_to_review(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path, "P8-T09")
    _packet(tmp_path, "P8-T09", "TASK-0069", "ready")

    exit_code, output = _invoke(tmp_path, "workflow", "run")
    assert exit_code == 0
    assert "workflow run: ok" in output

    (tmp_path / "tasks" / "P8-T09-TASK-0069" / "results.md").write_text(
        "# Results\nComplete.\n",
        encoding="utf-8",
    )

    data_after = _invoke_json(tmp_path, "workflow", "next")
    assert data_after["evaluation"]["ok"] is True
    assert data_after["evaluation"]["next_action"] == "task_review"
    assert data_after["evaluation"]["recommended_prompt"] == "prompts/task.review.md"


# ── Scenario C: Cross-command agreement on planning scenario ──────────────────


def test_cross_command_agreement_planning_workflow_next(tmp_path):
    _base_repo(tmp_path)
    _draft_backlog(tmp_path, "P8-T09")

    data = _invoke_json(tmp_path, "workflow", "next")
    assert data["evaluation"]["next_action"] == "task_planning"


def test_cross_command_agreement_planning_task_next(tmp_path):
    _base_repo(tmp_path)
    _draft_backlog(tmp_path, "P8-T09")

    data = _invoke_json(tmp_path, "task", "next")
    assert data["task_next"]["planning_required"] is True
    assert data["task_next"]["next_action"] == "task_planning"


def test_cross_command_agreement_planning_phase_next(tmp_path):
    _base_repo(tmp_path)
    _draft_backlog(tmp_path, "P8-T09")

    data = _invoke_json(tmp_path, "phase", "next")
    assert data["phase_next"]["phase_action"] == "phase_planning"


def test_cross_command_agreement_planning_workflow_run(tmp_path):
    _base_repo(tmp_path)
    _draft_backlog(tmp_path, "P8-T09")

    exit_code, output = _invoke(tmp_path, "workflow", "run")
    assert exit_code == 0
    assert "workflow run: gated" in output
    assert "planning_required" in output


# ── Scenario D: Phase boundary agreement ──────────────────────────────────────


def test_phase_boundary_workflow_next(tmp_path):
    _base_repo(tmp_path)
    _done_backlog(tmp_path, "P8-T09")

    data = _invoke_json(tmp_path, "workflow", "next")
    assert data["evaluation"]["stop_reason"] == "phase_boundary_review_close_required"


def test_phase_boundary_phase_next(tmp_path):
    _base_repo(tmp_path)
    _done_backlog(tmp_path, "P8-T09")

    data = _invoke_json(tmp_path, "phase", "next")
    assert data["phase_next"]["phase_action"] == "phase_review_close"
    assert data["phase_next"]["stop_reason"] == "phase_boundary_review_close_required"


def test_phase_boundary_workflow_run(tmp_path):
    _base_repo(tmp_path)
    _done_backlog(tmp_path, "P8-T09")

    exit_code, output = _invoke(tmp_path, "workflow", "run")
    assert exit_code == 0
    assert "workflow run: gated" in output
    assert "phase_boundary" in output


# ── Scenario E: JSON output invariants ────────────────────────────────────────


def test_json_invariants_workflow_next(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path, "P8-T09")

    data = _invoke_json(tmp_path, "workflow", "next")
    # Base CommandResult fields
    assert "ok" in data
    assert "command" in data
    assert "repo" in data
    assert "errors" in data
    # Payload key
    assert "evaluation" in data
    # Required evaluation subfields
    ev = data["evaluation"]
    assert "ok" in ev
    assert "next_action" in ev
    assert "stop_reason" in ev
    assert "blocking_reasons" in ev
    assert "recommended_prompt" in ev
    assert "affected_artifacts" in ev
    assert "active_phase" in ev
    assert "active_task_id" in ev
    assert "candidate_tasks" in ev


def test_json_invariants_task_next(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path, "P8-T09")

    data = _invoke_json(tmp_path, "task", "next")
    assert "ok" in data
    assert "command" in data
    assert "repo" in data
    assert "task_next" in data
    tn = data["task_next"]
    assert "next_task" in tn
    assert "next_action" in tn
    assert "planning_required" in tn
    assert "stop_reason" in tn
    assert "blocking_reasons" in tn
    assert "recommended_prompt" in tn
    assert "affected_artifacts" in tn


def test_json_invariants_phase_next(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path, "P8-T09")

    data = _invoke_json(tmp_path, "phase", "next")
    assert "ok" in data
    assert "command" in data
    assert "repo" in data
    assert "phase_next" in data
    pn = data["phase_next"]
    assert "active_phase" in pn
    assert "phase_action" in pn
    assert "reason" in pn
    assert "next_action" in pn
    assert "stop_reason" in pn
    assert "blocking_reasons" in pn
    assert "recommended_prompt" in pn
    assert "affected_artifacts" in pn


def test_json_invariants_workflow_run(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path, "P8-T09")
    _packet(tmp_path, "P8-T09", "TASK-0069", "ready")

    data = _invoke_json(tmp_path, "workflow", "run")
    assert "ok" in data
    assert "command" in data
    assert "repo" in data
    assert "workflow_run" in data
    wr = data["workflow_run"]
    assert "action_taken" in wr
    assert "gate_reason" in wr
    assert "gate_condition" in wr
    assert "task_activated" in wr
    assert "recommended_prompt" in wr
    assert "blocking_reasons" in wr
    assert "affected_artifacts" in wr
    assert "active_phase" in wr
    assert "active_task_id" in wr


def test_json_invariants_prompt_show(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path, "P8-T09")

    data = _invoke_json(tmp_path, "prompt", "show")
    assert "ok" in data
    assert "command" in data
    assert "repo" in data
    assert "prompt" in data
    p = data["prompt"]
    assert "recommended_prompt" in p
    assert "prompt_exists" in p
    assert "model_class" in p
    assert "next_action" in p
    assert "stop_reason" in p
    assert "blocking_reasons" in p
    assert "active_phase" in p
    assert "active_task_id" in p
