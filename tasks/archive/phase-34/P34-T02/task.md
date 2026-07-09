# Task: RecipeRun state model + file-backed persistence

## Metadata
- **ID:** P34-T02
- **Status:** done
- **Phase:** Phase 34 — Recipe step-runner MVP
- **Backlog:** P34-T02
- **Packet Path:** tasks/P34-T02/
- **Recipe-engine:** parallel engine (NOT the SDLC packet loop); run state apiVersion `grain.recipe-run/v1`, consumes recipe defs at `grain.recipe/v2`
- **Dependencies:** P34-T01 (RecipeDefinition / RecipeStep parser for `grain.recipe/v2`)
- **Primary Adapter:** code
- **Secondary Adapters:** none

## Objective
Build the run-state layer for the recipe step-runner: the `RecipeRun` and `RecipeStepRecord`
domain dataclasses plus a file-backed `recipe_store` that reads and writes `run.json`
(`apiVersion: grain.recipe-run/v1`) under `docs/recipes/runs/<run-id>/`. This is the single
source of truth a run resumes from — it owns the run-directory layout, run-id allocation,
status enums, and the atomic write ordering (step artifact lands first, then `run.json`), so
no consumer ever observes a corrupt or half-advanced run. This task delivers state + I/O only;
step execution, the cursor-advancing engine, and the CLI are separate P34 packets that build on
these types.

## Why This Task Exists
Recipe-engine spec §2.2 ("`run.json` — `apiVersion: grain.recipe-run/v1`"), §5 (Failure &
resume), and §9 (implementation notes) require a file-backed run state distinct from task
packets. The locked decision (spec §8.1) puts runs at `docs/recipes/runs/<run-id>/`, decoupled
from `tasks/`. Every other MVP packet (`next`, `status`, `resume`, the runner) reads/writes this
state, so it must land first behind only the parser. Carries v0.5.0 contract deliverable #2
(`grain recipe` execution) and #6 (familiar-drivable: `run.json` is the structured, file-backed
resume contract).

## Scope
- New domain module `src/grain/domain/recipe_run.py`:
  - `RecipeStepRecord` dataclass — one per recipe step in run order.
  - `RecipeRun` dataclass — the whole run; holds the ordered step records. Carries a `mode`
    field (`operator | auto`, spec §2.2) DISTINCT from `supervision`; never store
    `operator`/`auto` as a supervision value.
  - `VALID_RUN_STATUSES` / `VALID_STEP_STATUSES` frozensets =
    `{pending, running, awaiting_input, awaiting_gate, done, failed}` (same set for both run and
    step). `awaiting_input` is the operator-mode pause (prompt rendered, waiting for the artifact).
  - `VALID_MODES` frozenset = `{operator, auto}` for the run `mode` field.
  - `__post_init__` validation on both dataclasses (status membership, non-empty ids,
    `apiVersion` major check), mirroring `domain/workflow_loop.py` idioms.
  - `to_dict()` / `from_dict()` round-trip to the §2.2 JSON shape.
- New service `src/grain/services/recipe_store.py`:
  - Resolve the runs root (`docs/recipes/runs/`) and a single run dir by `run_id`.
  - Allocate the next `run_id` (`<recipe-id>-NNNN`, zero-padded) by scanning existing run dirs.
  - `create_run(...)` — make the run dir + initial `run.json` (status `pending`, all steps
    `pending`) from a parsed `RecipeDefinition`. Reads `definition.supervision` (now PARSED by
    P34-T01, not accept-and-ignore) and writes it to `run.json`; persists each step's declared
    `gate` onto its step record; sets the run `mode` (`operator | auto`) from the caller.
  - `load_run(run_id)` / `save_run(run)` — read/write `run.json`.
  - `list_runs()` — enumerate run ids (newest-first ok).
  - `write_step_artifact(...)` — atomically write a step artifact into the run dir, THEN
    persist `run.json` (artifact-first ordering, no partial-corruption window).
  - Atomic file writes via temp-file + `os.replace` within the run dir. The atomic-ordering test
    injects a fault by monkeypatching `os.replace` (or the temp-write) to raise on the `run.json`
    write and asserts the prior `run.json` is left intact (untruncated).
- Timestamps: engine stamps `created`/`updated` on the run and `started`/`ended` per step.
- Tests in `tests/` covering construction, validation, round-trip, run-id allocation, atomic
  ordering, and resume-by-reload.

## Out of Scope (deferred / other packets)
- Cursor advancement / step execution loop (the runner) — separate P34 packet.
- The `grain recipe` CLI surface and `--format json` rendering.
- Auto mode / `WorkflowLoopAgentConfig` shelling — operator mode is the demo path; this packet
  stores `supervision` but does not execute anything.
- Gate approve/reject logic (store the `awaiting_gate` status + per-step `gate`; do not implement
  the gate transition engine).
- Structural / per-step output validators (MVP = existence check, owned by the runner packet).
- MCP exposure, branching/parallel/loops, `recipe suggest`, apply/write-back, full
  `workspace_kind`, per-step adapters.

## Acceptance Criteria
- Importing `RecipeRun` / `RecipeStepRecord` and constructing one with an invalid status (not in
  `{pending, running, awaiting_input, awaiting_gate, done, failed}`) raises `ValueError` in
  `__post_init__`; a valid one (including `awaiting_input`) constructs. An invalid `mode` (not in
  `{operator, auto}`) also raises. (unit test)
- `RecipeRun.from_dict(run.to_dict())` round-trips a run with mixed step statuses (incl. a step
  carrying `gate: review`) and a populated `mode` + `supervision` with no field loss, and the
  emitted dict carries `"apiVersion": "grain.recipe-run/v1"`. (unit test)
- `create_run` on a parsed `RecipeDefinition` creates `docs/recipes/runs/<run-id>/run.json` with
  run `status: pending`, `cursor` on the first step, one step record per recipe step all
  `status: pending`, `params` populated, `recipe_apiVersion: grain.recipe/v2`, `mode` set from the
  caller, `supervision` copied from `definition.supervision`, and each step record carrying its
  declared `gate`. (test asserts on-disk JSON)
- Calling `create_run` twice for the same recipe id yields distinct, monotonically increasing,
  zero-padded run ids (e.g. `research-brief-0001`, `research-brief-0002`) and two separate run
  dirs. (unit test)
- `write_step_artifact` writes the artifact file AND then `run.json`; a test that makes the
  `run.json` write fail (monkeypatch `os.replace`/temp-write to raise) leaves the previously
  persisted `run.json` intact (no truncated/partial file) — i.e. writes go through a temp file +
  `os.replace`. (unit test)
- `load_run(run_id)` reconstructs a `RecipeRun` equal to one previously `save_run`'d (resume =
  re-read `run.json`), and `load_run` on an unknown major in `apiVersion` raises. (unit test)

## Constraints
- Run state is parallel to the SDLC loop: do NOT import or call `evaluate_workflow_state`,
  task-packet, or review/close code. No coupling to `tasks/`.
- File-backed only — no DB, no daemon, no `.grain/` hidden state. State lives at
  `docs/recipes/runs/<run-id>/` as inspectable, diff-able JSON.
- Reuse Grain idioms: `@dataclass` + `__post_init__` + `VALID_*` frozensets, matching
  `src/grain/domain/workflow_loop.py`. Do not invent a new validation style.
- Reject unknown `apiVersion` majors on load (engine contract, spec §1.5).
- Step artifacts are never mutated by a prior step's write; re-running a step overwrites only
  that step's artifact and increments its `attempts` (store must support this even though the
  runner drives it).

## Escalation Conditions
- P34-T01's `RecipeDefinition` / `RecipeStep` shape differs from spec §2.1 in a way that changes
  what `create_run` must read (e.g. step `id`/`output` field names) — reconcile before building.
- The locked run-id format (`<recipe-id>-NNNN`) collides with any existing on-disk convention —
  stop and confirm rather than guessing a scheme.

## Model recommendation
Opus-class (or strongest available) for the design pass — the atomic-write ordering and the
resume/round-trip contract are the load-bearing correctness surface. A mid-tier model is fine for
the mechanical dataclass + JSON round-trip once the store's write protocol is settled.
