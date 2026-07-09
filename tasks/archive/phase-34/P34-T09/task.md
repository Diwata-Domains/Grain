# Task: (stretch) Auto-mode step execution

## Metadata
- **ID:** P34-T09
- **Status:** draft
- **Phase:** Phase 34 — Recipe Step-Runner MVP
- **Backlog:** P34-T09
- **Packet Path:** tasks/P34-T09/
- **Dependencies:** P34-T03, P34-T05
- **Primary Adapter:** code
- **Secondary Adapters:** none
- **Recipe-engine:** parallel engine — auto-mode step execution layered on the operator-mode state machine (P34-T03); consumes `grain.recipe/v2` definitions and `grain.recipe-run/v1` run state; reuses `WorkflowLoopAgentConfig` for agent invocation; does NOT create task packets or touch `evaluate_workflow_state` / the SDLC review-close loop. **STRETCH — NOT required for the July 21 demo (operator mode is the demo path); for post-demo or a pre-recorded demo only.**

## Objective
Add the **auto (live, networked) execution mode** to the recipe step-runner: instead of surfacing a rendered prompt for a human/familiar to fulfil (operator mode), auto mode shells out to a configured agent CLI per step, captures the agent's output into the step's declared `output` artifact, and advances the run to completion or the next gate. Agent invocation reuses `WorkflowLoopAgentConfig` (shortcut `claude|codex` or raw `command`, with optional `model`). Supervision is honored: `autonomous` runs straight through, `gated`/`supervised` (or a step's `gate: review`) still pauses at `awaiting_gate`. This is the risky path (auth, network, can hang); it is **explicitly STRETCH** and the July 21 demo ships on operator mode regardless of whether this lands.

## Why This Task Exists
`recipe_engine_spec.md` §3 defines two execution modes mirroring `grain workflow next` (operator) vs `grain workflow loop` (auto). The MVP slice (§7) ships operator mode only and marks auto mode "optional / pre-record for the demo." This packet implements that optional auto path so the engine can run end-to-end unattended — the §1.4 headless / familiar-drivable principle and v0.5.0 contract #6 (grain-as-engine) taken to its conclusion. It is gated behind P34-T03 (the operator-mode state machine it extends) and P34-T05 (the `recipe run` CLI it adds an `--auto` flag to), and is sequenced last in the phase because it is not on the demo critical path.

## Approach / Scope
**In scope:**
- **Auto-mode advance.** Add an auto path to the recipe service (extend `recipe_service.py`) that, for the cursor step, renders the same scoped prompt operator mode renders, then **shells out to the configured agent CLI** to produce the step's `output` artifact (rather than returning the prompt for a human). It then applies the identical completion/gate/advance logic operator mode uses (existence check, cursor advance, `awaiting_gate` on gate/supervision), to completion or the next gate.
- **Agent config reuse.** Resolve the agent invocation from `WorkflowLoopAgentConfig` (`mode` = `shortcut` with `shortcut ∈ {claude, codex}` or `mode` = `command` with a raw `command`, plus optional `model`). Do NOT define a new agent-config shape; reuse the existing dataclass and its `__post_init__` validation. The per-step optional `model:` key (spec §2.1) biases the model passed to the agent when present.
- **`--auto` opt-in.** Extend the existing `grain recipe run` verb (P34-T05) with an `--auto` flag. Default remains operator mode (offline, deterministic). `--auto` is also implied when the resolved supervision is `autonomous`.
- **Supervision honored.** `autonomous` advances through all non-gated steps; `gated`, or any step declaring `gate: review`, still enters `awaiting_gate` and stops (gate approve/reject resume is owned by P34-T05). Auto mode never bypasses a gate. **`supervised` is treated as gated-equivalent for this MVP** — it pauses at `awaiting_gate` rather than after every step; full supervised-mode polish (pause-after-every-step) is deferred per spec §7. Encode supervised as the same "pause at a gate" path as `gated`; do not implement a distinct per-step pause here.
- **Failure capture.** A non-zero agent exit, a timeout, or a missing `output` artifact after the agent returns marks the step and run `status: failed`, records the error (and an `attempts` increment) in `run.json`, and leaves the cursor on the failed step for `grain recipe resume`. Completion is the locked **output-artifact existence check only** (spec §8.5) — no non-empty/structural check. Idempotent re-run overwrites the step artifact; no prior step's artifact is ever mutated.
- **Subprocess safety.** Invoke the agent via a non-shell-injectable subprocess call with a bounded timeout and the workspace as cwd; capture stdout/stderr for the error record. No network/auth code lives in Grain itself — it only shells to the user-configured CLI.
- **Idioms.** Any new result/config helpers are dataclasses with `__post_init__` validation and `VALID_*` frozensets (reuse `VALID_SUPERVISION_LEVELS`, `VALID_AGENT_SHORTCUTS` from `domain/workflow_loop.py`); the operator-vs-auto split mirrors `workflow next` vs `workflow loop`.

**Out of scope (deferred — do NOT build here):**
- Operator-mode logic itself (P34-T03) — auto mode reuses it, does not reimplement it.
- The `recipe run/next/status/resume/gate` verbs themselves (P34-T05) — this packet only adds the `--auto` flag to `run`.
- A new agent-config file/format — reuse `WorkflowLoopAgentConfig` and the existing `docs/runtime/workflow_loop.yaml` shape.
- MCP exposure, `recipe suggest`, `scaffold`, registry/install.
- Branching, conditional, parallel, or loop steps; per-step `adapter` scoping.
- Structural output validators (MVP = existence check only); apply / write-back to office docs.
- Full `workspace_kind` resolution (degrade gracefully if absent).

## Deliverable
Extended `src/grain/services/recipe_service.py` adding an auto-mode advance path that shells to a `WorkflowLoopAgentConfig`-configured agent per step, plus the `--auto` flag on `grain recipe run`, with tests that drive an auto run to completion using a **stubbed/fake agent command** (a local script that writes the step artifact) — never a real network call.

## Acceptance Criteria
- With the agent configured as a fake `command` that writes the step's `output` file, `grain recipe run <no-gate-recipe> --auto` (pre-staged workspace) exits 0, drives the run to `status: done`, and writes the `final` artifact — asserted by a test reading `run.json` and the artifact, using NO real network/API key.
- `--auto` is opt-in: `grain recipe run <id>` without `--auto` (and non-`autonomous` supervision) takes the operator path and does NOT invoke any agent subprocess — asserted by a test that fails if the fake agent is called.
- On a recipe whose step declares `gate: review` (or supervision `gated`/`supervised` — supervised is treated as gated-equivalent for this MVP), an `--auto` run halts at `status: awaiting_gate` with the cursor on the gated step and does not execute past it — asserted via `run.json` state.
- A fake agent that exits non-zero (or leaves the `output` artifact missing) marks the step and run `status: failed`, records the error in `run.json`, leaves the cursor on the failed step, and `grain recipe resume` re-enters and increments that step's `attempts` — asserted by a test. (Completion is the output-artifact existence check only; an empty-but-present artifact counts as produced.)
- Auto mode resolves the agent from `WorkflowLoopAgentConfig` (shortcut `claude|codex` or `command`, optional `model`) and passes the per-step `model:` when set; an invalid agent config raises before any step runs — asserted by a unit test on the resolution helper.
- The module imports and the auto path is reachable with no real network access; `recipe_service.py` references neither `evaluate_workflow_state` nor any task-packet/review/close service — asserted by test + grep.

## Dependencies
- **P34-T03** — `RecipeService` operator-mode engine (render scoped prompt, completion detection, cursor/gate/resume state machine). Auto mode extends this; it reuses the advance/gate/persist logic rather than duplicating it.
- **P34-T05** — `grain recipe run` CLI verb (and the `recipe` Click group). This packet adds the `--auto` flag to that existing verb.

## Relevant Files
- `src/grain/services/recipe_service.py` — EXTEND (the deliverable): add the auto-mode advance path + agent-invocation helper.
- `src/grain/cli/recipe.py` — EXTEND: add `--auto` to the `run` verb (wiring only; calls the service).
- `tests/services/test_recipe_service.py` — EXTEND / `tests/cli/test_recipe_run_cli.py` — auto-mode tests using a fake agent command (no network).
- `src/grain/domain/workflow_loop.py` — `WorkflowLoopAgentConfig` (`mode`/`shortcut`/`model`/`command`), `VALID_AGENT_SHORTCUTS`, `VALID_SUPERVISION_LEVELS` — reused, not redefined.
- `docs/runtime/workflow_loop.yaml` — canonical workspace agent-config file (the runtime path `WorkflowLoopAgentConfig`/`workflow_loop_config_service` already loads); its shortcut/command/model shape is reused as-is for the recipe agent. (Seeded from the bundled template `src/grain/data/runtime/workflow_loop.yaml`; the canonical *load* path is `docs/runtime/workflow_loop.yaml`.)
- `docs/working/recipe_engine_spec.md` — §3 (auto mode), §5 (failure & resume), §7 (MVP vs deferred — auto is optional/pre-recorded), §9 (reuse `WorkflowLoopAgentConfig`).

## Constraints
- **STRETCH / not on the demo critical path.** Operator mode (P34-T03/T05) is the July 21 demo; if this slips it is dropped, not rushed. The demo, if it shows auto mode at all, uses a pre-recording (spec §3, §7).
- Parallel engine only: no import of or call into `evaluate_workflow_state`, task-packet lifecycle, or review/close services (spec §1, §6).
- Reuse `WorkflowLoopAgentConfig` for agent invocation — do NOT define a new agent-config shape (spec §9).
- Auto mode never bypasses a gate or supervision pause; gate approve/reject resume stays in P34-T05.
- `run.json` is the single source of truth; update it only AFTER the artifact lands; failures recorded with the cursor left on the failed step (spec §2.2, §5).
- Agent subprocess: bounded timeout, no shell injection, workspace as cwd; Grain holds no network/auth code itself (it only shells to the user's configured CLI).
- Tests use a fake/stub agent command (a local script) — NEVER a real network call or API key.

## Escalation Conditions
- P34-T03 does not expose a reusable advance/gate/persist seam an auto path can plug into (i.e. auto mode would have to reimplement the state machine) — reconcile the service interface before coding.
- The configured agent CLI contract (how a step prompt is passed and where the agent is expected to write the `output` artifact) is ambiguous — confirm the prompt-delivery / artifact-write convention rather than guessing.
- A locked decision in `recipe_engine_spec.md` §8 appears to conflict with an implementation need — surface, do not reopen unilaterally.

## Model Recommendation
**Claude Opus** (or strongest available). Subprocess orchestration with timeouts/failure capture, reuse of the operator state machine without duplicating it, and correct gate/supervision honoring under live execution are the kind of interacting invariants where a subtle bug corrupts a run or hangs unattended. Scope is bounded (one service extension + a CLI flag + fake-agent tests), so correctness, not breadth, dominates.
