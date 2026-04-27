"""Workflow runner service — executes one legal workflow step or stops at a gate."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from grain.cli.output import CommandResult

_TASK_ID_RE = re.compile(r"TASK-\d{4,}")

# Gate reasons mapped from stop conditions and next_action states.
_GATE_MAP: dict[str, str] = {
    "required_docs_missing": "required_docs_missing",
    "required_docs_invalid": "required_docs_invalid",
    "project_complete": "project_complete",
    "task_blocked": "task_blocked",
    "review_artifacts_incomplete": "review_artifacts_incomplete",
    "conflicting_next_actions": "ambiguous_next_action",
    "task_planning_required": "planning_required",
    "phase_boundary_review_close_required": "phase_boundary",
}


def run_workflow_step(root: Path, simple: bool = False) -> tuple[CommandResult, dict | None]:
    """Execute one legal workflow step or stop at a gate.

    This is the only service in the system that may mutate state.
    State mutation is limited to writing ``docs/working/current_task.md``
    when a ready task is activated.

    Returns a (CommandResult, payload) tuple.  payload is None only on a
    hard service failure (evaluate_workflow_state returned None).
    """
    from grain.services.workflow_service import evaluate_workflow_state

    cmd_result, evaluation = evaluate_workflow_state(root)

    if evaluation is None:
        return cmd_result, None

    # ── Evaluation returned a stop condition ──────────────────────────────
    if not evaluation.ok:
        gate_reason = _GATE_MAP.get(evaluation.stop_reason, evaluation.stop_reason or "unknown_state")
        payload = _gate_payload(
            action_taken="none",
            gate_reason=gate_reason,
            gate_condition=evaluation.stop_reason,
            recommended_prompt=evaluation.recommended_prompt,
            blocking_reasons=evaluation.blocking_reasons,
            affected_artifacts=evaluation.affected_artifacts,
            active_phase=evaluation.active_phase,
            active_task_id=evaluation.active_task_id,
        )
        result = CommandResult(
            ok=False,
            command="workflow run",
            repo=str(root),
            errors=list(evaluation.blocking_reasons),
        )
        return result, payload

    # ── next_action == "task_execute" ─────────────────────────────────────
    if evaluation.next_action == "task_execute":
        # Task is already in_progress — execution requires an agent/human.
        if evaluation.active_task_id:
            payload = _gate_payload(
                action_taken="none",
                gate_reason="execution_in_flight",
                gate_condition="task_in_progress",
                recommended_prompt=evaluation.recommended_prompt,
                blocking_reasons=[
                    "active task is in progress; execution requires agent or human"
                ],
                affected_artifacts=evaluation.affected_artifacts,
                active_phase=evaluation.active_phase,
                active_task_id=evaluation.active_task_id,
            )
            result = CommandResult(
                ok=False,
                command="workflow run",
                repo=str(root),
                errors=["active task is in progress; execution requires agent or human"],
            )
            return result, payload

        # One ready candidate with no active task → activate it.
        if len(evaluation.candidate_tasks) == 1:
            candidate = evaluation.candidate_tasks[0]
            task_ref = candidate.task_ref
            packet_dir = _find_packet_dir_for_ref(root, task_ref)
            packet_was_created = False

            if packet_dir is None:
                # Auto-bootstrap: create the missing packet so execution can proceed.
                packet_dir, create_error = _create_packet_for_ref(root, task_ref, simple=simple)
                if packet_dir is None:
                    payload = _gate_payload(
                        action_taken="none",
                        gate_reason="packet_create_failed",
                        gate_condition="required_docs_invalid",
                        recommended_prompt="",
                        blocking_reasons=[
                            f"packet not found and auto-create failed for {task_ref}: {create_error}"
                        ],
                        affected_artifacts=["tasks/"],
                        active_phase=evaluation.active_phase,
                        active_task_id="",
                    )
                    result = CommandResult(
                        ok=False,
                        command="workflow run",
                        repo=str(root),
                        errors=[f"packet not found and auto-create failed for {task_ref}"],
                    )
                    return result, payload
                packet_was_created = True

            task_id = _read_task_id_from_packet(packet_dir)
            task_path = f"tasks/{packet_dir.name}/"
            _write_current_task(root, task_id or task_ref, task_path, "in_progress")

            action = "create_and_activate_task" if packet_was_created else "activate_task"
            files_updated = ["docs/working/current_task.md"]
            if packet_was_created:
                files_updated.insert(0, task_path)

            payload = {
                "action_taken": action,
                "gate_reason": "",
                "gate_condition": "",
                "task_activated": task_id or task_ref,
                "packet_created": packet_was_created,
                "recommended_prompt": evaluation.recommended_prompt or "prompts/task.execute.md",
                "blocking_reasons": [],
                "affected_artifacts": [
                    "docs/working/current_task.md",
                    task_path,
                ],
                "active_phase": evaluation.active_phase,
                "active_task_id": task_id or task_ref,
            }
            result = CommandResult(
                ok=True,
                command="workflow run",
                repo=str(root),
                files_updated=files_updated,
            )
            return result, payload

    # ── next_action == "task_close" ───────────────────────────────────────
    if evaluation.next_action == "task_close":
        payload = _gate_payload(
            action_taken="none",
            gate_reason="human_review_required",
            gate_condition="task_close",
            recommended_prompt=evaluation.recommended_prompt,
            blocking_reasons=["task is in review; closure requires human or reviewer approval"],
            affected_artifacts=evaluation.affected_artifacts,
            active_phase=evaluation.active_phase,
            active_task_id=evaluation.active_task_id,
        )
        result = CommandResult(
            ok=False,
            command="workflow run",
            repo=str(root),
            errors=["task is in review; closure requires human or reviewer approval"],
        )
        return result, payload

    # ── next_action == "task_review" ──────────────────────────────────────
    if evaluation.next_action == "task_review":
        payload = _gate_payload(
            action_taken="none",
            gate_reason="human_review_required",
            gate_condition="task_review",
            recommended_prompt=evaluation.recommended_prompt,
            blocking_reasons=["task has execution artifacts and must be reviewed before closure"],
            affected_artifacts=evaluation.affected_artifacts,
            active_phase=evaluation.active_phase,
            active_task_id=evaluation.active_task_id,
        )
        result = CommandResult(
            ok=False,
            command="workflow run",
            repo=str(root),
            errors=["task has execution artifacts and must be reviewed before closure"],
        )
        return result, payload

    # ── next_action == "task_planning" ────────────────────────────────────
    if evaluation.next_action == "task_planning":
        payload = _gate_payload(
            action_taken="none",
            gate_reason="planning_required",
            gate_condition="task_planning",
            recommended_prompt=evaluation.recommended_prompt,
            blocking_reasons=evaluation.blocking_reasons,
            affected_artifacts=evaluation.affected_artifacts,
            active_phase=evaluation.active_phase,
            active_task_id=evaluation.active_task_id,
        )
        result = CommandResult(
            ok=False,
            command="workflow run",
            repo=str(root),
            errors=list(evaluation.blocking_reasons),
        )
        return result, payload

    # ── Unknown / unhandled next_action ───────────────────────────────────
    payload = _gate_payload(
        action_taken="none",
        gate_reason="unknown_state",
        gate_condition="unknown",
        recommended_prompt=evaluation.recommended_prompt,
        blocking_reasons=["workflow state could not be resolved to a legal runner action"],
        affected_artifacts=[],
        active_phase=evaluation.active_phase,
        active_task_id=evaluation.active_task_id,
    )
    result = CommandResult(
        ok=False,
        command="workflow run",
        repo=str(root),
        errors=["workflow state could not be resolved to a legal runner action"],
    )
    return result, payload


# ── Helpers ───────────────────────────────────────────────────────────────────


def _gate_payload(
    *,
    action_taken: str,
    gate_reason: str,
    gate_condition: str,
    recommended_prompt: str,
    blocking_reasons: list[str],
    affected_artifacts: list[str],
    active_phase: str,
    active_task_id: str,
) -> dict[str, Any]:
    return {
        "action_taken": action_taken,
        "gate_reason": gate_reason,
        "gate_condition": gate_condition,
        "task_activated": "",
        "recommended_prompt": recommended_prompt,
        "blocking_reasons": list(blocking_reasons),
        "affected_artifacts": list(affected_artifacts),
        "active_phase": active_phase,
        "active_task_id": active_task_id,
    }


def _find_packet_dir_for_ref(root: Path, task_ref: str) -> Path | None:
    """Return the packet directory whose name starts with ``task_ref + '-'``."""
    tasks_dir = root / "tasks"
    if not tasks_dir.exists():
        return None
    prefix = task_ref + "-"
    for candidate in tasks_dir.iterdir():
        if candidate.is_dir() and candidate.name.startswith(prefix):
            return candidate
    return None


_TASK_REF_RE = re.compile(r"P(\d+)-T(\d+)")


def _create_packet_for_ref(
    root: Path, task_ref: str, simple: bool = False
) -> tuple[Path | None, str]:
    """Create a packet directory for task_ref and return (packet_dir, error).

    Parses phase and task number from the task_ref (e.g. ``P15-T01``), calls
    ``create_packet_directory``, then re-resolves the created directory by prefix.
    Returns ``(None, error_message)`` on failure.
    """
    m = _TASK_REF_RE.match(task_ref)
    if not m:
        return None, f"cannot parse phase/task number from task ref: {task_ref}"

    phase = int(m.group(1))
    task_num = int(m.group(2))

    from grain.services.task_service import create_packet_directory

    create_result = create_packet_directory(root, phase=phase, task_num=task_num, simple=simple)
    if not create_result.ok:
        return None, "; ".join(create_result.errors)

    packet_dir = _find_packet_dir_for_ref(root, task_ref)
    if packet_dir is None:
        return None, f"packet directory not found after creation for {task_ref}"

    return packet_dir, ""


def _read_task_id_from_packet(packet_dir: Path) -> str:
    """Extract the TASK-#### identifier from ``task.md`` in a packet directory."""
    task_md = packet_dir / "task.md"
    if not task_md.exists():
        return ""
    for line in task_md.read_text(encoding="utf-8").splitlines():
        if "**ID:**" in line:
            m = _TASK_ID_RE.search(line)
            if m:
                return m.group(0)
    return ""


def _write_current_task(root: Path, task_id: str, task_path: str, status: str) -> None:
    """Write ``docs/working/current_task.md`` to record the active task."""
    current_task_path = root / "docs" / "working" / "current_task.md"
    content = (
        "# Current Task\n\n"
        f"Task ID: {task_id}\n"
        f"Task Path: {task_path}\n"
        f"Status: {status}\n"
    )
    current_task_path.write_text(content, encoding="utf-8")
