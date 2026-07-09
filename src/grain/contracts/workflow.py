# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT
"""Grain's published workflow vocabulary — protocol, run, gate, artifact, stop_reason.

Grain owns the workflow capability, so Grain publishes the words for it
(`Diwata-Infra/docs/canonical/capability_register.md`;
`docs/superpowers/specs/2026-07-09-entity-boundaries-design.md` §5.1). Anything that wants to speak
about workflows — Diwa's Missions over Postgres, a familiar driving Grain headlessly — imports these
types rather than inventing a parallel set.

Three rules hold this module in place:

**Types, not code.** No reducer, no store, no I/O, stdlib only. §11 of the spec draws the line:
contracts share types, not code. The `RunStore` port and the `advance()` reducer live in
`grain.engine`, which is a different promise.

**Off the CLI import graph.** Nothing under `grain.cli` may import this module. The console script
is `grain = "grain.cli:cli"`, and `cli()` (`cli/__init__.py:317-334`) wraps only `main()` — it runs
*after* import. An import-time fault here would print a traceback no handler can catch, on
`grain status`, which is the live demo's first command. `tests/test_contracts_workflow.py` asserts
the separation.

**Vocabulary already in force.** The enums are not a fresh opinion. `Gate`, `RunStatus`,
`StepStatus`, `Mode` and `Supervision` mirror the `VALID_*` frozensets in `domain/recipe_run.py`;
`StopReason` mirrors the twenty `STOP_*` constants in `services/workflow_service.py`. A contract that
drifts from its callers is worse than no contract, so tests derive both rosters from source.

The serialization here is `grain.workflow-run/v1` and speaks of a **protocol**. The recipe engine's
on-disk `grain.recipe-run/v1` speaks of a **recipe**; mapping between them belongs to P37-T17, which
owns byte-identical compatibility for existing `run.json` files.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

WORKFLOW_RUN_API_VERSION = "grain.workflow-run/v1"
PROTOCOL_API_VERSION = "grain.protocol/v1"
_RUN_API_MAJOR = "1"


def _api_major(api_version: str) -> str:
    """Return the major component of a ``name/vN`` apiVersion string."""
    if not isinstance(api_version, str) or "/v" not in api_version:
        raise ValueError(f"malformed apiVersion {api_version!r}; expected '<name>/v<major>'")
    return api_version.rsplit("/v", 1)[1].split(".", 1)[0]


class Gate(str, Enum):
    """Whether a step halts for a human. Mirrors VALID_GATES."""

    NONE = "none"
    REVIEW = "review"


class RunStatus(str, Enum):
    """Mirrors VALID_RUN_STATUSES."""

    PENDING = "pending"
    RUNNING = "running"
    AWAITING_INPUT = "awaiting_input"
    AWAITING_GATE = "awaiting_gate"
    DONE = "done"
    FAILED = "failed"


class StepStatus(str, Enum):
    """Mirrors VALID_STEP_STATUSES. Same members as RunStatus, deliberately a distinct type."""

    PENDING = "pending"
    RUNNING = "running"
    AWAITING_INPUT = "awaiting_input"
    AWAITING_GATE = "awaiting_gate"
    DONE = "done"
    FAILED = "failed"


class Mode(str, Enum):
    """How a run is driven. Distinct from Supervision. Mirrors VALID_MODES."""

    OPERATOR = "operator"
    AUTO = "auto"


class Supervision(str, Enum):
    """How much autonomy a protocol grants. Mirrors VALID_SUPERVISION."""

    SUPERVISED = "supervised"
    GATED = "gated"
    AUTONOMOUS = "autonomous"


class StopReason(str, Enum):
    """Why the workflow will not advance. Mirrors the STOP_* constants in workflow_service.py.

    Loop-level reasons (`steps_limit_reached`, `supervision_required`, `invocation_failed`,
    `no_state_change`) are NOT here: they belong to the `workflow loop` command's JSON payload,
    never to a `WorkflowEvaluation`.
    """

    REQUIRED_DOCS_MISSING = "required_docs_missing"
    REQUIRED_DOCS_INVALID = "required_docs_invalid"
    PROJECT_COMPLETE = "project_complete"
    BOOTSTRAP_INCOMPLETE = "bootstrap_incomplete"
    PREVIOUS_PHASE_NOT_CLOSED = "previous_phase_not_closed"
    STALE_TASK_POINTER = "stale_task_pointer"
    WORKFLOW_STATE_DRIFT = "workflow_state_drift"
    TASK_BLOCKED = "task_blocked"
    TASK_NEEDS_FIX = "task_needs_fix"
    REVIEW_ARTIFACTS_INCOMPLETE = "review_artifacts_incomplete"
    REVIEW_CLOSE_BLOCKED = "review_close_blocked"
    EXECUTION_IN_FLIGHT = "execution_in_flight"
    CONFLICTING_NEXT_ACTIONS = "conflicting_next_actions"
    PACKET_REQUIRED = "packet_required"
    PHASE_HAS_NO_TASKS = "phase_has_no_tasks"
    PHASE_BOUNDARY_REVIEW_CLOSE_REQUIRED = "phase_boundary_review_close_required"
    TASK_PLANNING_REQUIRED = "task_planning_required"
    WRONG_BRANCH = "wrong_branch"
    VERIFICATION_PENDING = "verification_pending"
    VERIFICATION_FAILED = "verification_failed"


@dataclass(frozen=True)
class Artifact:
    """What a step produced. `path` is relative to the run; a store decides what that means."""

    path: str

    def __post_init__(self) -> None:
        if not isinstance(self.path, str) or not self.path:
            raise ValueError("artifact requires a non-empty path")


@dataclass(frozen=True)
class StepSpec:
    """A step as *declared* by a protocol, before any run exists."""

    id: str
    gate: Gate = Gate.NONE

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id:
            raise ValueError("step spec requires non-empty id")
        object.__setattr__(self, "gate", Gate(self.gate))


@dataclass(frozen=True)
class Protocol:
    """A reusable template: the steps a run will walk, in order."""

    id: str
    api_version: str = PROTOCOL_API_VERSION
    steps: tuple[StepSpec, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id:
            raise ValueError("protocol requires non-empty id")
        object.__setattr__(self, "steps", tuple(self.steps))
        ids = [s.id for s in self.steps]
        if len(ids) != len(set(ids)):
            raise ValueError("protocol step ids must be unique")

    def step(self, step_id: str) -> StepSpec:
        for spec in self.steps:
            if spec.id == step_id:
                return spec
        raise KeyError(step_id)


@dataclass(frozen=True)
class StepRecord:
    """State of one step within a run, in protocol step order."""

    id: str
    status: StepStatus = StepStatus.PENDING
    artifact: Artifact | None = None
    gate: Gate = Gate.NONE
    attempts: int = 0
    started: str | None = None
    ended: str | None = None
    error: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id:
            raise ValueError("step record requires non-empty id")
        object.__setattr__(self, "status", StepStatus(self.status))
        object.__setattr__(self, "gate", Gate(self.gate))
        if not isinstance(self.attempts, int) or isinstance(self.attempts, bool) or self.attempts < 0:
            raise ValueError("attempts must be an int >= 0")

    def to_dict(self) -> dict[str, Any]:
        """Omit defaults, mirroring the readability of `RecipeStepRecord.to_dict`."""
        out: dict[str, Any] = {"id": self.id, "status": self.status.value}
        if self.artifact is not None:
            out["artifact"] = self.artifact.path
        if self.attempts:
            out["attempts"] = self.attempts
        if self.gate is not Gate.NONE:
            out["gate"] = self.gate.value
        for key in ("started", "ended", "error"):
            value = getattr(self, key)
            if value is not None:
                out[key] = value
        return out

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StepRecord:
        if not isinstance(data, dict):
            raise ValueError("step record payload must be a mapping")
        try:
            step_id = data["id"]
        except KeyError as exc:
            raise ValueError("step record payload missing required key 'id'") from exc
        artifact = data.get("artifact")
        return cls(
            id=step_id,
            status=StepStatus(data.get("status", "pending")),
            artifact=Artifact(path=artifact) if artifact is not None else None,
            gate=Gate(data.get("gate", "none")),
            attempts=data.get("attempts", 0),
            started=data.get("started"),
            ended=data.get("ended"),
            error=data.get("error"),
        )


@dataclass(frozen=True)
class Run:
    """One execution of a protocol. The single source of truth for resuming it."""

    run_id: str
    protocol: str
    protocol_api_version: str
    params: dict[str, str] = field(default_factory=dict)
    mode: Mode = Mode.OPERATOR
    supervision: Supervision = Supervision.SUPERVISED
    status: RunStatus = RunStatus.PENDING
    cursor: str = ""
    steps: tuple[StepRecord, ...] = ()
    api_version: str = WORKFLOW_RUN_API_VERSION
    created: str | None = None
    updated: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.run_id, str) or not self.run_id:
            raise ValueError("run requires non-empty run_id")
        if not isinstance(self.protocol, str) or not self.protocol:
            raise ValueError("run requires non-empty protocol id")
        object.__setattr__(self, "mode", Mode(self.mode))
        object.__setattr__(self, "supervision", Supervision(self.supervision))
        object.__setattr__(self, "status", RunStatus(self.status))
        object.__setattr__(self, "steps", tuple(self.steps))
        object.__setattr__(self, "params", dict(self.params))
        if not self.steps:
            raise ValueError("run requires at least one step record")
        ids = [s.id for s in self.steps]
        if len(ids) != len(set(ids)):
            raise ValueError("step record ids must be unique within a run")
        if self.cursor not in ids:
            raise ValueError(f"cursor {self.cursor!r} not among step ids {ids}")

    def step(self, step_id: str) -> StepRecord:
        for record in self.steps:
            if record.id == step_id:
                return record
        raise KeyError(step_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "apiVersion": self.api_version,
            "run_id": self.run_id,
            "protocol": self.protocol,
            "protocol_apiVersion": self.protocol_api_version,
            "params": dict(self.params),
            "mode": self.mode.value,
            "supervision": self.supervision.value,
            "status": self.status.value,
            "cursor": self.cursor,
            "created": self.created,
            "updated": self.updated,
            "steps": [s.to_dict() for s in self.steps],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Run:
        """Reconstruct a run. A missing key surfaces as ValueError, never a raw KeyError."""
        if not isinstance(data, dict):
            raise ValueError("run payload must be a mapping")
        api_version = data.get("apiVersion")
        if api_version is None:
            raise ValueError(f"run payload missing 'apiVersion'; expected major {_RUN_API_MAJOR}")
        if _api_major(api_version) != _RUN_API_MAJOR:
            raise ValueError(
                f"unsupported run apiVersion {api_version!r}; "
                f"expected major {_RUN_API_MAJOR} ({WORKFLOW_RUN_API_VERSION})"
            )
        try:
            return cls(
                run_id=data["run_id"],
                protocol=data["protocol"],
                protocol_api_version=data["protocol_apiVersion"],
                params=data.get("params", {}),
                mode=Mode(data["mode"]),
                supervision=Supervision(data["supervision"]),
                status=RunStatus(data["status"]),
                cursor=data["cursor"],
                steps=tuple(StepRecord.from_dict(s) for s in data.get("steps", [])),
                api_version=api_version,
                created=data.get("created"),
                updated=data.get("updated"),
            )
        except KeyError as exc:
            raise ValueError(f"run payload missing required key {exc.args[0]!r}") from exc


__all__ = [
    "Artifact",
    "Gate",
    "Mode",
    "PROTOCOL_API_VERSION",
    "Protocol",
    "Run",
    "RunStatus",
    "StepRecord",
    "StepSpec",
    "StepStatus",
    "StopReason",
    "Supervision",
    "WORKFLOW_RUN_API_VERSION",
]
