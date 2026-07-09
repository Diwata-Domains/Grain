# Task: recipe_service — operator-mode engine

## Metadata
- **ID:** P34-T03
- **Status:** draft
- **Phase:** Phase 34 — Recipe Step-Runner MVP
- **Backlog:** P34-T03
- **Packet Path:** tasks/P34-T03/
- **Dependencies:** P34-T01, P34-T02
- **Primary Adapter:** code
- **Secondary Adapters:** none
- **Recipe-engine:** parallel engine — operator-mode step advance; consumes `grain.recipe/v2` definitions (P34-T01) and `grain.recipe-run/v1` run state (P34-T02); does NOT touch `evaluate_workflow_state`, task packets, or the SDLC review/close loop.

## Objective
Build `RecipeService` — the operator-mode (offline, deterministic) execution engine for the recipe step-runner. The service resolves a recipe by id (bundled + workspace `docs/recipes/<id>/`), starts a run under `docs/recipes/runs/<run-id>/` (returning outcome `started`: `status=pending`, cursor on the first step, NO auto-advance), and advances the run exactly ONE step per `next()` call: it renders the current step's prompt with its scoped declared inputs (`params` + named prior-step artifacts), surfaces the rendered prompt plus the absolute output-artifact path for a human or familiar to fulfil (an unfulfilled step pauses at `awaiting_input` — the operator-mode pause, NOT a failure), detects step completion by output-artifact existence, advances the cursor, handles a `gate: review` pause (`awaiting_gate`), and resumes from the persisted cursor in the recorded `mode` on a later invocation. No network, no API key, no control flow. This packet is the recipe-enumeration owner (bundled + workspace); T06 ships the bundled `research-brief` recipe as DATA only.

## Why This Task Exists
This is the executable core of v0.5.0 contract deliverable #2 (`grain recipe` execution) and the deterministic, offline demo path called out in `recipe_engine_spec.md` §3 and §7 (MVP must-ship). P34-T01 (definition model + `grain.recipe/v2` parser) and P34-T02 (`RecipeRun` / `run.json` file-backed state under `docs/recipes/runs/`) provide the data layer; this task is the state-machine that drives a run forward one inspectable step at a time. The CLI surface (`grain recipe next|status|resume`) and auto-mode are separate packets; this packet owns the service logic they call.

## Approach / Scope
**In scope:**
- **Recipe resolution + enumeration.** `resolve(recipe_id)` finds a recipe by id, searching workspace `docs/recipes/<id>/recipe.yaml` first, then bundled recipes, and parses it via the P34-T01 loader into a `RecipeDefinition`. Unknown id → `RecipeNotFoundError`. This packet also owns recipe *enumeration* (`list_recipes()` → bundled + workspace recipe ids/metadata), the single source the CLI `list` (T04) consumes; T06 contributes the bundled `research-brief` recipe as DATA only.
- **Run start.** `start_run(recipe_id, params)` validates required params against the definition, allocates a `<run-id>` via the P34-T02 run-id allocation helper (the single owner of id allocation — `<recipe-id>-<NNNN>`, zero-padded; this service calls it, does not reimplement scanning), creates `docs/recipes/runs/<run-id>/`, writes the initial `run.json` (`apiVersion: grain.recipe-run/v1`, all steps `pending`, cursor on the first step, `status: pending`, `mode` set from the run mode (operator by default), `supervision` copied from the parsed definition) via the P34-T02 writer, and returns a result with `outcome == "started"`. `start_run` does NOT auto-advance — the first `next()` renders the first prompt.
- **Advance one step (operator mode).** `next(run_id)` reads `run.json`, locates the cursor step, and:
  1. If the step's `output` artifact already exists → mark step `done`, stamp `ended`, advance cursor to the next step (or mark run `done` if none), persist, return outcome `advanced` (or `run_complete`).
  2. Else render the step prompt (load `prompt:` path under the recipe dir, or `inline:` block) with scoped inputs and return outcome `prompt_ready` carrying the rendered prompt text + absolute output path + the input artifact paths; set step and run `status: awaiting_input` (the operator-mode pause — a missing output is NOT a failure), persist. The call is idempotent: re-invoking before the artifact lands re-surfaces the same prompt at `awaiting_input`.
- **Scoped declared inputs.** Only the step's declared `inputs:` are assembled: `params` expands to the run's params dict; each other id is a prior step's artifact (absolute path + content), resolved from `run.json`. No auto-include of the whole run. A declared input referencing a not-yet-`done` prior step → `InputNotReadyError`.
- **Completion detection.** A step completes iff its declared `output` artifact exists on disk (MVP validation = existence check only; no structural validator).
- **Gate handling.** When the just-completed cursor step declares `gate: review`, set the step and run `status: awaiting_gate` (cursor stays on that step) instead of advancing; `next()` on an `awaiting_gate` run returns outcome `noop` reporting the pending gate. (Gate approve/reject resume is the T05 runner packet; this packet only enters/reports the state and never raises a gate-blocked error.)
- **Resume from cursor.** `resume(run_id)` re-reads `run.json` and continues `next()` semantics from the persisted cursor in the run's recorded `mode` — no separate in-memory state; `run.json` is the single source of truth. In operator mode `status: failed` is unreachable (a missing output is `awaiting_input`, not failure), so resume simply re-surfaces or advances the cursor step. Unknown run id → `RunNotFoundError`.
- **Substitution.** Minimal `{{param}}` and `{{steps.<id>}}` token replacement in prompt text only, reusing Grain's existing no-control-flow templating idiom. `{{steps.<id>}}` resolves to that prior step's artifact content for a step that is BOTH `done` AND declared in `inputs:`. A reference to a step that is done but NOT declared in `inputs:` (out of scope) → `UndeclaredInputError`; a reference to a declared-but-not-done step → `InputNotReadyError`; any other unresolved token → `UnknownTokenError`.
- **Idioms.** Result objects are dataclasses with `__post_init__` validation; status/mode/outcome strings guarded by `VALID_*` frozensets, mirroring `domain/workflow_loop.py`.

**Out of scope (deferred — do NOT build here):**
- Auto mode / `--auto` / shelling to an agent CLI (`WorkflowLoopAgentConfig` wiring) — sibling packet.
- The `grain recipe` CLI group and `--format json` rendering — sibling packet (service returns structured objects).
- MCP exposure, `recipe suggest`, `scaffold`, registry/install.
- Branching, conditional, parallel, or loop steps; per-step `adapter` scoping; `model` bias.
- Structural output validators; apply / write-back to office docs.
- Full `workspace_kind` resolution (degrade gracefully if absent).

## Deliverable
`src/grain/services/recipe_service.py` (the single canonical service-module name) — `RecipeService` implementing `resolve`, `list_recipes`, `start_run`, `next`, `resume`, plus operator-mode result dataclasses, with a unit test suite exercising start → multi-step advance → gate pause → resume against a temp workspace and a fixture recipe.

## Acceptance Criteria
- `start_run(<fixture-id>, {<required params>})` against the packet's OWN 2–3 step fixture recipe (scaffolded by the test under a temp `docs/recipes/<fixture-id>/`; do NOT use the bundled `research-brief`, which is T06 data shipped AFTER T03 and cannot be a T03 test input — see `deliverable_spec.md` §1, §10.1) returns a result with `outcome == "started"`, does NOT auto-advance, and creates `docs/recipes/runs/<fixture-id>-0001/run.json` with `apiVersion == "grain.recipe-run/v1"`, all N steps `pending`, `cursor` on the first step, `status == "pending"`, `mode == "operator"`, and `supervision` copied from the parsed definition — assertable by reading the file. Missing a required param raises `MissingParamError` and writes no run dir. The `<run-id>` is allocated via the P34-T02 allocation helper (not reimplemented here).
- `resolve("does-not-exist")` raises `RecipeNotFoundError` — assertable. `next("no-such-run")` / `resume("no-such-run")` raise `RunNotFoundError` — assertable.
- Calling `next(run_id)` when the cursor step's `output` does not exist returns outcome `prompt_ready` with run and step `status == "awaiting_input"` (NOT `failed`), whose rendered prompt has all `{{param}}`/`{{steps.<id>}}` tokens substituted, exposes the absolute output path, and includes ONLY the step's declared inputs (a step declaring `inputs: [params, intake]` must not surface `gather`'s artifact) — assertable by inspecting the result object and `run.json`.
- A `{{steps.<id>}}` reference to a step that is `done` but NOT declared in the cursor step's `inputs:` raises `UndeclaredInputError` (distinct from `InputNotReadyError`, which covers a declared-but-not-done input) — assertable.
- After a test writes the cursor step's `output` artifact, the next `next(run_id)` marks that step `done`, advances `cursor` to the following step (returning outcome `advanced`), and persists both to `run.json` — assertable by re-reading `run.json`.
- A step declaring `gate: review`: once its artifact exists, `next()` sets step and run `status == "awaiting_gate"` and leaves `cursor` on that step (does not advance); a further `next()` returns outcome `noop` reporting the pending gate (no `GateBlockedError` is raised) — assertable from `run.json` and the returned result.
- The final step fulfilled → `next()` returns outcome `run_complete`, run `status == "done"`, `cursor == None` — assertable.
- `resume(run_id)` on a fresh `RecipeService` instance (no shared memory) continues from the persisted `cursor` in the recorded `mode` and reproduces identical `next()` behavior — assertable by driving a run, discarding the service, and resuming.
- The module imports and runs with no network access and no API key set, and references neither `evaluate_workflow_state` nor any task-packet/review/close service — assertable by test + grep.

## Dependencies
- **P34-T01** — `RecipeDefinition` / `RecipeStep` domain model + `grain.recipe/v2` parser (provides `resolve`'s parse step and the step schema).
- **P34-T02** — `RecipeRun` / `RecipeStepRecord` file-backed model + `run.json` (`grain.recipe-run/v1`) read/write under `docs/recipes/runs/`, and the **run-id allocation helper** (single owner; this packet calls it) — provides start/persist/resume I/O.

(Role: P34-T03 = operator-mode engine + recipe-enumeration owner. Consumers: T04 = CLI list/show/scaffold; T05 = CLI run/next/status/resume/gate (the runner, incl. gate approve/reject and auto mode); T06 = bundled `research-brief` recipe, data only.)

## Relevant Files
- `src/grain/services/recipe_service.py` — NEW, the deliverable.
- `tests/services/test_recipe_service.py` — NEW, unit tests (mirror existing `tests/services/` layout).
- `src/grain/domain/recipe.py` — from P34-T01 (definition dataclasses, `VALID_*`, parser). Consumed.
- `src/grain/domain/recipe_run.py` — from P34-T02 (run dataclasses + `run.json` I/O). Consumed.
- `src/grain/domain/workflow_loop.py` — idiom reference (`dataclass` + `__post_init__` + `VALID_*` frozensets).
- `src/grain/services/workflow_loop_service.py` — service-style reference (operator vs auto split mirrors `workflow next` vs `workflow loop`).
- `docs/working/recipe_engine_spec.md` — §2 data model, §3 execution model, §5 resume, §8 locked decisions, §9 implementation notes.

## Model recommendation
**Claude Opus** (or strongest available) for implementation: this is a stateful engine with several interacting invariants (cursor/gate/idempotency/scoping correctness, atomic-write ordering, single-source-of-truth resume) where a subtle bug silently corrupts a run. The work is contained to one new service + its tests, so cost is bounded; correctness of the state machine is the dominant risk.

## Constraints
- Parallel engine only: no import of or call into `evaluate_workflow_state`, task-packet lifecycle, or review/close services (`recipe_engine_spec.md` §1, §6).
- Operator mode only — no network, no API key, no agent CLI shell-out in this packet.
- `run.json` is the single source of truth; resume re-reads it (no hidden/in-memory run state).
- Update `run.json` only AFTER the artifact lands; artifacts/run.json written atomically (no partial-corruption window) — `recipe_engine_spec.md` §2.2. (I/O primitives owned by P34-T02; this service must call them in the correct order.)
- Input scoping is declared `inputs:` only — never auto-include the whole run (§1.7, §8.3). A `{{steps.<id>}}` referencing a `done` step that is NOT in `inputs:` is an out-of-scope reference → `UndeclaredInputError`.
- Substitution is `{{param}}` / `{{steps.<id>}}` only — no conditionals, loops, or expressions.
- Validation is output-artifact existence only; structural validators are deferred (§8.5).
- Engine outcomes are exactly `{started | prompt_ready | advanced | awaiting_gate | run_complete | noop}` (`recipe_engine_spec.md` §3.1); `awaiting_input` is a run/step *status*, not an outcome (`next` returns `prompt_ready` with status `awaiting_input`). `start_run` returns `started` (no auto-advance).
- `mode` (`operator | auto`) is DISTINCT from `supervision` (`supervised | gated | autonomous`): `mode` is set at run time (default `operator`); `supervision` is parsed into `RecipeDefinition` and copied to `run.json`. Never store `operator`/`auto` in a supervision field or vice-versa.
- Run-id allocation is owned by the P34-T02 helper; this service calls it and never reimplements the scan.
- `status: failed` is unreachable in operator mode (a missing output is `awaiting_input`); it is reserved for auto-mode agent errors / explicit validation (the T05 runner packet). Do not raise `GateBlockedError` here.

## Escalation Conditions
- P34-T01 / P34-T02 interfaces (parser entry point, run read/write signatures, run-id allocation ownership) are unresolved or differ from the shapes assumed in `deliverable_spec.md` — confirm before coding rather than duplicating I/O.
- A locked decision in `recipe_engine_spec.md` §8 appears to conflict with an implementation need — surface, do not reopen unilaterally.
