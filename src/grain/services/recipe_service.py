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
from grain.domain.recipe import RecipeDefinition, RecipeStep, load_recipe
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
class RecipeNotFoundError(Exception):
    """No recipe with the given id under workspace or bundled recipes."""


class RunNotFoundError(Exception):
    """No run with the given id under docs/recipes/runs/."""


class MissingParamError(Exception):
    """A required recipe parameter was not supplied to start_run."""


class InputNotReadyError(Exception):
    """A declared input references a prior step that is not yet ``done``."""


class UndeclaredInputError(Exception):
    """A ``{{steps.<id>}}`` references a step NOT in the cursor step's inputs."""


class UnknownTokenError(Exception):
    """A ``{{...}}`` token resolves to neither a param nor a valid steps.<id>."""


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
        """Find + parse a recipe by id (workspace first, then bundled)."""
        recipe_dir = self._recipe_dir(recipe_id)
        return load_recipe(recipe_dir / "recipe.yaml")

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

        definition = self.resolve(run.recipe)
        recipe_dir = self._recipe_dir(run.recipe)
        step_def = self._step_def(definition, run.cursor)
        record = run.step(run.cursor)
        directory = recipe_store.run_dir(self.workspace_root, run.run_id)
        output_path = directory / step_def.output

        # 4. Output exists -> mark done + advance (or gate / complete).
        if output_path.exists():
            record.status = "done"
            record.artifact = step_def.output
            record.ended = recipe_store._utc_now()
            if record.attempts == 0:
                record.attempts = 1

            if step_def.gate == "review":
                record.status = "awaiting_gate"
                run.status = "awaiting_gate"
                # cursor unchanged
                recipe_store.save_run(self.workspace_root, run)
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
                # cursor stays on the final step id (run.json invariant, §2.2);
                # the NextResult reports cursor=None for a done run.
                recipe_store.save_run(self.workspace_root, run)
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
            recipe_store.save_run(self.workspace_root, run)
            return NextResult(
                run_id=run.run_id,
                outcome="advanced",
                cursor=next_step.id,
                step_id=next_step.id,
                run_status="running",
                message=f"step {step_def.id} done; advanced to {next_step.id}",
            )

        # 5. Output missing -> operator-mode pause (render + surface, no failure).
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

            definition = self.resolve(run.recipe)
            recipe_dir = self._recipe_dir(run.recipe)
            step_def = self._step_def(definition, run.cursor)
            record = run.step(run.cursor)
            directory = recipe_store.run_dir(self.workspace_root, run.run_id)
            output_path = directory / step_def.output

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
            if not output_path.exists():
                self._fail_step(
                    run, record, "agent produced no output artifact", invocation
                )
                return run

            # Output exists -> reuse the operator advance/gate/complete logic.
            result = self.next(run_id)
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
        record = run.step(step_id)  # KeyError impossible: parser validates refs
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
            content=artifact_path.read_text(encoding="utf-8"),
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
                if ref_id not in declared:
                    raise UndeclaredInputError(
                        f"{{{{steps.{ref_id}}}}} is not declared in step "
                        f"{step_def.id!r} inputs {sorted(declared)}"
                    )
                return self._artifact_input(run, ref_id, directory).content
            if token in run.params:
                return run.params[token]
            raise UnknownTokenError(
                f"unresolved token {{{{{token}}}}} in step {step_def.id!r}"
            )

        return _TOKEN_RE.sub(_replace, template)
