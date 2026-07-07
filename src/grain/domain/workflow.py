# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""Domain models for workflow runner state evaluation."""

from dataclasses import dataclass, field


@dataclass
class WorkflowTaskState:
    """Normalized task signal extracted from backlog/current task state."""

    task_ref: str
    status: str
    source: str
    task_id: str = ""    # TASK-XXXX from backlog TASK-ID field; empty if not parsed


@dataclass
class WorkflowEvaluation:
    """Read-only workflow decision for one runner step."""

    ok: bool
    next_action: str = ""
    stop_reason: str = ""
    blocking_reasons: list[str] = field(default_factory=list)
    recommended_prompt: str = ""
    affected_artifacts: list[str] = field(default_factory=list)
    active_phase: str = ""
    active_task_id: str = ""
    candidate_tasks: list[WorkflowTaskState] = field(default_factory=list)
    # Populated when next_action == "task_execute" — gives agents a direct packet reference.
    task_packet_path: str = ""
    task_title: str = ""
    # Non-blocking advisories attached to any routing decision.
    warnings: list[str] = field(default_factory=list)
    # Populated when stop_reason == "wrong_branch"; gives agents an actionable target.
    suggested_branch: str = ""
    # Populated when the active packet has a verification request (FR-006 gate) —
    # set on verification_pending / verification_failed stops and on task_close
    # after a completed verification, so agents know which VERIFY-… to act on.
    verification_id: str = ""
