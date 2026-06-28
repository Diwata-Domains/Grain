# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Operator-mode execution engine for the recipe step-runner.

:class:`RecipeService` is the deterministic, offline state machine that drives a
``grain.recipe/v2`` definition forward one inspectable step at a time. It is a
PARALLEL engine: it never touches the SDLC workflow-state evaluator, task
packets, or the review/close loop. It does no network I/O and needs no API key.

Responsibilities (this packet):
  * resolve + enumerate recipes (workspace ``docs/recipes/<id>/`` + bundled),
  * ``start_run`` — create a run (``status=pending``, cursor on the first step,
    NO auto-advance) under ``docs/recipes/runs/<run-id>/``,
  * ``next`` — advance exactly one step: render the current step's prompt with
    its scoped declared inputs and pause at ``awaiting_input`` (operator pause,
    NOT a failure) until the human/agent writes the output artifact; once the
    artifact exists, mark the step done and advance the cursor, entering
    ``awaiting_gate`` at a ``gate: review`` step and ``run_complete`` at the end,
  * ``resume`` — re-read ``run.json`` (the single source of truth) and continue
    from the persisted cursor in the recorded ``mode``.

The engine NEVER writes a step's output artifact itself (auto mode is T05); a
missing output is the ``awaiting_input`` pause, not a ``failed`` run.

Idioms mirror :mod:`grain.domain.workflow_loop`: ``@dataclass`` results with
``__post_init__`` validation and ``VALID_*`` frozensets.
"""

from __future__ import annotations

import os
import re
import shlex
import subprocess
from dataclasses import dataclass, field, replace
from pathlib import Path

from grain.domain.recipe import RECIPE_API_VERSION as _RECIPE_API_VERSION
from grain.domain.recipe import (
    RecipeDefinition,
    RecipeSchemaError,
    RecipeStep,
    ensure_output_within,
    load_recipe,
)
from grain.domain.recipe_run import RUN_API_VERSION as _RUN_API_VERSION
from grain.domain.recipe_run import (
    VALID_GATES,
    VALID_MODES,
    VALID_RUN_STATUSES,
    VALID_STEP_STATUSES,
    RecipeRun,
)
from grain.domain.workflow_loop import WorkflowLoopAgentConfig
from grain.services import recipe_store
from grain.services.workflow_loop_config_service import load_workflow_loop_config

# --- Status / vocabulary re-exports (deliverable_spec §3) --------------------
VALID_RUN_STATUS: frozenset[str] = VALID_RUN_STATUSES
VALID_STEP_STATUS: frozenset[str] = VALID_STEP_STATUSES
VALID_GATE_KINDS: frozenset[str] = VALID_GATES
RECIPE_RUN_API_VERSION: str = _RUN_API_VERSION
RECIPE_API_VERSION: str = _RECIPE_API_VERSION
RUNS_DIR = "docs/recipes/runs"
RECIPES_DIR = "docs/recipes"

# Engine outcome vocabulary (spec §3.1). ``awaiting_input`` is a STATUS, never an
# outcome: the operator pause is returned as ``prompt_ready`` + status
# ``awaiting_input``.
VALID_NEXT_OUTCOMES: frozenset[str] = frozenset(
    {
        "started",
        "prompt_ready",
        "advanced",
        "awaiting_gate",
        "run_complete",
        "noop",
    }
)

_PARAMS_INPUT = "params"
_INLINE_PREFIX = "inline:"
_TOKEN_RE = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")
_STEPS_PREFIX = "steps."

# Auto-mode (T09) tunables / conventions.
DEFAULT_AGENT_TIMEOUT_S = 600  # bounded; never run an unattended agent forever.
_ERROR_DETAIL_LIMIT = 2000  # truncate captured stdout/stderr in the error record.
# Env vars the engine exports to the agent subprocess so it knows where to write
# the step's `output` artifact (the absolute path operator-mode render computes).
_ENV_OUTPUT = "GRAIN_RECIPE_OUTPUT"
_ENV_RUN_DIR = "GRAIN_RECIPE_RUN_DIR"


# --- Typed errors ------------------------------------------------------------
class RecipeEngineError(Exception):
    """Base class for EVERY typed error the recipe engine raises (F14).

    Each engine error subclasses this so the CLI run verbs can translate the
    WHOLE family uniformly to a :mod:`grain.domain.errors` type (and thus a spec
    exit code) with a single ``except RecipeEngineError`` catch. This is what
    guarantees no engine error — including any added later — falls through to the
    CLI catch-all as a bare ``Error: ...`` exit 1, and that no raw
    ``KeyError`` / ``FileNotFoundError`` / ``UnicodeDecodeError`` ever escapes.
    """


class RecipeNotFoundError(RecipeEngineError):
    """No recipe with the given id under workspace or bundled recipes."""


class RunNotFoundError(RecipeEngineError):
    """No run with the given id under docs/recipes/runs/."""


class MissingParamError(RecipeEngineError):
    """A required recipe parameter was not supplied to start_run."""


class InputNotReadyError(RecipeEngineError):
    """A declared input references a prior step that is not yet ``done``."""


class UndeclaredInputError(RecipeEngineError):
    """A ``{{steps.<id>}}`` references a step NOT in the cursor step's inputs."""


class UnknownTokenError(RecipeEngineError):
    """A ``{{...}}`` token resolves to neither a param nor a valid steps.<id>."""


class RecipeDefinitionChangedError(RecipeEngineError):
    """The live ``recipe.yaml`` no longer matches the run's persisted steps.

    Raised (F8) when a recipe definition is edited mid-run so that its step set /
    order — or its captured ``recipe_apiVersion`` — diverges from what the run was
    created against. Surfacing this as a TYPED error keeps a desync from stranding
    the run with a raw ``KeyError`` / ``ValueError`` deep in the engine.
    """


class ArtifactDecodeError(RecipeEngineError):
    """A prior step artifact (or step output) is not decodable UTF-8 text (F12).

    The engine reads artifacts as UTF-8; a binary / non-UTF8 file yields this
    clean typed error instead of letting a raw ``UnicodeDecodeError`` escape.
    """


class GateStateError(RecipeEngineError):
    """A gate decision (approve/reject) was requested on a non-``awaiting_gate`` run."""


def _recipe_api_major(version: str) -> str:
    """Major component of a ``<name>/v<major>`` recipe apiVersion string."""
    if not isinstance(version, str) or "/v" not in version:
        raise RecipeDefinitionChangedError(
            f"malformed recipe apiVersion {version!r}; expected '<name>/v<major>'"
        )
    return version.rsplit("/v", 1)[1].split(".", 1)[0]


def _read_artifact_text(path: Path, *, label: str) -> str:
    """Read ``path`` as UTF-8, translating a decode failure into a typed error (F12)."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ArtifactDecodeError(
            f"{label} {path.name!r} is not valid UTF-8 text "
            f"(binary or wrong-encoding artifact): {exc}"
        ) from exc


# --- Result dataclasses ------------------------------------------------------
@dataclass
class ScopedInput:
    """One declared input surfaced to the step."""

    kind: str  # "params" | "artifact"
    id: str  # "params" or the prior step id
    path: str  # absolute path ("" for params)
    content: str  # rendered/loaded content (params -> formatted k=v block)

    def __post_init__(self) -> None:
        if self.kind not in {"params", "artifact"}:
            raise ValueError(
                f"invalid ScopedInput kind {self.kind!r}; expected 'params' or 'artifact'"
            )


@dataclass
class RecipeSummary:
    """One enumerated recipe (for list_recipes / the T04 CLI ``list``)."""

    id: str
    name: str
    source: str  # "bundled" | "workspace"
    category: str = ""
    description: str = ""

    def __post_init__(self) -> None:
        if self.source not in {"bundled", "workspace"}:
            raise ValueError(
                f"invalid RecipeSummary source {self.source!r}; "
                f"expected 'bundled' or 'workspace'"
            )


@dataclass
class NextResult:
    """Outcome of one RecipeService.start_run() / next() / resume() call."""

    run_id: str
    outcome: str  # ∈ VALID_NEXT_OUTCOMES
    cursor: str | None  # step id the run rests on (None when run done)
    step_id: str | None
    run_status: str  # ∈ VALID_RUN_STATUS
    prompt: str = ""  # rendered prompt text, when outcome == "prompt_ready"
    output_path: str = ""  # absolute path the artifact must be written to
    inputs: list[ScopedInput] = field(default_factory=list)
    gate: str = "none"  # ∈ VALID_GATE_KINDS; "review" when awaiting_gate
    message: str = ""

    def __post_init__(self) -> None:
        if self.outcome not in VALID_NEXT_OUTCOMES:
            raise ValueError(
                f"invalid outcome {self.outcome!r}; expected one of "
                f"{sorted(VALID_NEXT_OUTCOMES)}"
            )
        if self.run_status not in VALID_RUN_STATUS:
            raise ValueError(
                f"invalid run_status {self.run_status!r}; expected one of "
                f"{sorted(VALID_RUN_STATUS)}"
            )
        if self.gate not in VALID_GATE_KINDS:
            raise ValueError(
                f"invalid gate {self.gate!r}; expected one of {sorted(VALID_GATE_KINDS)}"
            )
        if self.outcome == "prompt_ready":
            if not self.prompt or not self.output_path:
                raise ValueError(
                    "prompt_ready result requires non-empty prompt and output_path"
                )
            if self.run_status != "awaiting_input":
                raise ValueError(
                    "prompt_ready result requires run_status == 'awaiting_input'"
                )


# --- Auto-mode (T09) result helpers -----------------------------------------
@dataclass
class AutoStepOutcome:
    """Outcome of executing ONE cursor step in auto mode (spec §2.2).

    A per-step summary the auto loop produces before reusing the operator-mode
    advance/gate logic. ``status`` is constrained to the run/step status set so
    auto mode never invents new vocabulary.
    """

    step_id: str
    status: str  # ∈ VALID_STEP_STATUS: "done" | "awaiting_gate" | "failed"
    artifact: str = ""  # relative artifact name when produced
    attempts: int = 0
    error: str = ""  # captured stderr/summary on failure

    def __post_init__(self) -> None:
        if self.status not in VALID_STEP_STATUS:
            raise ValueError(
                f"invalid AutoStepOutcome status {self.status!r}; expected one of "
                f"{sorted(VALID_STEP_STATUS)}"
            )
        if not isinstance(self.attempts, int) or self.attempts < 0:
            raise ValueError("AutoStepOutcome attempts must be >= 0")


@dataclass
class _AgentInvocation:
    """Captured result of one agent subprocess call (internal)."""

    returncode: int | None  # None on timeout
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False


def resolve_recipe_agent(
    root: Path,
    *,
    step_model: str = "",
) -> WorkflowLoopAgentConfig:
    """Resolve the auto-mode agent from the workspace runtime config (spec §2.1).

    Reuses the canonical ``docs/runtime/workflow_loop.yaml`` shape (and its
    loader) rather than defining a new agent-config format; the recipe runner
    drives a single agent per step, so the loop's ``executor`` stage agent is
    used. ``step_model`` (the per-step recipe ``model:`` key) biases the model
    passed to the agent when set, overriding the config's model.

    Raises a typed :class:`grain.domain.errors.ForgeError` (``MissingPathError``
    on a missing config, ``ConfigError`` on an invalid one) BEFORE any step runs.
    """
    config = load_workflow_loop_config(Path(root))
    agent = config.stages.executor
    if step_model:
        agent = replace(agent, model=step_model)
    return agent


def _build_agent_argv(agent: WorkflowLoopAgentConfig) -> list[str]:
    """Build the non-shell argv for an agent config (spec §2.3).

    ``command`` mode is split into an argument list (no ``shell=True``);
    ``shortcut`` mode maps ``claude``/``codex`` to their argv, appending
    ``--model <model>`` when a model is set. No injectable shell string is ever
    constructed.
    """
    if agent.mode == "command":
        argv = shlex.split(agent.command)
        if not argv:
            raise ValueError("agent command is empty after parsing")
        return argv
    # shortcut mode
    argv = [agent.shortcut]
    if agent.model:
        argv += ["--model", agent.model]
    return argv


def _default_bundled_root() -> Path:
    """Package-relative default for bundled recipes (``src/grain/data/recipes``)."""
    return Path(__file__).resolve().parent.parent / "data" / "recipes"


def _format_params(params: dict[str, str]) -> str:
    """Render run params as a deterministic ``key=value`` block."""
    return "\n".join(f"{key}={params[key]}" for key in sorted(params))


def _artifact_present_nonempty(path: Path) -> bool:
    """True iff ``path`` is a non-empty file (the completion gate, F2).

    Completion is NOT bare existence: an artifact must exist AND carry content
    for the step to count as done. A zero-byte file is treated as not-yet-done.
    """
    try:
        return path.is_file() and path.stat().st_size > 0
    except OSError:
        return False


class RecipeService:
    """Operator-mode (offline, deterministic) recipe step-runner engine."""

    def __init__(
        self, workspace_root: Path, bundled_recipes_root: Path | None = None
    ) -> None:
        self.workspace_root = Path(workspace_root)
        self.bundled_recipes_root = (
            Path(bundled_recipes_root)
            if bundled_recipes_root is not None
            else _default_bundled_root()
        )

    # --- resolution / enumeration -------------------------------------------
    def _workspace_recipes_dir(self) -> Path:
        return self.workspace_root / RECIPES_DIR

    def _recipe_dir(self, recipe_id: str) -> Path:
        """Return the directory holding ``recipe.yaml`` for ``recipe_id``.

        Workspace ``docs/recipes/<id>/`` takes precedence over bundled.
        Raises :class:`RecipeNotFoundError` if neither holds a ``recipe.yaml``.
        """
        workspace_dir = self._workspace_recipes_dir() / recipe_id
        if (workspace_dir / "recipe.yaml").is_file():
            return workspace_dir
        bundled_dir = self.bundled_recipes_root / recipe_id
        if (bundled_dir / "recipe.yaml").is_file():
            return bundled_dir
        raise RecipeNotFoundError(
            f"no recipe {recipe_id!r} under {self._workspace_recipes_dir()} or "
            f"{self.bundled_recipes_root}"
        )

    def resolve(self, recipe_id: str) -> RecipeDefinition:
        """Find + parse a recipe by id (workspace first, then bundled).

        Enforces two start-time invariants so a run can never be stranded later:

        * **F5 (dir == id):** the parsed ``id`` MUST equal the directory the
          recipe was resolved from. Resolution keys on the directory name while
          persistence keys on ``definition.id``; requiring them equal means
          resolve-by-dir and persist-by-id can never diverge into an orphaned run.
        * **F11 (prompt files exist):** every path-based step ``prompt:`` must
          exist now, failing fast with a typed :class:`RecipeSchemaError` rather
          than mid-run via an unguarded ``read_text``.
        """
        recipe_dir = self._recipe_dir(recipe_id)
        definition = load_recipe(recipe_dir / "recipe.yaml")
        if definition.id != recipe_dir.name:
            raise RecipeSchemaError(
                f"recipe id {definition.id!r} does not match its directory "
                f"{recipe_dir.name!r}; a recipe must live in "
                f"docs/recipes/<id>/recipe.yaml with id == <id>"
            )
        self._validate_prompt_files(definition, recipe_dir)
        return definition

    @staticmethod
    def _validate_prompt_files(
        definition: RecipeDefinition, recipe_dir: Path
    ) -> None:
        """Fail fast (F11) if any path-based step ``prompt:`` is missing on disk."""
        for step in definition.steps:
            if step.prompt.startswith(_INLINE_PREFIX):
                continue
            prompt_path = recipe_dir / step.prompt
            if not prompt_path.is_file():
                raise RecipeSchemaError(
                    f"recipe {definition.id!r} step {step.id!r} prompt file "
                    f"{step.prompt!r} not found at {str(prompt_path)!r}"
                )

    def _resolve_for_run(self, run: RecipeRun) -> RecipeDefinition:
        """Resolve the recipe for a run, asserting it has not desynced (F8).

        A ``recipe.yaml`` edited mid-run must not strand the run with a raw
        ``KeyError`` / ``ValueError``. This re-resolves the definition and checks
        it still matches the run's persisted state:

        * the captured ``recipe_apiVersion`` major must match this engine's, and
        * the definition's step ids (in order) must equal the run's step records.

        Any divergence raises a typed :class:`RecipeDefinitionChangedError`.
        """
        definition = self.resolve(run.recipe)
        if _recipe_api_major(run.recipe_api_version) != _recipe_api_major(
            RECIPE_API_VERSION
        ):
            raise RecipeDefinitionChangedError(
                f"run {run.run_id!r} was created against recipe apiVersion "
                f"{run.recipe_api_version!r}, incompatible with this engine's "
                f"{RECIPE_API_VERSION!r}; start a new run"
            )
        def_ids = [step.id for step in definition.steps]
        run_ids = [record.id for record in run.steps]
        if def_ids != run_ids:
            raise RecipeDefinitionChangedError(
                f"recipe {run.recipe!r} definition changed since run "
                f"{run.run_id!r} started: live steps {def_ids} no longer match "
                f"the run's persisted steps {run_ids}; resolve the desync or "
                f"start a new run"
            )
        return definition

    def list_recipes(self) -> list[RecipeSummary]:
        """Enumerate bundled + workspace recipes (workspace overrides bundled)."""
        summaries: dict[str, RecipeSummary] = {}
        # Bundled first, so workspace recipes override by id.
        for source, root in (
            ("bundled", self.bundled_recipes_root),
            ("workspace", self._workspace_recipes_dir()),
        ):
            if not root.is_dir():
                continue
            for entry in sorted(root.iterdir(), key=lambda p: p.name):
                if not entry.is_dir() or entry.name == "runs":
                    continue
                if not (entry / "recipe.yaml").is_file():
                    continue
                try:
                    definition = load_recipe(entry / "recipe.yaml")
                except Exception:
                    # A malformed recipe must not break enumeration of the rest.
                    continue
                # F5: a recipe whose id does not match its directory is not
                # resolvable (resolve enforces dir == id), so it must not be
                # advertised as runnable.
                if definition.id != entry.name:
                    continue
                summaries[definition.id] = RecipeSummary(
                    id=definition.id,
                    name=definition.name,
                    source=source,
                    category=definition.category,
                    description=definition.description,
                )
        return [summaries[key] for key in sorted(summaries)]

    # --- run lifecycle ------------------------------------------------------
    def start_run(
        self, recipe_id: str, params: dict[str, str], *, mode: str = "operator"
    ) -> NextResult:
        """Validate params, create the run, return outcome ``started`` (no advance)."""
        if mode not in VALID_MODES:
            raise ValueError(
                f"invalid mode {mode!r}; expected one of {sorted(VALID_MODES)}"
            )
        definition = self.resolve(recipe_id)
        params = dict(params)

        # Validate required params BEFORE any run dir is created.
        for param in definition.params:
            if not param.required:
                continue
            value = params.get(param.id)
            if value is None or (isinstance(value, str) and not value.strip()):
                raise MissingParamError(
                    f"recipe {recipe_id!r} requires param {param.id!r}"
                )

        run = recipe_store.create_run(
            self.workspace_root, definition, params, mode=mode
        )
        first_step_id = definition.steps[0].id
        return NextResult(
            run_id=run.run_id,
            outcome="started",
            cursor=first_step_id,
            step_id=first_step_id,
            run_status="pending",
            message=f"run {run.run_id} created; call next to render the first step",
        )

    def _load_run(self, run_id: str) -> RecipeRun:
        try:
            return recipe_store.load_run(self.workspace_root, run_id)
        except FileNotFoundError as exc:
            raise RunNotFoundError(f"no run {run_id!r}") from exc

    def next(self, run_id: str) -> NextResult:
        """Advance the run by exactly one step (operator semantics, spec §6)."""
        run = self._load_run(run_id)

        # 1. Already paused at a gate — report, do not write.
        if run.status == "awaiting_gate":
            return NextResult(
                run_id=run.run_id,
                outcome="noop",
                cursor=run.cursor,
                step_id=run.cursor,
                run_status="awaiting_gate",
                gate="review",
                message="awaiting gate approval",
            )

        # 2. Run already complete.
        if run.status == "done":
            return NextResult(
                run_id=run.run_id,
                outcome="run_complete",
                cursor=None,
                step_id=run.cursor,
                run_status="done",
                message="run already complete",
            )

        # F8: re-resolve against the run, rejecting a mid-run definition desync
        # as a typed error instead of a raw KeyError/ValueError deep in advance.
        definition = self._resolve_for_run(run)
        recipe_dir = self._recipe_dir(run.recipe)
        step_def = self._step_def(definition, run.cursor)
        record = run.step(run.cursor)
        directory = recipe_store.run_dir(self.workspace_root, run.run_id)
        # F1: confirm the declared output resolves strictly inside the run dir.
        output_path = ensure_output_within(directory, step_def.output, label="step")

        # 4. Completion (F2/F4): a step is done ONLY when its output artifact
        #    EXISTS and is NON-EMPTY, the step record is not ``failed``, and the
        #    run is not ``failed``. A failed run/step must take an explicit
        #    re-run path (re-render + re-author) — a left-behind output never
        #    silently counts as completion.
        if (
            run.status != "failed"
            and record.status != "failed"
            and _artifact_present_nonempty(output_path)
        ):
            return self._complete_and_advance(
                run, definition, step_def, record, content=None
            )

        # 5. Output missing/empty (or re-entering a failed step) -> operator-mode
        #    pause (render + surface, no failure). The engine writes NOTHING.
        scoped_inputs = self._assemble_inputs(run, step_def, directory)
        prompt_text = self._render_prompt(
            run, step_def, recipe_dir, directory
        )

        # Increment attempts only on the FIRST transition into the pause for
        # this step (re-invocation before the artifact lands must not double-count).
        if record.status != "awaiting_input":
            record.attempts += 1
        record.status = "awaiting_input"
        if record.started is None:
            record.started = recipe_store._utc_now()
        run.status = "awaiting_input"
        recipe_store.save_run(self.workspace_root, run)

        return NextResult(
            run_id=run.run_id,
            outcome="prompt_ready",
            cursor=step_def.id,
            step_id=step_def.id,
            run_status="awaiting_input",
            prompt=prompt_text,
            output_path=str(output_path),
            inputs=scoped_inputs,
            message=f"step {step_def.id} awaiting output artifact",
        )

    def _complete_and_advance(
        self,
        run: RecipeRun,
        definition: RecipeDefinition,
        step_def: RecipeStep,
        record,
        *,
        content: str | None,
    ) -> NextResult:
        """Mark the cursor step done, then gate / advance / complete (spec §3.1).

        Shared by operator :meth:`next` and auto :meth:`run_auto`.

        * ``content is None`` (operator): the human already authored the artifact
          on disk; the engine NEVER writes a step artifact in operator mode, so
          only ``run.json`` is persisted (via :func:`recipe_store.save_run`).
        * ``content`` supplied (auto): the artifact is (re)written ATOMICALLY via
          :func:`recipe_store.write_step_artifact` (artifact lands first, then
          ``run.json``), making the documented atomic-write invariant live.
        """
        record.status = "done"
        record.artifact = step_def.output
        record.ended = recipe_store._utc_now()
        if record.attempts == 0:
            record.attempts = 1

        def _persist() -> None:
            if content is None:
                recipe_store.save_run(self.workspace_root, run)
            else:
                recipe_store.write_step_artifact(
                    self.workspace_root, run, step_def.id, content, step_def.output
                )

        if step_def.gate == "review":
            record.status = "awaiting_gate"
            run.status = "awaiting_gate"
            # cursor unchanged
            _persist()
            return NextResult(
                run_id=run.run_id,
                outcome="awaiting_gate",
                cursor=run.cursor,
                step_id=step_def.id,
                run_status="awaiting_gate",
                gate="review",
                message=f"step {step_def.id} complete; awaiting review gate",
            )

        next_step = self._next_step_def(definition, run.cursor)
        if next_step is None:
            run.status = "done"
            # cursor stays on the final step id (run.json invariant, §2.2); the
            # NextResult reports cursor=None for a done run.
            _persist()
            return NextResult(
                run_id=run.run_id,
                outcome="run_complete",
                cursor=None,
                step_id=step_def.id,
                run_status="done",
                message="final step complete; run done",
            )

        run.status = "running"
        run.cursor = next_step.id
        _persist()
        return NextResult(
            run_id=run.run_id,
            outcome="advanced",
            cursor=next_step.id,
            step_id=next_step.id,
            run_status="running",
            message=f"step {step_def.id} done; advanced to {next_step.id}",
        )

    # --- gate decisions (spec §3 / §5) --------------------------------------
    def approve_gate(self, run_id: str) -> RecipeRun:
        """Approve the review gate on the cursor step and advance past it.

        The gated step is marked ``done`` WITHOUT re-running it (its already
        produced artifact stands); the cursor moves to the next step (or the run
        completes if the gated step was last). Returns the updated run.
        """
        run = self._load_run(run_id)
        if run.status != "awaiting_gate":
            raise GateStateError(
                f"run {run_id!r} is not awaiting a gate (status {run.status!r})"
            )
        definition = self._resolve_for_run(run)
        record = run.step(run.cursor)
        record.status = "done"
        record.ended = recipe_store._utc_now()

        next_step = self._next_step_def(definition, run.cursor)
        if next_step is None:
            # cursor stays on the final step id (run.json invariant, §2.2).
            run.status = "done"
        else:
            run.cursor = next_step.id
            run.status = "running"
        recipe_store.save_run(self.workspace_root, run)
        return run

    def reject_gate(self, run_id: str) -> RecipeRun:
        """Reject the review gate, sending the gated step back for rework (F7).

        Reject is NOT a dead-end: it resets the gated step to a re-runnable state
        so the NEXT ``next`` (operator) / ``resume`` (auto) re-renders / re-invokes
        it. The rejected artifact is discarded (removed from disk + its record
        reference cleared) so the run does not immediately re-complete from the
        stale output; the cursor stays on the gated step and the run returns to
        ``running``. Returns the updated run.
        """
        run = self._load_run(run_id)
        if run.status != "awaiting_gate":
            raise GateStateError(
                f"run {run_id!r} is not awaiting a gate (status {run.status!r})"
            )
        definition = self._resolve_for_run(run)
        step_def = self._step_def(definition, run.cursor)
        record = run.step(run.cursor)

        directory = recipe_store.run_dir(self.workspace_root, run.run_id)
        output_path = ensure_output_within(directory, step_def.output, label="step")
        # Discard the rejected artifact so completion does not re-fire from it.
        try:
            output_path.unlink()
        except FileNotFoundError:
            pass

        record.status = "pending"
        record.artifact = None
        record.ended = None
        run.status = "running"
        # cursor unchanged — `next`/`resume` re-render and re-author the step.
        recipe_store.save_run(self.workspace_root, run)
        return run

    def resume(
        self, run_id: str, *, agent: WorkflowLoopAgentConfig | None = None
    ) -> NextResult | RecipeRun:
        """Re-read run.json and continue from the persisted cursor in its ``mode``.

        ``run.json`` is the single source of truth (no carried in-memory state).
        The recorded ``mode`` decides how to re-enter:

        * ``operator`` — re-surface or advance the cursor step via :meth:`next`
          (a missing output is the normal ``awaiting_input`` pause, not failure);
          returns a :class:`NextResult`.
        * ``auto`` — re-enter the agent loop via :meth:`run_auto`, retrying the
          (possibly ``failed``) cursor step; returns the updated :class:`RecipeRun`.
          The agent is resolved from the workspace config when not supplied.
        """
        run = self._load_run(run_id)
        if run.mode == "auto":
            resolved = (
                agent if agent is not None else resolve_recipe_agent(self.workspace_root)
            )
            return self.run_auto(run_id, agent=resolved)
        return self.next(run_id)

    # --- auto mode (T09) ----------------------------------------------------
    def run_auto(
        self,
        run_id: str,
        *,
        agent: WorkflowLoopAgentConfig,
        timeout_s: int = DEFAULT_AGENT_TIMEOUT_S,
    ) -> RecipeRun:
        """Drive a run via the configured agent until done / gate / failure.

        Per cursor step: render the same scoped prompt operator mode renders,
        shell to the agent (no shell injection, ``cwd=root``, bounded timeout)
        expecting it to write the step's declared ``output`` artifact, then apply
        the IDENTICAL operator-mode completion/advance/gate logic (via
        :meth:`next`) on the locked output-artifact existence check (spec §8.5).

        A non-zero exit, a timeout, or a missing ``output`` after the agent
        returns marks the step + run ``failed``, records the error and increments
        ``attempts``, and leaves the cursor on the failed step for ``resume``.
        Never advances past a gate; never mutates a prior step's artifact.
        ``run.json`` is rewritten only after the artifact lands.
        """
        if timeout_s <= 0:
            raise ValueError("timeout_s must be > 0")

        while True:
            run = self._load_run(run_id)
            # Terminal / paused states stop the loop (gates are honoured, never
            # bypassed; a done run is a noop).
            if run.status in ("done", "awaiting_gate"):
                return run

            # F8: reject a mid-run definition desync as a typed error.
            definition = self._resolve_for_run(run)
            recipe_dir = self._recipe_dir(run.recipe)
            step_def = self._step_def(definition, run.cursor)
            record = run.step(run.cursor)
            directory = recipe_store.run_dir(self.workspace_root, run.run_id)
            # F1: confirm the declared output resolves inside the run dir.
            output_path = ensure_output_within(directory, step_def.output, label="step")

            # Render BEFORE marking the step running so a render error (e.g. an
            # undeclared token) is not mistaken for an agent failure.
            prompt_text = self._render_prompt(run, step_def, recipe_dir, directory)

            # Count this attempt and mark the step running before the agent runs.
            record.attempts += 1
            record.status = "running"
            record.error = None
            if record.started is None:
                record.started = recipe_store._utc_now()
            run.status = "running"
            recipe_store.save_run(self.workspace_root, run)

            invocation = self._invoke_agent(agent, prompt_text, output_path, timeout_s)

            if invocation.timed_out:
                self._fail_step(
                    run, record, f"agent timed out after {timeout_s}s", invocation
                )
                return run
            if invocation.returncode != 0:
                self._fail_step(
                    run, record, f"agent exited {invocation.returncode}", invocation
                )
                return run
            # Completion gate (F2): the artifact must exist AND be non-empty.
            if not output_path.is_file():
                self._fail_step(
                    run, record, "agent produced no output artifact", invocation
                )
                return run
            if output_path.stat().st_size == 0:
                self._fail_step(
                    run, record, "agent produced an empty output artifact", invocation
                )
                return run

            # Output present + non-empty -> finalize through write_step_artifact
            # (atomic: artifact-first, then run.json) and advance/gate/complete.
            # F12: a non-UTF8 agent artifact is a step failure, not a crash.
            try:
                content = _read_artifact_text(output_path, label="output artifact")
            except ArtifactDecodeError as exc:
                self._fail_step(run, record, str(exc), invocation)
                return run
            result = self._complete_and_advance(
                run, definition, step_def, record, content=content
            )
            if result.outcome in ("awaiting_gate", "run_complete"):
                return self._load_run(run_id)
            # outcome == "advanced": continue with the next cursor step.

    def _invoke_agent(
        self,
        agent: WorkflowLoopAgentConfig,
        prompt: str,
        output_path: Path,
        timeout_s: int,
    ) -> _AgentInvocation:
        """Shell to the agent (no shell injection) and capture its result.

        The rendered prompt is delivered on the agent's stdin; the absolute
        output-artifact path is exported via ``GRAIN_RECIPE_OUTPUT`` (and the run
        dir via ``GRAIN_RECIPE_RUN_DIR``) so the agent knows where to write. No
        network/auth code lives here — Grain only execs the user-configured CLI.
        """
        argv = _build_agent_argv(agent)
        env = dict(os.environ)
        env[_ENV_OUTPUT] = str(output_path)
        env[_ENV_RUN_DIR] = str(output_path.parent)
        try:
            completed = subprocess.run(
                argv,
                cwd=str(self.workspace_root),
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout_s,
                env=env,
            )
        except subprocess.TimeoutExpired as exc:
            return _AgentInvocation(
                returncode=None,
                stdout=exc.stdout if isinstance(exc.stdout, str) else "",
                stderr=exc.stderr if isinstance(exc.stderr, str) else "",
                timed_out=True,
            )
        return _AgentInvocation(
            returncode=completed.returncode,
            stdout=completed.stdout or "",
            stderr=completed.stderr or "",
            timed_out=False,
        )

    def _fail_step(
        self,
        run: RecipeRun,
        record,
        message: str,
        invocation: _AgentInvocation,
    ) -> None:
        """Mark the cursor step + run ``failed``, record the error, persist.

        The cursor is left on the failed step so ``resume`` re-enters there.
        """
        detail = (invocation.stderr or invocation.stdout or "").strip()
        if detail:
            if len(detail) > _ERROR_DETAIL_LIMIT:
                detail = detail[:_ERROR_DETAIL_LIMIT] + "...(truncated)"
            error = f"{message}: {detail}"
        else:
            error = message
        record.status = "failed"
        record.error = error
        record.ended = recipe_store._utc_now()
        run.status = "failed"
        # cursor unchanged — resume retries this step.
        recipe_store.save_run(self.workspace_root, run)

    # --- helpers ------------------------------------------------------------
    @staticmethod
    def _step_def(definition: RecipeDefinition, step_id: str) -> RecipeStep:
        for step in definition.steps:
            if step.id == step_id:
                return step
        raise RunNotFoundError(
            f"cursor {step_id!r} not found in recipe {definition.id!r}"
        )

    @staticmethod
    def _next_step_def(
        definition: RecipeDefinition, step_id: str
    ) -> RecipeStep | None:
        ids = [step.id for step in definition.steps]
        idx = ids.index(step_id)
        if idx + 1 < len(definition.steps):
            return definition.steps[idx + 1]
        return None

    def _assemble_inputs(
        self, run: RecipeRun, step_def: RecipeStep, directory: Path
    ) -> list[ScopedInput]:
        """Assemble ONLY the step's declared inputs (no auto-include, §7)."""
        scoped: list[ScopedInput] = []
        for input_id in step_def.inputs:
            if input_id == _PARAMS_INPUT:
                scoped.append(
                    ScopedInput(
                        kind="params",
                        id="params",
                        path="",
                        content=_format_params(run.params),
                    )
                )
                continue
            scoped.append(self._artifact_input(run, input_id, directory))
        return scoped

    def _artifact_input(
        self, run: RecipeRun, step_id: str, directory: Path
    ) -> ScopedInput:
        try:
            record = run.step(step_id)
        except KeyError as exc:
            # Belt-and-suspenders (F10): a reference to a non-step id (e.g.
            # 'params') must never escape as a raw KeyError from run.step().
            raise UnknownTokenError(
                f"input {step_id!r} is not a step in run {run.run_id!r}"
            ) from exc
        if record.status != "done":
            raise InputNotReadyError(
                f"input {step_id!r} is not done (status {record.status!r})"
            )
        artifact_path = directory / record.artifact if record.artifact else None
        if artifact_path is None or not artifact_path.exists():
            raise InputNotReadyError(
                f"input {step_id!r} has no artifact on disk"
            )
        return ScopedInput(
            kind="artifact",
            id=step_id,
            path=str(artifact_path),
            # F12: a non-UTF8 prior artifact yields a typed ArtifactDecodeError,
            # never a raw UnicodeDecodeError crash.
            content=_read_artifact_text(artifact_path, label=f"input {step_id!r} artifact"),
        )

    def _render_prompt(
        self,
        run: RecipeRun,
        step_def: RecipeStep,
        recipe_dir: Path,
        directory: Path,
    ) -> str:
        """Load the step prompt (path or ``inline:``) and substitute tokens (§8)."""
        prompt = step_def.prompt
        if prompt.startswith(_INLINE_PREFIX):
            template = prompt[len(_INLINE_PREFIX) :]
        else:
            template = (recipe_dir / prompt).read_text(encoding="utf-8")
        return self._substitute(template, run, step_def, directory)

    def _substitute(
        self,
        template: str,
        run: RecipeRun,
        step_def: RecipeStep,
        directory: Path,
    ) -> str:
        """Replace ``{{param}}`` / ``{{steps.<id>}}`` tokens; fail loud otherwise."""
        declared = set(step_def.inputs)

        def _replace(match: re.Match[str]) -> str:
            token = match.group(1).strip()
            if token.startswith(_STEPS_PREFIX):
                ref_id = token[len(_STEPS_PREFIX) :]
                # F10: 'params' is a legal *inputs* entry but is NOT a step, so a
                # ``{{steps.params}}`` reference must not be treated as an
                # artifact lookup (which would hit ``run.step('params')`` and
                # raise a raw KeyError). Surface a clean typed token error.
                if ref_id == _PARAMS_INPUT:
                    raise UnknownTokenError(
                        f"{{{{steps.params}}}} in step {step_def.id!r} is not a "
                        f"valid step reference; 'params' is not a step (use "
                        f"'{{{{<param>}}}}' with 'params' declared in inputs)"
                    )
                if ref_id not in declared:
                    raise UndeclaredInputError(
                        f"{{{{steps.{ref_id}}}}} is not declared in step "
                        f"{step_def.id!r} inputs {sorted(declared)}"
                    )
                return self._artifact_input(run, ref_id, directory).content
            if token in run.params:
                # F13: a {{param}} token is in scope ONLY when the step declares
                # ``params`` in its inputs — same declared-input scoping as
                # {{steps.<id>}}. Otherwise it is an undeclared (out-of-scope)
                # reference, not a free-for-all read of the run params.
                if _PARAMS_INPUT not in declared:
                    raise UndeclaredInputError(
                        f"{{{{{token}}}}} references a param but step "
                        f"{step_def.id!r} does not declare 'params' in its "
                        f"inputs {sorted(declared)}"
                    )
                return run.params[token]
            raise UnknownTokenError(
                f"unresolved token {{{{{token}}}}} in step {step_def.id!r}"
            )

        return _TOKEN_RE.sub(_replace, template)
