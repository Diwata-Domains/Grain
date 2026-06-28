# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Domain models for the recipe step-runner run-state layer.

A *run* is the file-backed state of one execution of a recipe definition. It is
the single source of truth a run resumes from: it records the ordered step
records, the cursor, the run ``mode`` (``operator | auto``) and ``supervision``
level, and the status of the run and each step.

This module is the run-state model only (``apiVersion: grain.recipe-run/v1``):
no cursor advancement, no execution, no I/O. Persistence lives in
``services/recipe_store.py``. The recipe engine is parallel to the SDLC loop and
never touches packet lifecycle code.

Idioms mirror :mod:`grain.domain.workflow_loop` / :mod:`grain.domain.recipe`:
plain ``@dataclass`` + ``__post_init__`` validation + ``VALID_*`` frozensets.
"""

from __future__ import annotations

from dataclasses import dataclass, field

RUN_API_VERSION = "grain.recipe-run/v1"
_RUN_API_MAJOR = "1"

# Single status set, shared by the run and its step records (spec §2.2).
VALID_RUN_STATUSES: frozenset[str] = frozenset(
    {"pending", "running", "awaiting_input", "awaiting_gate", "done", "failed"}
)
VALID_STEP_STATUSES: frozenset[str] = frozenset(
    {"pending", "running", "awaiting_input", "awaiting_gate", "done", "failed"}
)

# How a run is driven; DISTINCT from supervision (supervised|gated|autonomous).
VALID_MODES: frozenset[str] = frozenset({"operator", "auto"})

# Per-step gate values carried from the definition (not actioned in this layer).
VALID_GATES: frozenset[str] = frozenset({"none", "review"})

# Supervision levels copied verbatim from the recipe definition.
VALID_SUPERVISION: frozenset[str] = frozenset({"supervised", "gated", "autonomous"})


def _api_major(api_version: str) -> str:
    """Return the major component of a ``name/vN`` apiVersion string."""
    if not isinstance(api_version, str) or "/v" not in api_version:
        raise ValueError(
            f"malformed apiVersion {api_version!r}; expected '<name>/v<major>'"
        )
    return api_version.rsplit("/v", 1)[1].split(".", 1)[0]


@dataclass
class RecipeStepRecord:
    """State of one recipe step within a run, in recipe step order."""

    id: str
    status: str = "pending"  # ∈ VALID_STEP_STATUSES
    artifact: str | None = None  # relative filename; None until produced
    gate: str = "none"  # "none" | "review"; carried from def, not actioned here
    attempts: int = 0  # incremented by the runner on each (re)run
    started: str | None = None  # ISO-8601 UTC, engine-stamped
    ended: str | None = None  # ISO-8601 UTC, engine-stamped
    error: str | None = None  # set when status == "failed"

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id:
            raise ValueError("step record requires non-empty id")
        if self.status not in VALID_STEP_STATUSES:
            raise ValueError(
                f"invalid step status {self.status!r}; expected one of "
                f"{sorted(VALID_STEP_STATUSES)}"
            )
        if self.gate not in VALID_GATES:
            raise ValueError(
                f"invalid step gate {self.gate!r}; expected one of "
                f"{sorted(VALID_GATES)}"
            )
        if not isinstance(self.attempts, int) or self.attempts < 0:
            raise ValueError("attempts must be >= 0")

    def to_dict(self) -> dict:
        """Emit the §2.2 JSON shape, omitting None/default fields for readability."""
        out: dict = {"id": self.id, "status": self.status}
        if self.artifact is not None:
            out["artifact"] = self.artifact
        if self.attempts:
            out["attempts"] = self.attempts
        if self.gate != "none":
            out["gate"] = self.gate
        if self.started is not None:
            out["started"] = self.started
        if self.ended is not None:
            out["ended"] = self.ended
        if self.error is not None:
            out["error"] = self.error
        return out

    @classmethod
    def from_dict(cls, data: dict) -> RecipeStepRecord:
        """Reconstruct a step record; absent keys fall back to their defaults.

        A missing *required* key (``id``) is surfaced as a clean ``ValueError``
        (F15) rather than a raw ``KeyError`` so an unreadable run.json never
        crashes the engine with a cryptic ``KeyError: 'id'``.
        """
        if not isinstance(data, dict):
            raise ValueError("step record payload must be a mapping")
        try:
            step_id = data["id"]
        except KeyError as exc:
            raise ValueError("step record payload missing required key 'id'") from exc
        return cls(
            id=step_id,
            status=data.get("status", "pending"),
            artifact=data.get("artifact"),
            gate=data.get("gate", "none"),
            attempts=data.get("attempts", 0),
            started=data.get("started"),
            ended=data.get("ended"),
            error=data.get("error"),
        )


@dataclass
class RecipeRun:
    """File-backed state of one recipe run; single source of truth for resume."""

    run_id: str  # "<recipe-id>-NNNN"
    recipe: str  # recipe id
    recipe_api_version: str  # "grain.recipe/v2" (def the run was created from)
    params: dict[str, str]  # resolved run params
    mode: str  # ∈ VALID_MODES; how the run is driven
    supervision: str  # ∈ VALID_SUPERVISION; carried from the def
    status: str  # ∈ VALID_RUN_STATUSES
    cursor: str  # id of the current/next step (final step id on done)
    steps: list[RecipeStepRecord] = field(default_factory=list)
    api_version: str = RUN_API_VERSION
    created: str | None = None  # ISO-8601 UTC
    updated: str | None = None  # ISO-8601 UTC

    def __post_init__(self) -> None:
        if not isinstance(self.run_id, str) or not self.run_id:
            raise ValueError("run requires non-empty run_id")
        if not isinstance(self.recipe, str) or not self.recipe:
            raise ValueError("run requires non-empty recipe id")
        if self.mode not in VALID_MODES:
            raise ValueError(
                f"invalid mode {self.mode!r}; expected one of {sorted(VALID_MODES)}"
            )
        if self.supervision not in VALID_SUPERVISION:
            raise ValueError(
                f"invalid supervision {self.supervision!r}; expected one of "
                f"{sorted(VALID_SUPERVISION)}"
            )
        if self.status not in VALID_RUN_STATUSES:
            raise ValueError(
                f"invalid run status {self.status!r}; expected one of "
                f"{sorted(VALID_RUN_STATUSES)}"
            )
        if not self.steps:
            raise ValueError("run requires at least one step record")
        ids = [s.id for s in self.steps]
        if len(ids) != len(set(ids)):
            raise ValueError("step record ids must be unique within a run")
        if self.cursor not in ids:
            raise ValueError(f"cursor {self.cursor!r} not among step ids {ids}")

    def step(self, step_id: str) -> RecipeStepRecord:
        """Return the step record with ``step_id``; raise ``KeyError`` if absent."""
        for record in self.steps:
            if record.id == step_id:
                return record
        raise KeyError(step_id)

    def to_dict(self) -> dict:
        """Emit exactly the §2.2 run.json shape (JSON uses apiVersion casing)."""
        return {
            "apiVersion": self.api_version,
            "run_id": self.run_id,
            "recipe": self.recipe,
            "recipe_apiVersion": self.recipe_api_version,
            "params": dict(self.params),
            "mode": self.mode,
            "supervision": self.supervision,
            "status": self.status,
            "cursor": self.cursor,
            "created": self.created,
            "updated": self.updated,
            "steps": [s.to_dict() for s in self.steps],
        }

    @classmethod
    def from_dict(cls, data: dict) -> RecipeRun:
        """Reconstruct a run from its run.json dict.

        Rejects a payload whose ``apiVersion`` major differs from this engine's
        supported major (engine contract, spec §1.5).
        """
        if not isinstance(data, dict):
            raise ValueError("run payload must be a mapping")
        api_version = data.get("apiVersion")
        if api_version is None:
            raise ValueError(
                f"run payload missing 'apiVersion'; expected major {_RUN_API_MAJOR}"
            )
        if _api_major(api_version) != _RUN_API_MAJOR:
            raise ValueError(
                f"unsupported run apiVersion {api_version!r}; "
                f"expected major {_RUN_API_MAJOR} ({RUN_API_VERSION})"
            )
        steps = [RecipeStepRecord.from_dict(s) for s in data.get("steps", [])]
        # F15: a run.json missing a required key (e.g. ``cursor``) must surface a
        # clean ``ValueError`` ("unreadable run") rather than a cryptic raw
        # ``KeyError: 'cursor'`` escaping to the CLI catch-all as exit 1.
        try:
            return cls(
                run_id=data["run_id"],
                recipe=data["recipe"],
                recipe_api_version=data["recipe_apiVersion"],
                params=dict(data.get("params", {})),
                mode=data["mode"],
                supervision=data["supervision"],
                status=data["status"],
                cursor=data["cursor"],
                steps=steps,
                api_version=api_version,
                created=data.get("created"),
                updated=data.get("updated"),
            )
        except KeyError as exc:
            raise ValueError(
                f"run payload missing required key {exc.args[0]!r}"
            ) from exc
