# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Workflow runner service — executes one legal workflow step or stops at a gate."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from grain.domain.command_result import CommandResult
from grain.domain.packets import write_packet_status
from grain.services.task_observability_service import update_task_observability

_TASK_ID_RE = re.compile(r"TASK-\d{4,}")
_BACKLOG_TASK_HEADING_RE = re.compile(r"^###\s+(P(\d+)-T(\d+))\s+—\s+(.+)$")
_BACKLOG_PHASE_HEADING_RE = re.compile(r"^##\s+\d+\.\s+(Phase\s+\d+\s+—\s+.+)$")

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

    # ── next_action == "task_execute" or stop_reason == "packet_required" ────
    if evaluation.next_action == "task_execute" or evaluation.stop_reason == "packet_required":
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
            if task_id:
                write_packet_status(packet_dir, "in_progress")
                _write_backlog_task_status(root / "docs" / "working" / "backlog.md", task_ref, "in_progress")
            task_path = f"tasks/{packet_dir.name}/"
            _write_current_task(root, task_id or task_ref, task_path, "in_progress")
            observability_path = None
            try:
                _, observability_path = update_task_observability(
                    root,
                    task_id or task_ref,
                    stage="execute",
                    workflow_action=f"workflow_run:{'create_and_activate_task' if packet_was_created else 'activate_task'}",
                )
            except FileNotFoundError:
                observability_path = None

            action = "create_and_activate_task" if packet_was_created else "activate_task"
            files_updated = ["docs/working/current_task.md"]
            if packet_was_created:
                files_updated.insert(0, task_path)
            if observability_path is not None:
                files_updated.append(str(observability_path.relative_to(root)))

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
    phase_label, task_title = _read_backlog_task_metadata(root / "docs" / "working" / "backlog.md", task_ref)

    from grain.services.task_service import create_packet_directory

    create_result = create_packet_directory(
        root,
        phase=phase,
        task_num=task_num,
        title=task_title,
        simple=simple,
    )
    if not create_result.ok:
        return None, "; ".join(create_result.errors)

    packet_dir = _find_packet_dir_for_ref(root, task_ref)
    if packet_dir is None:
        return None, f"packet directory not found after creation for {task_ref}"

    task_id = _read_task_id_from_packet(packet_dir)
    _hydrate_packet_templates(
        packet_dir,
        task_id=task_id,
        task_ref=task_ref,
        phase_label=phase_label or f"Phase {phase}",
        task_title=task_title or task_ref,
    )

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


def _read_backlog_task_metadata(backlog_path: Path, task_ref: str) -> tuple[str, str]:
    current_phase_label = ""
    for line in backlog_path.read_text(encoding="utf-8").splitlines():
        phase_match = _BACKLOG_PHASE_HEADING_RE.match(line.strip())
        if phase_match:
            current_phase_label = phase_match.group(1)
            continue
        heading_match = _BACKLOG_TASK_HEADING_RE.match(line.strip())
        if heading_match and heading_match.group(1) == task_ref:
            return current_phase_label, heading_match.group(4).strip()
    return "", ""


def _hydrate_packet_templates(
    packet_dir: Path,
    *,
    task_id: str,
    task_ref: str,
    phase_label: str,
    task_title: str,
) -> None:
    replacements = {
        "TASK-####": task_id,
        "[Title]": task_title,
        "[phase name]": phase_label,
        "[backlog item]": task_ref,
        "[packet-dir]": packet_dir.name,
        "[none or TASK-IDs]": "none",
        "[none or adapter_id]": "none",
        "[none or comma-separated adapter_ids]": "none",
        "[adapter_id or none]": "none",
        "[adapter_ids or none]": "none",
    }
    static_overrides = {
        "context.md": {
            "- [doc path] — [relevant section or reason]": "- `docs/canonical/cli_spec.md` — task-specific canonical contract to refine during execution",
            "- [doc path] — [reason, e.g. sequencing or blockers]": "- `docs/working/backlog.md` — sequencing reference for this task",
            "- **Adapter Rationale:** [why this adapter applies to this task, or \"n/a\"]": "- **Adapter Rationale:** To be refined during execution based on the specific implementation slice.",
            "- [doc or area excluded and why]": "- Unrelated repo areas are excluded until task-specific context is refined.",
            "[One sentence confirming the selected docs are sufficient to implement and review this task.]": "Bootstrapped packet created by `workflow run`; refine task-specific context before major edits.",
        },
        "plan.md": {
            "[One paragraph describing the overall implementation strategy.]": "Refine the task-specific implementation strategy before major edits; this bootstrap plan only establishes the packet shape.",
            "## Step 1 — [Step name]": "## Step 1 — Refine scope",
            "[What to do and why.]": "Replace this bootstrap content with task-specific execution steps before substantial implementation work.",
            "## Step 2 — [Step name]": "## Step 2 — Implement the slice",
            "## Step 3 — [Step name]": "## Step 3 — Verify and document",
            "[How to confirm the implementation is correct before writing results.]": "Run the task-specific verification commands before writing `results.md`.",
        },
        "deliverable_spec.md": {
            "- [path] — [brief description]": "- None",
            "- [path] — [what changes]": "- Task-specific file targets to be refined during execution",
            "- [ ] [criterion]": "- [ ] Refine task-specific acceptance criteria before substantial implementation work",
            "- [explicitly out of scope for this task]": "- Any work not explicitly refined into this packet during execution",
        },
    }

    for filename in ("task.md", "context.md", "plan.md", "deliverable_spec.md"):
        path = packet_dir / filename
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        for old, new in replacements.items():
            content = content.replace(old, new)
        for old, new in static_overrides.get(filename, {}).items():
            content = content.replace(old, new)
        path.write_text(content, encoding="utf-8")


def _write_backlog_task_status(backlog_path: Path, task_ref: str, status: str) -> None:
    lines = backlog_path.read_text(encoding="utf-8").splitlines()
    updated_lines: list[str] = []
    in_target = False

    for line in lines:
        stripped = line.strip()
        heading_match = _BACKLOG_TASK_HEADING_RE.match(stripped)
        if heading_match:
            in_target = heading_match.group(1) == task_ref
            updated_lines.append(line)
            continue
        if in_target and stripped.startswith("- **Status:**"):
            prefix = line.split("- **Status:**", 1)[0]
            updated_lines.append(f"{prefix}- **Status:** {status}")
            in_target = False
            continue
        updated_lines.append(line)

    backlog_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
