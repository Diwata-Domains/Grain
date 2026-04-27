"""Workflow state evaluator service (read-only, no mutation)."""

from __future__ import annotations

import re
from dataclasses import asdict
from pathlib import Path
from typing import Any

from grain.domain.packets import find_packet_dir, parse_task_metadata
from grain.domain.workflow import WorkflowEvaluation, WorkflowTaskState
from grain.validators.packet_validator import validate_packet

_CURRENT_TASK_REQUIRED = ("Task ID:", "Task Path:", "Status:")
_TASK_HEADING = re.compile(r"^###\s+(P(\d+)-T(\d+))\s+—\s+(.+)$")
_PHASE_HEADING = re.compile(r"^##\s+\d+\.\s+Phase\s+(\d+)\s+—")
_BACKLOG_STATUS = re.compile(r"^- \*\*Status:\*\*\s*(\S+)")
_CURRENT_PHASE_LINE = re.compile(r"^Phase\s+(\d+)\s+—")
_CURRENT_PHASE_COMPLETE_LINE = re.compile(r"^(Phase:\s*)?(complete|done)\s*$", re.IGNORECASE)
_PHASE_CLOSED_MARKER_RE = re.compile(r"^Phase\s+(\d+)\s+closed:")
_DEFAULT_PHASE_DOC = "docs/working/current_focus.md"
_DEFAULT_BACKLOG_DOC = "docs/working/backlog.md"
_DEFAULT_CURRENT_TASK_DOC = "docs/working/current_task.md"

# Phases >= this value require a grain-verified closed marker before the next
# phase can be evaluated.  Phases before this were closed before grain phase
# close existed and are grandfathered.
_PHASE_CLOSE_MIN_ENFORCED = 15


def evaluate_workflow_state(
    root: Path,
) -> tuple[Any, WorkflowEvaluation | None]:
    """Evaluate repo workflow state and return the next legal one-step action.

    This service is intentionally read-only: it never mutates packet or doc state.
    """
    required = [
        _DEFAULT_PHASE_DOC,
        _DEFAULT_BACKLOG_DOC,
        _DEFAULT_CURRENT_TASK_DOC,
    ]
    missing = [path for path in required if not (root / path).exists()]
    if missing:
        evaluation = WorkflowEvaluation(
            ok=False,
            stop_reason="required_docs_missing",
            blocking_reasons=[f"missing required doc: {path}" for path in missing],
            affected_artifacts=required,
        )
        return (
            _command_result(
                ok=False,
                command="workflow evaluate",
                repo=str(root),
                errors=list(evaluation.blocking_reasons),
            ),
            evaluation,
        )

    current_phase = _read_current_phase(root / _DEFAULT_PHASE_DOC)
    if not current_phase:
        evaluation = WorkflowEvaluation(
            ok=False,
            stop_reason="required_docs_invalid",
            blocking_reasons=["unable to parse current phase from docs/working/current_focus.md"],
            affected_artifacts=required,
        )
        return (
            _command_result(
                ok=False,
                command="workflow evaluate",
                repo=str(root),
                errors=list(evaluation.blocking_reasons),
            ),
            evaluation,
        )

    if current_phase == "complete":
        evaluation = WorkflowEvaluation(
            ok=False,
            stop_reason="project_complete",
            blocking_reasons=[
                "project is marked complete — no further workflow action is required"
            ],
            affected_artifacts=[_DEFAULT_PHASE_DOC],
            active_phase=current_phase,
        )
        return _result_with_evaluation(root, evaluation)

    if current_phase == "0":
        evaluation = WorkflowEvaluation(
            ok=False,
            stop_reason="bootstrap_incomplete",
            blocking_reasons=[
                "working docs are in bootstrap state — run the onboarding prompt to populate "
                "project-specific content before using the workflow runner"
            ],
            affected_artifacts=required,
            recommended_prompt="prompts/workflow.onboard.existing.md",
        )
        return (
            _command_result(
                ok=False,
                command="workflow evaluate",
                repo=str(root),
                errors=list(evaluation.blocking_reasons),
            ),
            evaluation,
        )

    # Guard: if the previous phase is within the enforced range, require that it
    # was properly sealed by `grain phase close` before routing begins.
    # This blocks manual current_focus.md edits that skip the close gate.
    try:
        phase_int = int(current_phase)
    except ValueError:
        phase_int = 0
    if phase_int > _PHASE_CLOSE_MIN_ENFORCED:
        prev_phase = str(phase_int - 1)
        if not _is_phase_properly_closed(root / _DEFAULT_PHASE_DOC, prev_phase):
            evaluation = WorkflowEvaluation(
                ok=False,
                stop_reason="previous_phase_not_closed",
                blocking_reasons=[
                    f"Phase {prev_phase} was not sealed — check out Phase {prev_phase} "
                    f"and run `grain phase close` to seal it before beginning Phase {current_phase}"
                ],
                affected_artifacts=[_DEFAULT_PHASE_DOC],
                active_phase=current_phase,
            )
            return _result_with_evaluation(root, evaluation)

    current_task = _read_current_task(root / _DEFAULT_CURRENT_TASK_DOC)
    if current_task is None:
        evaluation = WorkflowEvaluation(
            ok=False,
            stop_reason="required_docs_invalid",
            blocking_reasons=["docs/working/current_task.md is missing required fields"],
            affected_artifacts=required,
            active_phase=current_phase,
        )
        return (
            _command_result(
                ok=False,
                command="workflow evaluate",
                repo=str(root),
                errors=list(evaluation.blocking_reasons),
            ),
            evaluation,
        )

    active_task_id = current_task["task_id"]
    active_task_status = current_task["status"]

    if active_task_id != "none":
        packet_dir = _resolve_packet_dir(root, active_task_id, current_task["task_path"])
        if packet_dir is None:
            evaluation = WorkflowEvaluation(
                ok=False,
                stop_reason="required_docs_invalid",
                blocking_reasons=[f"active task packet not found: {active_task_id}"],
                affected_artifacts=[_DEFAULT_CURRENT_TASK_DOC, "tasks/"],
                active_phase=current_phase,
                active_task_id=active_task_id,
            )
            return _result_with_evaluation(root, evaluation)

        packet_errors = validate_packet(packet_dir)
        if packet_errors:
            evaluation = WorkflowEvaluation(
                ok=False,
                stop_reason="required_docs_invalid",
                blocking_reasons=[f"packet invalid: {err}" for err in packet_errors],
                affected_artifacts=[str(packet_dir.relative_to(root))],
                active_phase=current_phase,
                active_task_id=active_task_id,
            )
            return _result_with_evaluation(root, evaluation)

        packet_status = parse_task_metadata(packet_dir / "task.md").get("status", "")
        if packet_status == "done":
            active_task_id = "none"
            active_task_status = "idle"
        else:
            active_task_status = packet_status or active_task_status

    if active_task_id != "none":
        if active_task_status == "blocked":
            evaluation = WorkflowEvaluation(
                ok=False,
                stop_reason="task_blocked",
                blocking_reasons=[f"active task is blocked: {active_task_id}"],
                affected_artifacts=[
                    _DEFAULT_CURRENT_TASK_DOC,
                    str(packet_dir.relative_to(root) / "task.md"),
                ],
                active_phase=current_phase,
                active_task_id=active_task_id,
                recommended_prompt="prompts/task.execute.md",
            )
            return _result_with_evaluation(root, evaluation)

        if active_task_status == "needs_fix":
            evaluation = WorkflowEvaluation(
                ok=False,
                stop_reason="task_needs_fix",
                blocking_reasons=[f"active task needs fixes before closure: {active_task_id}"],
                affected_artifacts=[
                    _DEFAULT_CURRENT_TASK_DOC,
                    str(packet_dir.relative_to(root) / "task.md"),
                    str(packet_dir.relative_to(root) / "results.md"),
                ],
                active_phase=current_phase,
                active_task_id=active_task_id,
                recommended_prompt="prompts/task.execute.md",
            )
            return _result_with_evaluation(root, evaluation)

        if active_task_status == "review":
            missing_review_artifacts = _missing_review_artifacts(packet_dir)
            if missing_review_artifacts:
                evaluation = WorkflowEvaluation(
                    ok=False,
                    stop_reason="review_artifacts_incomplete",
                    blocking_reasons=missing_review_artifacts,
                    affected_artifacts=[str(packet_dir.relative_to(root))],
                    active_phase=current_phase,
                    active_task_id=active_task_id,
                    recommended_prompt="prompts/task.execute.md",
                )
                return _result_with_evaluation(root, evaluation)
            evaluation = WorkflowEvaluation(
                ok=True,
                next_action="task_close",
                recommended_prompt="prompts/task.close.md",
                affected_artifacts=[
                    _DEFAULT_CURRENT_TASK_DOC,
                    str(packet_dir.relative_to(root)),
                ],
                active_phase=current_phase,
                active_task_id=active_task_id,
            )
            return _result_with_evaluation(root, evaluation)

        # Gate: if results.md is absent, the task hasn't been formally completed yet.
        # Surface this before letting the agent jump to the next task.
        if not (packet_dir / "results.md").exists():
            evaluation = WorkflowEvaluation(
                ok=False,
                stop_reason="execution_in_flight",
                blocking_reasons=[
                    "task has no results.md — complete implementation and document outcomes "
                    "before advancing; use `grain task close --quick` for conversational workflows"
                ],
                affected_artifacts=[
                    str((packet_dir / "results.md").relative_to(root)),
                ],
                active_phase=current_phase,
                active_task_id=active_task_id,
                recommended_prompt="prompts/task.execute.md",
            )
            return _result_with_evaluation(root, evaluation)

        evaluation = WorkflowEvaluation(
            ok=True,
            next_action="task_review",
            recommended_prompt="prompts/task.review.md",
            affected_artifacts=[
                _DEFAULT_CURRENT_TASK_DOC,
                str(packet_dir.relative_to(root)),
            ],
            active_phase=current_phase,
            active_task_id=active_task_id,
        )
        return _result_with_evaluation(root, evaluation)

    backlog_tasks = _read_phase_backlog_tasks(root / _DEFAULT_BACKLOG_DOC, current_phase)
    ready_tasks = [task for task in backlog_tasks if task.status == "ready"]
    draft_tasks = [task for task in backlog_tasks if task.status == "draft"]
    open_tasks = [task for task in backlog_tasks if task.status not in {"done"}]

    if len(ready_tasks) > 1:
        evaluation = WorkflowEvaluation(
            ok=False,
            stop_reason="conflicting_next_actions",
            blocking_reasons=[
                "multiple ready tasks in active phase require deterministic selection",
                *[f"ready task: {task.task_ref}" for task in ready_tasks],
            ],
            affected_artifacts=[_DEFAULT_BACKLOG_DOC],
            active_phase=current_phase,
            candidate_tasks=ready_tasks,
            recommended_prompt="prompts/task.plan.next.md",
        )
        return _result_with_evaluation(root, evaluation)

    if len(ready_tasks) == 1:
        task = ready_tasks[0]
        evaluation = WorkflowEvaluation(
            ok=True,
            next_action="task_execute",
            recommended_prompt="prompts/task.execute.md",
            affected_artifacts=[_DEFAULT_BACKLOG_DOC, _DEFAULT_CURRENT_TASK_DOC],
            active_phase=current_phase,
            candidate_tasks=[task],
        )
        return _result_with_evaluation(root, evaluation)

    if draft_tasks:
        evaluation = WorkflowEvaluation(
            ok=True,
            next_action="task_planning",
            recommended_prompt="prompts/task.plan.next.md",
            affected_artifacts=[_DEFAULT_BACKLOG_DOC],
            active_phase=current_phase,
            candidate_tasks=[draft_tasks[0]],
        )
        return _result_with_evaluation(root, evaluation)

    if not backlog_tasks:
        evaluation = WorkflowEvaluation(
            ok=False,
            stop_reason="phase_has_no_tasks",
            blocking_reasons=[
                f"phase {current_phase} has no tasks defined in the backlog yet — "
                "add tasks before executing"
            ],
            affected_artifacts=[_DEFAULT_BACKLOG_DOC],
            active_phase=current_phase,
            recommended_prompt="prompts/task.plan.next.md",
        )
        return _result_with_evaluation(root, evaluation)

    if not open_tasks:
        evaluation = WorkflowEvaluation(
            ok=False,
            stop_reason="phase_boundary_review_close_required",
            blocking_reasons=[
                "no executable tasks remain in active phase; phase-level review/close required"
            ],
            affected_artifacts=[_DEFAULT_BACKLOG_DOC, _DEFAULT_PHASE_DOC],
            active_phase=current_phase,
            recommended_prompt="prompts/phase.review_and_close.md",
        )
        return _result_with_evaluation(root, evaluation)

    evaluation = WorkflowEvaluation(
        ok=False,
        stop_reason="task_planning_required",
        blocking_reasons=["no ready task found for active phase"],
        affected_artifacts=[_DEFAULT_BACKLOG_DOC],
        active_phase=current_phase,
        recommended_prompt="prompts/task.plan.next.md",
    )
    return _result_with_evaluation(root, evaluation)


def _result_with_evaluation(root: Path, evaluation: WorkflowEvaluation) -> tuple[Any, WorkflowEvaluation]:
    result = _command_result(ok=evaluation.ok, command="workflow evaluate", repo=str(root))
    if evaluation.blocking_reasons:
        result.errors = list(evaluation.blocking_reasons)
    return result, evaluation


def _command_result(**kwargs):
    # Local import avoids cli package import cycle during module load.
    from grain.cli.output import CommandResult

    return CommandResult(**kwargs)


def _read_current_phase(current_focus_path: Path) -> str:
    for line in current_focus_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if _CURRENT_PHASE_COMPLETE_LINE.match(stripped):
            return "complete"
        match = _CURRENT_PHASE_LINE.match(stripped)
        if match:
            return match.group(1)
    return ""


def _read_current_task(current_task_path: Path) -> dict[str, str] | None:
    text = current_task_path.read_text(encoding="utf-8")
    if not all(marker in text for marker in _CURRENT_TASK_REQUIRED):
        return None

    parsed: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        parsed[key.strip().lower()] = value.strip()

    task_id = parsed.get("task id", "")
    task_path = parsed.get("task path", "")
    status = parsed.get("status", "")
    if not task_id or not task_path or not status:
        return None

    return {
        "task_id": task_id,
        "task_path": task_path,
        "status": status,
    }


def _resolve_packet_dir(root: Path, task_id: str, task_path: str) -> Path | None:
    if task_path not in {"", "none"}:
        candidate = root / task_path
        if candidate.exists():
            return candidate
    return find_packet_dir(root / "tasks", task_id)


def _missing_review_artifacts(packet_dir: Path) -> list[str]:
    missing: list[str] = []
    for name in ("results.md", "handoff.md"):
        file_path = packet_dir / name
        if not file_path.exists():
            missing.append(f"missing review artifact: {name}")
            continue
        if not file_path.read_text(encoding="utf-8").strip():
            missing.append(f"empty review artifact: {name}")
    return missing


def _read_phase_backlog_tasks(backlog_path: Path, phase_number: str) -> list[WorkflowTaskState]:
    lines = backlog_path.read_text(encoding="utf-8").splitlines()
    current_phase = ""
    tasks: list[WorkflowTaskState] = []
    current_task_ref = ""
    current_status = ""

    for line in lines:
        phase_match = _PHASE_HEADING.match(line)
        if phase_match:
            if current_phase == phase_number and current_task_ref and current_status:
                tasks.append(
                    WorkflowTaskState(
                        task_ref=current_task_ref,
                        status=current_status,
                        source="backlog",
                    )
                )
            current_task_ref = ""
            current_status = ""
            current_phase = phase_match.group(1)
            continue

        heading_match = _TASK_HEADING.match(line)
        if heading_match:
            if current_phase == phase_number and current_task_ref and current_status:
                tasks.append(
                    WorkflowTaskState(
                        task_ref=current_task_ref,
                        status=current_status,
                        source="backlog",
                    )
                )
            current_task_ref = heading_match.group(1)
            current_status = ""
            continue

        if not current_task_ref:
            continue

        status_match = _BACKLOG_STATUS.match(line)
        if status_match:
            current_status = status_match.group(1)
            continue

    if current_phase == phase_number and current_task_ref and current_status:
        tasks.append(
            WorkflowTaskState(
                task_ref=current_task_ref,
                status=current_status,
                source="backlog",
            )
        )

    return tasks


def evaluation_to_dict(evaluation: WorkflowEvaluation) -> dict:
    """Serialize workflow evaluation for JSON-friendly command output."""
    return asdict(evaluation)


def _is_phase_properly_closed(current_focus_path: Path, phase_number: str) -> bool:
    """Return True if current_focus.md contains a grain-verified closed marker for phase_number."""
    for line in current_focus_path.read_text(encoding="utf-8").splitlines():
        m = _PHASE_CLOSED_MARKER_RE.match(line.strip())
        if m and m.group(1) == phase_number:
            return True
    return False
