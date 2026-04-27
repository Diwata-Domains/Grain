"""Tests for read-only workflow state evaluation service."""

from pathlib import Path

from grain.services.workflow_service import evaluate_workflow_state


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _base_docs(repo: Path, current_task_text: str, backlog_text: str) -> None:
    _write(
        repo / "docs" / "working" / "current_focus.md",
        "# Current Focus\n\n## Current Phase\nPhase 8 — Workflow Automation Runner Foundation\n",
    )
    _write(repo / "docs" / "working" / "current_task.md", current_task_text)
    _write(repo / "docs" / "working" / "backlog.md", backlog_text)


def _packet(repo: Path, dir_name: str, task_id: str, status: str) -> Path:
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
    return packet_dir


def test_evaluate_workflow_state_stops_when_required_docs_missing(tmp_path: Path):
    result, evaluation = evaluate_workflow_state(tmp_path)

    assert result.ok is False
    assert evaluation is not None
    assert evaluation.stop_reason == "required_docs_missing"
    assert "docs/working/current_focus.md" in evaluation.affected_artifacts


def test_evaluate_workflow_state_returns_bootstrap_incomplete_after_onboard(tmp_path: Path):
    """After `grain onboard`, current_focus.md has Phase 0 bootstrap marker.

    The workflow runner should return bootstrap_incomplete instead of a hard
    parse error, guiding the operator to run the onboarding prompt.
    """
    _write(
        tmp_path / "docs" / "working" / "current_focus.md",
        "# Current Focus\n\nPhase 0 — Bootstrap\n\n# DRAFT - run the onboarding prompt\n",
    )
    _write(
        tmp_path / "docs" / "working" / "current_task.md",
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: unset\n",
    )
    _write(tmp_path / "docs" / "working" / "backlog.md", "# Backlog\n\n# DRAFT\n")

    result, evaluation = evaluate_workflow_state(tmp_path)

    assert result.ok is False
    assert evaluation is not None
    assert evaluation.stop_reason == "bootstrap_incomplete"
    assert evaluation.recommended_prompt == "prompts/workflow.onboard.existing.md"


def test_evaluate_workflow_state_reports_project_complete_terminal_state(tmp_path: Path):
    _write(
        tmp_path / "docs" / "working" / "current_focus.md",
        "# Current Focus\n\n## Current Phase\nPhase: complete\n",
    )
    _write(
        tmp_path / "docs" / "working" / "current_task.md",
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: idle\n",
    )
    _write(tmp_path / "docs" / "working" / "backlog.md", "# Backlog\n")

    result, evaluation = evaluate_workflow_state(tmp_path)

    assert result.ok is False
    assert evaluation is not None
    assert evaluation.stop_reason == "project_complete"
    assert evaluation.active_phase == "complete"


def test_evaluate_workflow_state_stops_for_blocked_active_task(tmp_path: Path):
    _base_docs(
        tmp_path,
        (
            "# Current Task\n\n"
            "Task ID: TASK-0001\n"
            "Task Path: tasks/P8-T02-TASK-0001/\n"
            "Status: blocked\n"
        ),
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T02 — Implement workflow state evaluator service\n"
            "- **Status:** in_progress\n"
        ),
    )
    _packet(tmp_path, "P8-T02-TASK-0001", "TASK-0001", "blocked")

    result, evaluation = evaluate_workflow_state(tmp_path)

    assert result.ok is False
    assert evaluation is not None
    assert evaluation.stop_reason == "task_blocked"
    assert evaluation.active_task_id == "TASK-0001"


def test_evaluate_workflow_state_stops_for_needs_fix_active_task(tmp_path: Path):
    _base_docs(
        tmp_path,
        (
            "# Current Task\n\n"
            "Task ID: TASK-0001\n"
            "Task Path: tasks/P8-T02-TASK-0001/\n"
            "Status: needs_fix\n"
        ),
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T02 — Implement workflow state evaluator service\n"
            "- **Status:** needs_fix\n"
        ),
    )
    packet_dir = _packet(tmp_path, "P8-T02-TASK-0001", "TASK-0001", "needs_fix")
    _write(packet_dir / "results.md", "# Results: TASK-0001\n")

    result, evaluation = evaluate_workflow_state(tmp_path)

    assert result.ok is False
    assert evaluation is not None
    assert evaluation.stop_reason == "task_needs_fix"
    assert evaluation.active_task_id == "TASK-0001"


def test_evaluate_workflow_state_stops_for_incomplete_review_artifacts(tmp_path: Path):
    _base_docs(
        tmp_path,
        (
            "# Current Task\n\n"
            "Task ID: TASK-0001\n"
            "Task Path: tasks/P8-T02-TASK-0001/\n"
            "Status: review\n"
        ),
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T02 — Implement workflow state evaluator service\n"
            "- **Status:** review\n"
        ),
    )
    packet_dir = _packet(tmp_path, "P8-T02-TASK-0001", "TASK-0001", "review")
    _write(packet_dir / "results.md", "# Results\n")

    result, evaluation = evaluate_workflow_state(tmp_path)

    assert result.ok is False
    assert evaluation is not None
    assert evaluation.stop_reason == "review_artifacts_incomplete"
    assert "missing review artifact: handoff.md" in evaluation.blocking_reasons


def test_evaluate_workflow_state_recommends_task_close_for_review_ready_packet(tmp_path: Path):
    _base_docs(
        tmp_path,
        (
            "# Current Task\n\n"
            "Task ID: TASK-0001\n"
            "Task Path: tasks/P8-T02-TASK-0001/\n"
            "Status: review\n"
        ),
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T02 — Implement workflow state evaluator service\n"
            "- **Status:** review\n"
        ),
    )
    packet_dir = _packet(tmp_path, "P8-T02-TASK-0001", "TASK-0001", "review")
    _write(packet_dir / "results.md", "# Results\nComplete.\n")
    _write(packet_dir / "handoff.md", "# Handoff\nReady.\n")

    result, evaluation = evaluate_workflow_state(tmp_path)

    assert result.ok is True
    assert evaluation is not None
    assert evaluation.next_action == "task_close"
    assert evaluation.recommended_prompt == "prompts/task.close.md"


def test_evaluate_workflow_state_recommends_execute_for_single_ready_task(tmp_path: Path):
    _base_docs(
        tmp_path,
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: unset\n",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T02 — Implement workflow state evaluator service\n"
            "- **Status:** ready\n"
        ),
    )

    result, evaluation = evaluate_workflow_state(tmp_path)

    assert result.ok is True
    assert evaluation is not None
    assert evaluation.next_action == "task_execute"
    assert [task.task_ref for task in evaluation.candidate_tasks] == ["P8-T02"]


def test_evaluate_workflow_state_recommends_task_review_when_results_exist(tmp_path: Path):
    _base_docs(
        tmp_path,
        (
            "# Current Task\n\n"
            "Task ID: TASK-0001\n"
            "Task Path: tasks/P8-T02-TASK-0001/\n"
            "Status: in_progress\n"
        ),
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T02 — Implement workflow state evaluator service\n"
            "- **Status:** in_progress\n"
        ),
    )
    packet_dir = _packet(tmp_path, "P8-T02-TASK-0001", "TASK-0001", "in_progress")
    _write(packet_dir / "results.md", "# Results\nComplete.\n")

    result, evaluation = evaluate_workflow_state(tmp_path)

    assert result.ok is True
    assert evaluation is not None
    assert evaluation.next_action == "task_review"
    assert evaluation.recommended_prompt == "prompts/task.review.md"


def test_evaluate_workflow_state_ignores_done_packet_pointed_to_by_current_task(tmp_path: Path):
    _base_docs(
        tmp_path,
        (
            "# Current Task\n\n"
            "Task ID: TASK-0001\n"
            "Task Path: tasks/P8-T02-TASK-0001/\n"
            "Status: in_progress\n"
        ),
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T02 — Implement workflow state evaluator service\n"
            "- **Status:** done\n\n"
            "### P8-T03 — Follow-up task\n"
            "- **Status:** ready\n"
        ),
    )
    packet_dir = _packet(tmp_path, "P8-T02-TASK-0001", "TASK-0001", "done")
    _write(packet_dir / "results.md", "# Results\nComplete.\n")
    _write(packet_dir / "handoff.md", "# Handoff\nReady.\n")

    result, evaluation = evaluate_workflow_state(tmp_path)

    assert result.ok is True
    assert evaluation is not None
    assert evaluation.active_task_id == ""
    assert evaluation.next_action == "task_execute"
    assert [task.task_ref for task in evaluation.candidate_tasks] == ["P8-T03"]


def test_evaluate_workflow_state_stops_on_conflicting_ready_tasks(tmp_path: Path):
    _base_docs(
        tmp_path,
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: unset\n",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T02 — Implement workflow state evaluator service\n"
            "- **Status:** ready\n\n"
            "### P8-T11 — Add working-doc reconciliation checks for state drift\n"
            "- **Status:** ready\n"
        ),
    )

    result, evaluation = evaluate_workflow_state(tmp_path)

    assert result.ok is False
    assert evaluation is not None
    assert evaluation.stop_reason == "conflicting_next_actions"
    assert [task.task_ref for task in evaluation.candidate_tasks] == ["P8-T02", "P8-T11"]


def test_evaluate_workflow_state_recommends_task_planning_when_no_ready_task(tmp_path: Path):
    _base_docs(
        tmp_path,
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: unset\n",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T03 — Add `forge workflow next`\n"
            "- **Status:** draft\n"
        ),
    )

    result, evaluation = evaluate_workflow_state(tmp_path)

    assert result.ok is True
    assert evaluation is not None
    assert evaluation.next_action == "task_planning"
    assert evaluation.recommended_prompt == "prompts/task.plan.next.md"


def test_evaluate_workflow_state_stops_for_phase_review_when_no_open_tasks(tmp_path: Path):
    _base_docs(
        tmp_path,
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: unset\n",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T01 — Lock minimal workflow automation slice and stop-condition rules\n"
            "- **Status:** done\n"
        ),
    )

    result, evaluation = evaluate_workflow_state(tmp_path)

    assert result.ok is False
    assert evaluation is not None
    assert evaluation.stop_reason == "phase_boundary_review_close_required"
