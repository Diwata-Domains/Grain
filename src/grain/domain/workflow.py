"""Domain models for workflow runner state evaluation."""

from dataclasses import dataclass, field


@dataclass
class WorkflowTaskState:
    """Normalized task signal extracted from backlog/current task state."""

    task_ref: str
    status: str
    source: str


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
