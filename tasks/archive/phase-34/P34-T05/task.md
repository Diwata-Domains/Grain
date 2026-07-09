# Task: CLI — grain recipe run / next / status / resume / gate

## Metadata
- **ID:** P34-T05
- **Status:** done
- **Phase:** Phase 34 — Recipe Step-Runner MVP
- **Backlog:** P34-T05
- **Packet Path:** tasks/P34-T05/
- **Dependencies:** P34-T03, P34-T04
- **Primary Adapter:** code
- **Secondary Adapters:** none
- **Recipe-engine:** parallel engine — CLI surface over the run state machine; does NOT create task packets or touch `evaluate_workflow_state` / the SDLC review-close loop. Consumes `grain.recipe/v2` definitions and `grain.recipe-run/v1` run state.

## Objective
Build the operator-facing CLI verbs for executing a recipe run: `grain recipe run`, `next`, `status`, `resume`, and `gate approve|reject`. These wire the recipe service and domain models built in P34-T03 into the `recipe` Click group that P34-T04 creates and registers (the group this packet extends), mirroring the `grain workflow next` CLI pattern. The default `run` mode is operator (offline, deterministic): `run` starts the run and advances the cursor until the run reaches `awaiting_input`, `awaiting_gate`, or `run_complete` — without any network or API call. Because a fresh run has no step artifacts authored yet, operator `run` pauses at `awaiting_input` on the first step (a missing output in operator mode is a pause, not a failure); reaching `done` requires interleaving artifact authoring with `grain recipe next`. The run carries `mode: operator` (distinct from `supervision`), set at `run` time. Every verb supports `--format json` so a familiar can drive the full run loop headlessly.

## Why This Task Exists
Carries the v0.5.0 contract deliverable #2 (`grain recipe` execution) and #6 (grain-as-engine / familiar-drivable), and is the operator-mode demo path called out in `recipe_engine_spec.md` §3, §4, §7. P34-T03 produces the domain + service layer and P34-T04 creates the `recipe` CLI group; this packet is the CLI that makes a run actually drivable end-to-end and is required for the July 21 demo MVP slice.

## Scope
- Extend `src/grain/cli/recipe.py` (the `recipe` Click group; `list`/`show`/`scaffold` land in other P34 packets) with five verbs:
  - `grain recipe run <id> [--param k=v ...]` — start a run and, in operator mode (default), advance the cursor until the run reaches `awaiting_input` (first un-authored step), `awaiting_gate`, or `run_complete`. Records `mode: operator` on the run. `--run <run-id>` disambiguates when an open run exists.
  - `grain recipe next [--run <run-id>]` — advance exactly ONE step (operator mode).
  - `grain recipe status [--run <run-id>]` — report run state (status, cursor, per-step status + artifacts).
  - `grain recipe resume <id|run-id>` — re-enter a paused/`failed` run from its cursor in the run's recorded `mode`; it RE-RUNS the cursor step (re-renders the prompt / re-executes, incrementing `attempts`). On an `awaiting_gate` run, `resume` does NOT pass the gate — use `gate approve` for that.
  - `grain recipe gate approve|reject [--run <run-id>]` — decide a review gate on an `awaiting_gate` run: `approve` advances PAST the gated step (to the next step / completion) without re-running it; `reject` leaves the run stopped at the gate.
- `--format json` on all five verbs (read from `ctx.obj["fmt"]`, same as `workflow.py`); text output for humans, equivalent JSON for familiars.
- Operator-mode semantics only: `next`/`run` render the current step's prompt with its scoped inputs and surface the artifact path to write; advance only when the declared `output` artifact exists (existence check only — no structural validation). When the `output` is not yet written, the step/run sit in `awaiting_input` and the prompt is re-surfaced on the next `next` — a missing output is a pause, never a failure, in operator mode.
- Multi-run disambiguation: `run`/`next`/`status`/`gate` with exactly one open run operate on it implicitly; with multiple/ambiguous open runs they require `--run` and raise `UsageError` otherwise.

## Out of Scope (deferred — do NOT build here)
- `--auto` / auto-mode execution and `WorkflowLoopAgentConfig` wiring (separate P34 packet).
- `grain recipe list | show | scaffold` (other P34 packets).
- Recipe parsing, run.json read/write, and step-advance logic itself — those are P34-T03 (domain + service); P34-T04 creates the `recipe` CLI group; this packet only calls them.
- MCP exposure, branching/parallel/loops, `recipe suggest`, structural validators, per-step adapters, apply/write-back, full `workspace_kind`.

## Deliverable
- Extended `src/grain/cli/recipe.py` with `run`, `next`, `status`, `resume`, and `gate` subcommands registered on the existing `recipe` group, each honoring `ctx.obj["fmt"]` and `ctx.obj["repo"]`.
- Each verb returns a `CommandResult`-shaped payload printed via the shared output helper (text + json), with run state sourced from the P34-T03 service (no direct file parsing in the CLI layer).
- Tests in `tests/` (Click `CliRunner`) covering: an operator `run` pausing at `awaiting_input` on a no-gate recipe, then reaching `done` by interleaving artifact authoring with `next`; a run halting at `awaiting_gate`; `next` advancing exactly one step (cursor moves by one; steps array length fixed); `status` reflecting cursor + per-step status; `gate approve` advancing past the gate and `gate reject` stopping; `resume` re-running from a failed/paused cursor (and not passing a gate); ambiguous-open-run `UsageError`; and `--format json` shape (including `mode`, `created`, `updated`) on each verb.

## Acceptance Criteria
- `grain recipe run <id> --param topic=X` on a no-gate recipe (pre-staged workspace) exits 0 and creates `docs/recipes/runs/<run-id>/run.json` with `mode: operator` and `status: awaiting_input` (a fresh operator run does NOT reach `done` by itself — it pauses on the first un-authored step). Reaching `status: done` with the `final` artifact written is demonstrated by interleaving artifact authoring with `grain recipe next` until `run_complete` — verified by a `CliRunner` test that asserts the post-`run` status is `awaiting_input`, then writes each step's `output` and calls `next`, asserting final `run.json` status `done` and `final` artifact existence.
- On a recipe whose step declares `gate: review` (with that step's `output` authored so it reaches the gate), `grain recipe run`/`next` halts with run `status: awaiting_gate` and the cursor on the gated step; `grain recipe gate approve` advances PAST it (cursor moves to the next step, the gated step is not re-run) and `grain recipe gate reject` leaves the run stopped at the gate; `grain recipe resume` on the same `awaiting_gate` run does NOT pass the gate (still `awaiting_gate`) — asserted in tests via `run.json` state.
- `grain recipe next` (with the current step's `output` authored) advances by exactly one step per invocation — the `cursor` moves to the next step id (equivalently, the count of `status: done` steps increases by exactly one) while the `steps` array length stays fixed — verified by a test authoring two outputs and calling `next` twice.
- `grain --format json recipe status` emits valid JSON (from `run_to_dict`) containing `run_id`, `mode`, `supervision`, `status`, `cursor`, `created`, `updated`, and a `steps` array with per-step `id`/`status`/`artifact`, asserted by `json.loads` in a test; the `created`/`updated`/`mode` fields round-trip (re-loading the run preserves them).
- `grain recipe run <id>` / `next` / `status` / `gate` with two open runs and no `--run` exit non-zero with a `UsageError` naming the ambiguity — asserted by a test.
- `grain recipe resume <run-id>` on a `failed` run re-enters from the cursor and increments that step's `attempts` (never mutating a prior step's artifact) — asserted by a test.

## Constraints
- CLI layer stays thin: all run/parse/advance logic lives in the P34-T03 service and domain; the CLI only marshals args, calls the service, and formats output (same separation as `cli/workflow.py` → `services/workflow_service.py`).
- Read `fmt` and `repo` from `ctx.obj` exactly as `workflow.py` does; resolve the workspace via `resolve_repo_root(repo)`.
- Operator mode performs NO network/API calls and requires no API key (deterministic, offline demo path per spec §3).
- Reuse `VALID_*` frozensets and the run/step `status` vocabulary defined in P34-T03 domain (`pending | running | awaiting_input | awaiting_gate | done | failed`); do not redefine status strings in the CLI.
- Keep `mode` (`operator | auto`) DISTINCT from `supervision` (`supervised | gated | autonomous`): the CLI records `mode: operator` on a run started without `--auto`, and never stores `operator`/`auto` as a supervision value (or vice-versa).
- Run storage path is `docs/recipes/runs/<run-id>/`; the CLI must not write anywhere else and must not create or touch task packets.
- Errors raised as `UsageError` / `click.ClickException` so exit codes are non-zero and JSON error payloads stay consistent with the rest of the CLI.

## Escalation Conditions
- P34-T03 / P34-T04 interfaces differ materially from what this packet assumes (see deliverable_spec.md §"Assumed upstream interfaces") — reconcile before implementing.
- `run.json`/`recipe.yaml` schema needs a field not present in the spec data model (§2) to satisfy a verb — raise rather than extend the schema ad hoc.

## Model Recommendation
Claude Sonnet (mid-tier). Mechanical CLI wiring over an existing service layer with a clear in-repo precedent (`cli/workflow.py`); no novel design. Escalate to Opus only if upstream service signatures require rework.
