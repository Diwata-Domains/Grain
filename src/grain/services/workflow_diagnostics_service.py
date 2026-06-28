# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""Operator-facing workflow diagnostics layered over workflow evaluation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from grain.domain.workflow import WorkflowEvaluation
from grain.services.workflow_service import evaluate_workflow_state


@dataclass
class WorkflowDiagnostic:
    """Explain the current workflow state in operator-facing terms."""

    status: str
    summary: str
    likely_cause: str
    recommended_actions: list[str] = field(default_factory=list)
    suggested_commands: list[str] = field(default_factory=list)
    affected_artifacts: list[str] = field(default_factory=list)
    active_phase: str = ""
    active_task_id: str = ""
    stop_reason: str = ""
    next_action: str = ""
    recommended_prompt: str = ""


def explain_workflow_state(root: Path):
    """Return the read-only workflow evaluation plus operator-facing guidance."""
    result, evaluation = evaluate_workflow_state(root)
    if evaluation is None:
        return result, None, None
    return result, evaluation, _build_diagnostic(evaluation)


def diagnostic_to_dict(diagnostic: WorkflowDiagnostic) -> dict:
    return asdict(diagnostic)


def _build_diagnostic(evaluation: WorkflowEvaluation) -> WorkflowDiagnostic:
    active_task_id = evaluation.active_task_id or "none"
    status = "actionable" if evaluation.ok else "blocked"
    summary = "Workflow state evaluated successfully."
    likely_cause = "The current repo state matches the expected Grain workflow shape."
    recommended_actions: list[str] = []
    suggested_commands: list[str] = []

    if evaluation.ok:
        if evaluation.next_action == "task_execute" or evaluation.stop_reason == "packet_required":
            summary = "A task is ready to execute."
            likely_cause = "The current phase has exactly one actionable backlog item and no active packet is blocking progress."
            if evaluation.candidate_tasks:
                task_ref = evaluation.candidate_tasks[0].task_ref
                recommended_actions.append(
                    f"Create or activate the packet for {task_ref}, then execute through the packet files."
                )
                suggested_commands.extend(
                    [
                        "grain workflow next",
                        "grain workflow run",
                    ]
                )
        elif evaluation.next_action == "task_close":
            summary = "The active task is ready for closure."
            likely_cause = "Execution artifacts exist and Grain is waiting for review approval and closeout."
            recommended_actions.append(
                f"Review the packet results for {active_task_id}, approve if acceptable, then close it."
            )
            suggested_commands.extend(
                [
                    f"grain review check --id {active_task_id}",
                    f"grain task close --id {active_task_id}",
                ]
            )
        elif evaluation.next_action == "task_planning":
            summary = "The next step is planning, not execution."
            likely_cause = "The current phase has no single ready task to execute yet."
            recommended_actions.append(
                "Choose or define the next backlog item before trying to activate a packet."
            )
            suggested_commands.append("grain workflow next")
        elif evaluation.next_action == "phase_review_close":
            summary = "The phase is ready for review and closure."
            likely_cause = "Task execution for the phase is complete and Grain is waiting for the phase seal."
            recommended_actions.append(
                "Review phase outcomes, update metrics/current focus if needed, then close the phase."
            )
            suggested_commands.append("grain phase close")
    else:
        stop_reason = evaluation.stop_reason
        if stop_reason in {"required_docs_missing", "required_docs_invalid"}:
            summary = "Workflow metadata is incomplete or malformed."
            likely_cause = "One or more required working docs no longer match the file-backed contract Grain expects."
            recommended_actions.extend(
                [
                    "Repair the affected working docs so they contain the required fields and valid values.",
                    "Re-run the workflow command after the docs are repaired.",
                ]
            )
            suggested_commands.extend(
                [
                    "grain workflow next",
                    "grain workflow reconcile --dry-run",
                ]
            )
        elif stop_reason == "workflow_state_drift":
            summary = "Workflow documents and packet state have drifted apart."
            likely_cause = "The backlog, current_task pointer, or packet status no longer describes the same active state."
            recommended_actions.extend(
                [
                    "Inspect the affected backlog entry, current_task pointer, and packet status together.",
                    "Use the reconcile flow to preview or apply safe repairs before continuing.",
                ]
            )
            suggested_commands.extend(
                [
                    "grain workflow reconcile --dry-run",
                    "grain workflow reconcile --fix",
                ]
            )
        elif stop_reason == "execution_in_flight":
            summary = "The active task is still in execution."
            likely_cause = "An active packet exists but its review artifacts are not complete yet."
            recommended_actions.extend(
                [
                    "Continue execution inside the active packet and write the missing artifacts.",
                    "Produce results.md before trying to review or close the task.",
                ]
            )
            suggested_commands.append("grain workflow next")
        elif stop_reason == "review_artifacts_incomplete":
            summary = "Review artifacts are missing for the active task."
            likely_cause = "The task reached review status without both results.md and handoff.md in place."
            recommended_actions.extend(
                [
                    "Fill in the missing review artifact files in the active packet.",
                    "Re-run the review checks once the packet has both results.md and handoff.md.",
                ]
            )
            suggested_commands.append(f"grain review check --id {active_task_id}")
        elif stop_reason == "review_close_blocked":
            summary = "The task cannot close until review is approved."
            likely_cause = "The packet results still show pending or unresolved review state."
            recommended_actions.extend(
                [
                    "Review the packet results and update the review state to approved, revise, or follow-up.",
                    "Run the review check again before closing the task.",
                ]
            )
            suggested_commands.extend(
                [
                    f"grain review check --id {active_task_id}",
                    f"grain task close --id {active_task_id}",
                ]
            )
        elif stop_reason == "task_blocked":
            summary = "The active task is marked blocked."
            likely_cause = "The packet status is explicitly blocked and needs a documented unblock or follow-up decision."
            recommended_actions.extend(
                [
                    "Record the blocker clearly in the packet and decide whether to revise, replan, or create a follow-up task.",
                    "Do not keep executing until the blocker is resolved or the plan is changed.",
                ]
            )
            suggested_commands.append("grain workflow next")
        elif stop_reason == "task_needs_fix":
            summary = "The active task needs fixes before closure."
            likely_cause = "Review or verification found issues that require another execution pass."
            recommended_actions.extend(
                [
                    "Return to execution for the active packet and address the listed fixes.",
                    "Only attempt closure again after the review bundle is updated.",
                ]
            )
            suggested_commands.append("grain workflow next")
        elif stop_reason == "phase_has_no_tasks":
            summary = "The active phase has no executable tasks yet."
            likely_cause = "The phase exists in current_focus.md, but backlog items have not been seeded for it."
            recommended_actions.extend(
                [
                    "Add executable tasks for the active phase to docs/working/backlog.md.",
                    "Keep the next slice small enough that one ready task can be selected cleanly.",
                ]
            )
            suggested_commands.append("grain workflow next")
        elif stop_reason == "previous_phase_not_closed":
            summary = "The previous phase was not formally sealed."
            likely_cause = "current_focus.md moved forward without the grain-verified close marker for the prior phase."
            recommended_actions.extend(
                [
                    "Return to the previous phase and complete the normal review/close step.",
                    "Do not begin new phase work until the prior phase is sealed.",
                ]
            )
            suggested_commands.append("grain phase close")
        elif stop_reason == "phase_boundary_review_close_required":
            summary = "The phase must be reviewed and sealed before new work starts."
            likely_cause = "All current phase tasks are done, but the phase close step has not been completed."
            recommended_actions.extend(
                [
                    "Review the phase outcomes and update metrics/current focus if needed.",
                    "Seal the phase before starting the next one.",
                ]
            )
            suggested_commands.append("grain phase close")
        elif stop_reason == "conflicting_next_actions":
            summary = "More than one task is ready, so Grain cannot choose automatically."
            likely_cause = "The backlog has multiple ready tasks and no accepted sequencing decision."
            recommended_actions.extend(
                [
                    "Choose the one task that should run next and demote the others back to draft if needed.",
                    "Keep only one ready task when you want workflow next/run to route automatically.",
                ]
            )
            suggested_commands.append("grain workflow next")
        elif stop_reason == "task_planning_required":
            summary = "A task must be planned or created before execution can continue."
            likely_cause = "No executable packet candidate exists for the current phase."
            recommended_actions.extend(
                [
                    "Create the next task packet or define the next backlog item before continuing.",
                    "Use simple packet mode only for small mechanical audit work.",
                ]
            )
            suggested_commands.append("grain task create --help")
        else:
            summary = "Workflow is stopped on an explicit gate."
            likely_cause = "Grain detected a valid stop condition and is waiting for an operator decision or repair."
            recommended_actions.append(
                "Inspect the blocking reasons and affected artifacts, then resolve the gate before retrying."
            )
            suggested_commands.append("grain workflow next")

    diagnostic = WorkflowDiagnostic(
        status=status,
        summary=summary,
        likely_cause=likely_cause,
        recommended_actions=recommended_actions,
        suggested_commands=suggested_commands,
        affected_artifacts=list(evaluation.affected_artifacts),
        active_phase=evaluation.active_phase,
        active_task_id=active_task_id,
        stop_reason=evaluation.stop_reason,
        next_action=evaluation.next_action,
        recommended_prompt=evaluation.recommended_prompt,
    )
    return diagnostic
