# Task: Pre-staged knowledge workspace + demo runbook

## Metadata
- **ID:** P34-T07
- **Status:** draft
- **Phase:** 34 — Recipe Step-Runner MVP
- **Backlog:** P34-T07
- **Packet Path:** tasks/P34-T07/
- **Dependencies:** P34-T05, P34-T06
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Recipe-engine:** parallel engine only — this packet ships demo *content* (a pre-staged workspace + a runbook). It does NOT touch the SDLC packet loop, `evaluate_workflow_state`, or create task packets. Targets `grain.recipe/v2` recipes and `grain.recipe-run/v1` runs in operator mode.

## Objective
Deliver a self-contained, pre-staged Grain workspace under `examples/recipe-demo/` that supports the LOCKED "reference run + live next" demo — offline, deterministic, zero-risk: **(a)** a COMMITTED reference run `research-brief-0001` (`run.json` `status: done`, `cursor: format`, all 6 artifacts present) proves the finished structure with zero network, and **(b)** the live `grain recipe next` / `grain recipe status` commands drive the operator-mode state machine on a fresh run — `next` renders step 1's prompt and the run pauses at `awaiting_input`. In operator mode the engine NEVER writes artifacts: a bare `grain recipe run` returns outcome `started` (status `pending`, cursor = first step) and does NOT auto-advance or reach `done` offline; a human/agent authors each step's output, then `grain recipe next` advances the cursor. All of this WITHOUT the full `workspace_kind` integration (the engine must degrade gracefully when `workspace_kind` is absent). Alongside it, deliver a runbook markdown (the "demo-code" artifact Jacob needs the week before the Evening of Python Coding meetup) written in the venue's example style. The cross-reference to `Diwata-Infra/docs/working/grain_demo_script.md` is recorded in this packet's internal note (below) — not in the shipped README — since the shipped workspace is public and the script path is private.

## Why This Task Exists
The v0.5.0 contract's recipe engine (deliverable #2, carrying #6 and #10) must be *shown*, not just shipped. `recipe_engine_spec.md` §7 makes the MVP demo slice explicit: "One bundled `research-brief` recipe (6 steps), runnable on a **pre-staged** workspace" and "Full `workspace_kind` integration (#1) — MVP relies on a pre-staged workspace instead." This packet produces that workspace and the runnable artifact the venue requires, so the July 21 demo has a deterministic, offline, repeatable path that does not depend on the unfinished `workspace_kind` work.

## Scope
- **Included:**
  - A new pre-staged workspace at `examples/recipe-demo/` carrying a minimal Grain workspace marker (`grain.toml`) with `workspace_kind` **omitted**, exercising the spec §6 "degrade gracefully" path.
  - The `research-brief` recipe present in the workspace at `docs/recipes/research-brief/recipe.yaml` (+ `steps/*.md` prompts), reusing the bundled definition produced by P34-T06 verbatim (copy, not fork).
  - A committed, pre-recorded reference run under `examples/recipe-demo/docs/recipes/runs/research-brief-0001/` (run.json `status: done`, `cursor: format` + all 6 artifacts incl. `brief.md`) — the PRIMARY "prove the finished structure" beat (demo part (a)) and the zero-network offline fallback. Bare `grain recipe run` does not reproduce this offline; it only starts a run.
  - A runbook markdown — `examples/recipe-demo/README.md` — the venue-style "demo-code" artifact: install line, the exact operator-mode command sequence, the workflow walk-through, and the offline fallback, matching the example format at https://github.com/Jacob-Barhak/EveningOfPythonCoding. The shipped README carries **no** reference to the private `Diwata-Infra` script path.
  - Internal cross-reference (this packet note only, not shipped): record the link to `Diwata-Infra/docs/working/grain_demo_script.md` and note which "Fill in before recording" items (PyPI name, exact CLI commands, workflow file, repo URL) this artifact resolves.
- **Excluded (deferred / other packets):**
  - Auto mode / `--auto` (live agent calls) — referenced only as a pre-recorded fallback; no auto run is executed or committed here.
  - The recipe engine code, parser, run-state writer (P34-T05/T06).
  - Full `workspace_kind` integration, per-step adapters, gates polish, MCP exposure, `recipe suggest`, registry/`install`, branching/parallel/loops, apply/write-back.
  - Structural validators (MVP = output-artifact existence check only).

## Constraints
- Operator mode only: every command in the runbook is offline and deterministic (`grain recipe run` default mode, `grain recipe next`, `grain recipe status`, `grain recipe resume`). No API key, no network, no `--auto`. A bare `grain recipe run` only *starts* a run (outcome `started`, status `pending`, cursor = first step) and never writes artifacts; completion to `brief.md` offline is shown via the COMMITTED reference run, not by a live bare run. Auto mode (`--auto`, pre-recorded) is the optional "watch artifacts appear" beat, never the default path.
- The workspace must run the recipe with `workspace_kind` **absent** — proving graceful degradation. Do not add `workspace_kind` to `grain.toml`.
- Input scoping is declared-`inputs:`-only (params + named prior artifacts); the staged run.json and artifacts must reflect exactly the per-step `inputs` declared in `recipe.yaml`.
- Recipe definition carries `apiVersion: grain.recipe/v2`; the committed run carries `apiVersion: grain.recipe-run/v1`. Versions must match the bundled P34-T06 recipe byte-for-byte.
- Venue tone: open-source, anti-commercial. The runbook must not contain "best tool", pricing, competitor comparisons, or sales framing.
- No source code in this packet. Only workspace data files (yaml/md/json) under `examples/recipe-demo/` and this packet's files.
- Do not add AI/Co-Authored-By attribution to any committed content.

## Acceptance Criteria
- [ ] **Reference run proves the finished structure.** The committed reference run `examples/recipe-demo/docs/recipes/runs/research-brief-0001/` has `run.json` with `status: "done"`, `cursor: "format"` (the committed final step; there is no past-final sentinel), all 6 step records `status: "done"`, and all 6 artifacts (`01-intake.md` … `brief.md`) present and non-empty on disk (verifiable: read run.json, assert the fields with `jq`, and stat each `artifact`).
- [ ] **Live `next` renders step 1 and pauses at `awaiting_input`.** On a fresh run started from `examples/recipe-demo/`, `grain recipe next` renders step 1's (`intake`) prompt and the run status becomes `awaiting_input`; the engine writes NO artifact in operator mode (verifiable: `grain recipe next --format json` returns `outcome: "prompt_ready"` with the run/step `status: "awaiting_input"`, and no `01-intake.md` exists in the fresh run dir until a human/agent authors it). A bare `grain recipe run` returns `outcome: "started"` (status `pending`, cursor = first step) and does NOT auto-produce artifacts or reach `done` offline.
- [ ] **`status` shows the cursor.** `grain recipe status --format json` for that fresh run reports the cursor on the current step (`cursor: "intake"`) and per-step state (verifiable by piping to `jq` and asserting `cursor` + the `steps[]` statuses).
- [ ] **Graceful degradation.** The fresh run starts and `grain recipe next` renders step 1 / pauses at `awaiting_input` with `examples/recipe-demo/grain.toml` containing **no** `workspace_kind` key (verifiable: `grep -c '^workspace_kind' examples/recipe-demo/grain.toml` equals `0` and the engine still renders step 1 and pauses).
- [ ] **Reference run.json is schema-valid with distinct mode/supervision.** `examples/recipe-demo/docs/recipes/runs/research-brief-0001/run.json` validates as `apiVersion: grain.recipe-run/v1` with `mode: "operator"` and `supervision` ∈ {`supervised`, `gated`, `autonomous`} (never `operator`/`auto` as a supervision value), 6 step records all `status: "done"`, and the referenced artifacts (incl. `brief.md`) exist on disk (verifiable by a script that reads run.json and stats each `artifact`).
- [ ] **Recipe is the gateless T06 bundle, verbatim.** `examples/recipe-demo/docs/recipes/research-brief/recipe.yaml` is byte-identical to the bundled `research-brief` recipe shipped by P34-T06 (gateless — no `gate:` key on any step) and parses under `grain recipe show research-brief` (verifiable: `diff` against the bundled file exits 0).
- [ ] **Runbook reflects the locked demo.** `examples/recipe-demo/README.md` contains the install line, the reference-run beat (`cat docs/recipes/runs/research-brief-0001/run.json` / `brief.md`), the live operator-mode command sequence (`grain recipe show` / `run` / `next` / `status`), and an "Offline fallback" section that points at the committed reference run and notes auto mode (`--auto`, pre-recorded) as the optional "watch artifacts appear" beat (verifiable: `grep` for the install line, each command, and the "Offline fallback" heading). The README does **not** claim a bare `grain recipe run` produces 6 artifacts or reaches `done`, and does **not** reference the private `Diwata-Infra` path (verifiable: `grep -c grain_demo_script examples/recipe-demo/README.md` equals `0`).
- [ ] The cross-reference to `Diwata-Infra/docs/working/grain_demo_script.md` and the "Fill in before recording" items it resolves live in this packet's internal note (this `task.md` / `deliverable_spec.md`), not in any shipped file under `examples/recipe-demo/` (verifiable: the link appears in the packet dir and is absent from the shipped workspace).

## Dependencies
- **P34-T05** — the runner: `grain recipe run` (operator-mode default) / `next` / `status` / `resume` / `gate` that produces `grain.recipe-run/v1` runs; this packet's acceptance is gated on that runner existing and is the command surface the runbook drives.
- **P34-T06** — the bundled `research-brief` recipe (data only: 6 steps, `grain.recipe/v2`); this packet copies that definition into the demo workspace verbatim and diffs against it.

## Relevant Files
- `examples/recipe-demo/` — **new**, the pre-staged workspace (created by this packet).
- `examples/recipe-demo/README.md` — **new**, the venue-style demo-code runbook.
- `examples/recipe-demo/grain.toml` — **new**, minimal marker, `workspace_kind` omitted.
- `examples/recipe-demo/docs/recipes/research-brief/recipe.yaml` + `steps/*.md` — **new** (copied from P34-T06 bundle).
- `examples/recipe-demo/docs/recipes/runs/research-brief-0001/` — **new**, committed reference run.
- `docs/working/recipe_engine_spec.md` — spec; §2 data model, §3 operator mode, §6 graceful degradation, §7 MVP demo slice (read-only).
- `docs/working/v0.5.0_contract.md` — deliverables #2/#6/#10 context (read-only).
- `/Users/domicile/Diwata/Diwata-Infra/docs/working/grain_demo_script.md` — presentation run-of-show to cross-reference (read-only; cross-repo — do not edit).
- `src/grain/domain/workflow_loop.py` — idiom reference (dataclass + `__post_init__` + `VALID_*`) used by the engine packets (read-only).

## Model recommendation
**Claude Sonnet (latest).** This is content staging + prose authoring against a locked spec with no source code and objectively checkable file/command outcomes — well within Sonnet's range and cost-appropriate. Escalate to Opus only if the staged `brief.md` / step artifacts need higher narrative polish for the recorded demo.
