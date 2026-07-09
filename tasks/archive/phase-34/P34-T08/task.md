# Task: Integration tests + docs + audit-clean

## Metadata
- **ID:** P34-T08
- **Status:** done
- **Phase:** Phase 34 — Recipe Step-Runner MVP (v0.5.0)
- **Backlog:** P34-T08
- **Packet Path:** tasks/P34-T08/
- **Recipe-engine:** integration layer — exercises `grain.recipe/v2` + `grain.recipe-run/v1` end-to-end; ships no new engine surface. Parallel engine; does NOT touch the SDLC packet review/close loop.
- **Dependencies:** P34-T05, P34-T06
- **Primary Adapter:** code
- **Secondary Adapters:** none

## Objective
Close out the recipe step-runner MVP with proof and documentation. Add an end-to-end integration test that drives the bundled `research-brief` recipe to a full **operator-mode** completion via the authoring loop (write each step's `output` artifact, then `grain recipe next`) — a bare offline `grain recipe run` pauses at `status: awaiting_input` and never reaches `done` on its own — and a second test that resumes after an **explicit validation failure** mid-run, asserting the run lands at `status: done` with all six artifacts present and `run.json` consistent. Update `README.md` and the recipe docs so they state the step-runner engine **supersedes the single-packet recipe model**, keep the Grain docs audit clean (no broken links / orphaned references), and add a `CHANGELOG.md` note for the MVP. This packet ships no new engine code — it verifies and documents what P34-T05 (CLI `run`/`next`/`status`/`resume`/`gate` — the runner, where resume lives) and P34-T06 (the bundled `research-brief` recipe — data only) already built. The bundled `research-brief` is gateless, so the all-steps-to-`done` e2e loop is grounded entirely in T06's data.

## Why This Task Exists
The recipe step-runner is v0.5.0 contract deliverable #2 (`grain recipe` execution), carrying #6 (grain-as-engine / familiar-drivable) and #10 (graduated ceremony). `recipe_engine_spec.md` §7 names "Operator mode" and "Resume on failure" as MVP must-ships and demands the bundled `research-brief` recipe run on a pre-staged workspace. This packet provides the end-to-end regression proof for the July 21 demo path and makes the supersession of the canonical single-packet model (`recipe_spec.md` §1/§4/§7, see `recipe_engine_spec.md` §0/§6) visible in user-facing docs.

## Scope
- New `tests/test_recipe_e2e.py`: two end-to-end tests driving the real CLI/service against a temp pre-staged `knowledge` workspace.
  - **Test A — full operator run:** drive `research-brief` through the operator authoring loop — `grain recipe run` (starts the run: `status: pending`, `cursor` on the first step, no auto-advance), then for each step write its declared `output` artifact and call `grain recipe next` — to completion. A bare offline `run` does NOT write artifacts or reach `done`; the harness authors each artifact. Assert ordered step status transitions, that `run.json` carries `mode: "operator"`, `final` artifact (`brief.md`) exists, and `run.json` is internally consistent. (Test A may alternatively assert against a committed reference run, but the live authoring loop is the primary form.)
  - **Test B — resume after mid-run failure:** trigger an **explicit validation failure** on a step (e.g. write an `output` artifact that fails validation, or invoke the engine's validation-failure path) → `status: failed`, cursor stays on the failed step, error recorded in `run.json`. A *missing* output is NOT a failure in operator mode — it is `awaiting_input` — so the resume test must force a validation failure, not omit the artifact. Then `grain recipe resume`, write a valid artifact, and drive to `status: done`; assert `attempts` incremented on the retried step, that `resume` read `mode` from `run.json` to continue, and that no prior step artifact was mutated.
- Update `README.md`: recipe section states the step-runner engine supersedes the single-packet model; add the operator-mode quickstart; clarify recipes run **parallel to** (not inside) the task-packet loop.
- Update `docs/working/recipe_engine_spec.md` status if needed and add cross-links; keep `docs/canonical/recipe_spec.md` untouched (approval-gated — supersession is recorded as a working-doc note, not a canonical edit).
- Add a `CHANGELOG.md` entry under the v0.5.0 / unreleased section noting the recipe step-runner MVP.
- Ensure `grain docs audit` (or the repo doc link-check) passes clean after edits.

## Constraints
- **MVP only.** No auto-mode, MCP, gates polish, branching/parallel/loops, `recipe suggest`, full `workspace_kind`, per-step adapters, or apply/write-back. Test B exercises resume via an explicit validation failure, not `--auto`.
- **Operator mode never auto-completes and never writes artifacts.** `start_run` returns outcome `started` (status `pending`, cursor on the first step). `next` renders the current step's prompt and pauses at `status: awaiting_input` until the harness writes that step's `output`; the engine writes no artifacts in operator mode. Engine outcomes are `{started | prompt_ready | advanced | awaiting_gate | run_complete | noop}` — `awaiting_input` is a *status*, not an outcome (`next` returns `prompt_ready` with status `awaiting_input`).
- **`run.json` carries a `mode` field (`operator | auto`), distinct from `supervision` (`supervised | gated | autonomous`).** Never store `operator`/`auto` as a supervision value. Tests assert `mode == "operator"` and that `resume` reads `mode`.
- Tests are **offline and deterministic**: no network, no API key, no agent CLI shell-out. Operator mode writes artifacts as fixed fixture content; the test asserts engine ordering/scoping/gating, not LLM content (`recipe_engine_spec.md` §1.2).
- Tests must use a temp workspace and the bundled `research-brief` recipe; never touch the live workspace or create task packets.
- Recipes do NOT call `evaluate_workflow_state` or the packet lifecycle — assert no packet side effects.
- Run-state assertions use the locked contracts: `recipe.yaml` `apiVersion: grain.recipe/v2`, `run.json` `apiVersion: grain.recipe-run/v1`, runs under `docs/recipes/runs/<run-id>/`.
- Canonical docs (`docs/canonical/recipe_spec.md`) are approval-gated: do not edit them in this packet.

## Acceptance Criteria
- `uv run pytest tests/test_recipe_e2e.py` passes; Test A drives all six `research-brief` steps to `status: done` via the operator authoring loop (write `output` then `grain recipe next`), the `final` artifact `brief.md` exists under the run dir, and `run.json` carries `apiVersion: grain.recipe-run/v1`, `mode: "operator"`, `status: done`, and every step `done`. (A bare `grain recipe run` with no authoring loop pauses at `status: awaiting_input` and is asserted NOT to reach `done`.)
- Test B asserts: after an **explicit validation failure** (not a missing artifact) the run is `status: failed` with the cursor on the failed step and the error recorded; after `grain recipe resume` + a valid artifact write the run reaches `status: done`, the retried step's `attempts == 2`, `resume` read `mode` from `run.json`, and every prior step artifact is byte-for-byte unchanged.
- Both tests run fully offline (no network, no API key, no agent shell-out) — verifiable by the absence of any networked/`WorkflowLoopAgentConfig`-auto call in the test.
- `README.md` recipe section explicitly states the step-runner supersedes the single-packet model and includes a runnable operator-mode quickstart (`grain recipe run research-brief --param topic=...` then `grain recipe next` / `status`).
- `CHANGELOG.md` has a v0.5.0/unreleased entry naming the recipe step-runner MVP.
- The docs link/audit check (`grain docs audit`) reports clean; full suite `uv run pytest` is green with no regressions.

## Relevant Files
- `tests/test_recipe_e2e.py` *(new)* — the two end-to-end tests.
- `README.md` — recipe section: supersession statement + operator-mode quickstart.
- `CHANGELOG.md` — v0.5.0/unreleased MVP note.
- `docs/working/recipe_engine_spec.md` — status/cross-link touch-ups (working doc, not canonical).
- `docs/canonical/recipe_spec.md` — reference only; **do not edit** (approval-gated).
- `src/grain/cli/recipe.py`, `src/grain/services/recipe_service.py`, `src/grain/domain/recipe.py` — under test (built by P34-T05/T06); reference only.
- `src/grain/data/recipes/research-brief/recipe.yaml` + `steps/*.md` — bundled (gateless) recipe under test (built by P34-T06; data only). `docs/recipes/` is the workspace-recipe location, not where the bundled recipe lives.

## Model Recommendation
Sonnet-class is sufficient. This is integration-test authoring plus targeted prose edits against an already-built, well-specified engine — mechanical and bounded, no new design. Escalate to an Opus-class model only if the test reveals an engine contract gap that requires a design decision (escalate rather than patch the engine here).

## Escalation Conditions
- The end-to-end run surfaces an engine behavior that contradicts `recipe_engine_spec.md` (e.g. `run.json` shape, cursor/resume semantics, artifact atomicity) — stop and confirm; fix belongs in P34-T05/T06, not here.
- A docs edit would require changing approval-gated `docs/canonical/recipe_spec.md` — stop and raise a change proposal instead.
