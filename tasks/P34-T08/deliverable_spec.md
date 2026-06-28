# Deliverable Spec: P34-T08 — Integration tests + docs + audit-clean

This packet ships **tests + docs only**. It defines no new engine interface; it pins the
behavior of the P34-T05 runner (CLI `run`/`next`/`status`/`resume`/`gate` — resume lives here)
against the locked contracts, exercised over the P34-T06 bundled `research-brief` recipe (data
only). Versions under test: `recipe.yaml` `apiVersion: grain.recipe/v2`,
`run.json` `apiVersion: grain.recipe-run/v1`, runs under `docs/recipes/runs/<run-id>/`.

## Required Output

### New Files
- `tests/test_recipe_e2e.py` — two offline, deterministic end-to-end tests (detailed below).

### Modified Files
- `README.md` — recipe section rewritten to state the step-runner supersedes the single-packet
  model, recipes run parallel to the task-packet loop, plus an operator-mode quickstart.
- `CHANGELOG.md` — v0.5.0/unreleased entry naming the recipe step-runner MVP.
- `docs/working/recipe_engine_spec.md` — status note / cross-links only (working doc).

### Untouched (reference only)
- `docs/canonical/recipe_spec.md` — approval-gated; supersession is recorded in the working doc.
- `src/grain/{cli/recipe.py,services/recipe_service.py,domain/recipe.py}` — under test.

## Contracts asserted (from spec §2)

The tests treat these as the done-definition of the engine they exercise. No new shapes are
introduced; the spec shapes are the assertion targets.

### `run.json` (`grain.recipe-run/v1`)
Top-level keys asserted present and typed:
- `apiVersion` == `"grain.recipe-run/v1"`
- `run_id` (str), `recipe` (str), `recipe_apiVersion` == `"grain.recipe/v2"`
- `params` (object; `{"topic": <str>}` for `research-brief`)
- `mode` (str) ∈ `{operator, auto}` — records how the run is driven; distinct from `supervision`,
  set at `recipe run` time (default `operator`; `--auto` ⇒ `auto`), and is what `resume` reads to
  continue. Never store an `operator`/`auto` value in `supervision`.
- `supervision` (str) ∈ `{supervised, gated, autonomous}`
- `status` ∈ `{pending, running, awaiting_input, awaiting_gate, done, failed}`
- `cursor` (step id or null when done)
- `steps`: ordered list of step records, each `{id, status, artifact?, attempts}` where step
  `status` ∈ `{pending, running, awaiting_input, awaiting_gate, done, failed}`
- engine timestamps present (`created`/`updated`; per-step `started`/`ended` once a step runs)

### `recipe.yaml` (`grain.recipe/v2`)
`research-brief` is the bundled 6-step recipe shipped by P34-T06 (data only) and installed at
`src/grain/data/recipes/research-brief/`: `intake → gather → outline → draft → self_check →
format`, with `final: brief.md`. It is **gateless** — no step declares `gate: review` (unlike the
illustrative gated example in spec §2.1), so the full operator run advances every step straight to
`done` with no `awaiting_gate` pause. The tests read it via the engine, not by re-parsing YAML by
hand. (`docs/recipes/` is the workspace-recipe location; the bundled recipe lives under
`src/grain/data/recipes/`.)

## Test contract — `tests/test_recipe_e2e.py`

Shared fixture: build a temp pre-staged `knowledge` workspace containing the bundled
`research-brief` recipe (and any pre-staged source files the recipe expects), with no git/branch
or task-packet machinery required. Drive the real CLI entrypoints (or the service functions they
wrap); capture `--format json` for assertions. Operator mode **never writes artifacts and never
auto-completes** — the harness must **write each step's declared `output` artifact** (fixed fixture
text) between cursor advances; the engine does not generate content offline. `start_run` returns
outcome `started` (status `pending`, cursor on the first step, no auto-advance). `next` renders the
current step's prompt and returns outcome `prompt_ready` with status `awaiting_input` until the
artifact is written, then returns `advanced` (or `run_complete` at the end). Engine outcomes are
`{started | prompt_ready | advanced | awaiting_gate | run_complete | noop}`; `awaiting_input` is a
*status*, not an outcome.

### Test A — `test_research_brief_full_operator_run`
1. Start: `grain recipe run research-brief --param topic="GLP-1 obesity market" --format json`.
   Assert the start outcome is `started`, run `status == "pending"`, `mode == "operator"`, and the
   `cursor` is the first step (`intake`) — the bare `run` did **not** auto-advance or write any
   artifact.
2. (Negative check) Calling `grain recipe next` once **without** writing the step's `output` leaves
   the run at `status == "awaiting_input"` on the same cursor (the engine wrote no artifact and did
   not reach `done`). Then drive the loop properly.
3. Loop the 6 steps: for each, read `grain recipe status --format json` to get the `cursor`,
   write the step's declared `output` artifact into the run dir, then `grain recipe next`.
4. Assertions:
   - Steps reach `done` in spec order (`intake, gather, outline, draft, self_check, format`).
   - Final run `status == "done"`, `cursor == "format"` (final step id, per spec §2.2), every step
     record `status == "done"` with `attempts == 1`.
   - `run.json` carries `mode == "operator"` (not stored as a supervision value).
   - The `final` artifact `brief.md` exists under `docs/recipes/runs/<run-id>/`.
   - `run.json` round-trips the full contract above (apiVersions, run_id, recipe, params, mode).
   - No task packet created and `evaluate_workflow_state` not invoked (parallel-engine assertion).

   (Test A may alternatively assert against a **committed reference run** —
   `research-brief-0001` with `run.json status=done`, `cursor=format`, all 6 artifacts present — to
   prove the structure without the live loop; the live authoring loop is the primary form.)

### Test B — `test_resume_after_validation_failure`
1. Drive the run normally through the first few steps (e.g. through `outline`).
2. Force an **explicit validation failure** on the next step (`draft`): write a `draft` `output`
   artifact that fails validation (or invoke the engine's validation-failure path) and advance, so
   the engine records `status: failed`, leaves `cursor` on `draft`, and records the error in
   `run.json` (spec §5). NOTE: a *missing* output is NOT a failure in operator mode — it is the
   normal `awaiting_input` pause — so the test must trigger a validation failure, not omit the
   artifact.
3. Snapshot byte content of all prior step artifacts (`01-intake.md … 03-outline.md`).
4. `grain recipe resume <run-id>`, write a **valid** `draft` artifact, then drive remaining steps
   to done.
5. Assertions:
   - After the failure: run `status == "failed"`, `cursor == "draft"`, `draft` step `status ==
     "failed"`, error field populated.
   - After resume + completion: run `status == "done"`, `draft` step `attempts == 2`.
   - All prior step artifacts are byte-for-byte identical to the snapshot (no step mutates a prior
     step's artifact — spec §5).
   - Resume re-reads `run.json` (including `mode`) as the single source of truth and continues in
     the recorded `mode` (no hidden state).

## Acceptance Checklist
- [ ] `uv run pytest tests/test_recipe_e2e.py` passes (both tests).
- [ ] Tests are offline/deterministic: no network, no API key, no agent CLI shell-out, no
      `WorkflowLoopAgentConfig` auto path exercised.
- [ ] `run.json` assertions cover `apiVersion: grain.recipe-run/v1`, `recipe_apiVersion:
      grain.recipe/v2`, and `mode == "operator"` (distinct from `supervision`); run dir is under
      `docs/recipes/runs/<run-id>/`.
- [ ] Test A proves operator mode does not auto-complete: bare `run` ⇒ `started`/`pending`, and
      `next` without an authored artifact ⇒ `awaiting_input` (not `failed`, not `done`).
- [ ] Test B proves resume via an **explicit validation failure** (not a missing artifact):
      `failed → done`, retried step `attempts == 2`, `resume` reads `mode`, prior artifacts unchanged.
- [ ] `README.md` states the engine supersedes the single-packet model + has an operator quickstart.
- [ ] `CHANGELOG.md` has the v0.5.0/unreleased recipe step-runner MVP entry.
- [ ] `grain docs audit` clean; full `uv run pytest` green with no regressions.

## Not Required
- Auto-mode / `--auto` execution, MCP exposure, gate approve/reject flows, structural output
  validators, branching/parallel/loop steps, `recipe suggest`, full `workspace_kind`, per-step
  adapters, apply/write-back, or any edit to approval-gated `docs/canonical/recipe_spec.md`.
- Asserting LLM/content equality — only engine ordering, scoping, gating, and run-state are tested.
