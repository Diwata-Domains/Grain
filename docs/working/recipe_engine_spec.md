# Grain Recipe Engine (Step-Runner) Spec

**Status:** Working draft (v0.5.0) — **supersedes the single-packet model in canonical
`recipe_spec.md` §1, §4, §7.** Promote to canonical via change proposal during the v0.5.0
planning pass. Authored 2026-06-26.

MVP shipped (P34-T05/T06) and proven end-to-end (P34-T08:
`tests/test_recipe_e2e.py` — full operator run + resume after an explicit validation
failure). The supersession is now surfaced to users in the repo `README.md` ("Recipes"
section) and `CHANGELOG.md` (v0.5.0/unreleased); canonical `recipe_spec.md` stays
untouched (approval-gated).

**One-line:** turn a recipe from a *configured entry point into the SDLC packet loop* into a
*general, deterministic, multi-step workflow engine* — the primitive the rest of the Diwata
stack (and familiars) compose on.

---

## 0. Why this supersedes the canonical recipe model

Canonical `recipe_spec.md` defines a recipe as "the full execute → review → close pattern
configured for a specific use case" that "does not bypass the workflow engine" — i.e. a recipe
prepares **one** task packet and stops (§4). That makes recipes a coding-SDLC convenience, not a
general workflow engine. It cannot express "intake → gather → outline → draft → self-check →
format" as discrete, ordered, inspectable steps.

This spec replaces that with a **step-runner**: a recipe is an ordered list of steps, each
producing an inspectable artifact, with memory flowing between steps via declared inputs. It runs
as its own small linear state machine **parallel to** (never bolted onto) the SDLC packet loop.

This is the v0.5.0 contract's deliverable #2 (`grain recipe` execution), and it carries #10
(graduated ceremony) and #6 (grain-as-engine / familiar-drivable) as first-class concerns.

---

## 1. Design principles (the contract)

1. **Parallel, not bolted-on.** The step-runner is a separate engine. It does NOT touch
   `evaluate_workflow_state`, task-packet lifecycle, or review/close semantics. A workspace may
   use both engines.
2. **Determinism = process, not output.** Grain owns step *ordering, scoping, and gating*; the
   model owns *content within a step*. The sequence is fixed and replayable; LLM output is not
   claimed to be identical.
3. **File-backed, no hidden state.** Definitions and run state live in the workspace as plain
   files (not `.grain/`, not a DB, not a daemon) — inspectable and diff-able, consistent with
   Grain's existing posture.
4. **Headless-first / familiar-drivable.** Every operation is driveable end-to-end by an agent
   with no human and no browser: `--format json` on everything, file-backed resume, idempotent
   steps, and an MCP surface. (v0.5.0 guiding principle.)
5. **Versioned engine contract.** Recipe definitions and run state carry an `apiVersion`. The
   engine rejects unknown majors. Downstream tools/familiars depend on this contract.
6. **Right-sized ceremony.** Default is no gates (quick lane). Steps opt into review gates where
   they matter. Reuses the existing `supervised | gated | autonomous` supervision levels.
7. **Minimal context per step.** A step receives only its declared `inputs` (params + named prior
   artifacts), not the whole run — preserving Grain's minimal-context principle.

---

## 2. Data model

### 2.1 `recipe.yaml` — `apiVersion: grain.recipe/v2`

Lives in `docs/recipes/<id>/recipe.yaml` (same location as today). v2 adds `steps`; existing v1
keys (`name`, `description`, `category`, `parameters`) are retained.

```yaml
apiVersion: grain.recipe/v2
id: research-brief
name: "Research Brief"
description: "Produce a sourced research brief on a topic"
category: research          # research | docs | data | ops | content | code | custom
workspace_kind: knowledge   # optional; default: any (degrade gracefully if unset)
supervision: gated          # default run mode: supervised | gated | autonomous

params:
  - id: topic
    label: "Topic"
    required: true
    type: string

steps:
  - id: intake
    name: "Frame the topic"
    prompt: steps/intake.md          # path (or `inline:` block); {{topic}} substitution
    inputs: [params]                 # what this step may read
    output: 01-intake.md             # artifact this step must produce
  - id: gather
    name: "Gather sources"
    prompt: steps/gather.md
    inputs: [params, intake]         # prior step artifacts by id
    output: 02-sources.md
  - id: outline
    prompt: steps/outline.md
    inputs: [intake, gather]
    output: 03-outline.md
  - id: draft
    prompt: steps/draft.md
    inputs: [outline, gather]
    output: 04-draft.md
  - id: self_check
    prompt: steps/self_check.md
    inputs: [draft, gather]
    output: 05-review.md
    gate: review                     # pause for approval after this step (none | review)
  - id: format
    prompt: steps/format.md
    inputs: [draft, self_check]
    output: brief.md

final: brief.md                      # the deliverable artifact
```

Per-step optional keys: `adapter` (tune context selection via `adapter_profiles`), `model`
(model-class bias). Unknown keys are rejected under strict schema validation.

### 2.2 `run.json` — `apiVersion: grain.recipe-run/v1`

A run is a directory `docs/recipes/runs/<run-id>/` containing `run.json` plus the step artifacts.
`run.json` is the single source of truth; resume = re-read it.

```json
{
  "apiVersion": "grain.recipe-run/v1",
  "run_id": "research-brief-0001",
  "recipe": "research-brief",
  "recipe_apiVersion": "grain.recipe/v2",
  "params": {"topic": "GLP-1 obesity market"},
  "mode": "operator",
  "supervision": "gated",
  "status": "awaiting_gate",
  "cursor": "self_check",
  "steps": [
    {"id": "intake", "status": "done", "artifact": "01-intake.md", "attempts": 1},
    {"id": "gather", "status": "done", "artifact": "02-sources.md", "attempts": 1},
    {"id": "outline", "status": "done", "artifact": "03-outline.md", "attempts": 1},
    {"id": "draft", "status": "done", "artifact": "04-draft.md", "attempts": 1},
    {"id": "self_check", "status": "awaiting_gate", "artifact": "05-review.md", "attempts": 1, "gate": "review"},
    {"id": "format", "status": "pending"}
  ]
}
```

Run `status`: `pending | running | awaiting_input | awaiting_gate | done | failed`. Step `status`:
`pending | running | awaiting_input | awaiting_gate | done | failed`.

- **`mode`** (`operator | auto`) records how the run is driven; it is distinct from `supervision`.
  `mode` is set at `recipe run` time (`--auto` ⇒ `auto`, default ⇒ `operator`) and is what `resume`
  reads to continue correctly.
- **`awaiting_input`** is the operator-mode pause: the engine has rendered the current step's prompt
  and is waiting for the human/agent to write the step's `output` artifact. (Auto mode never enters
  it — it writes the artifact itself.)
- Per-step **`gate`** is persisted on the step record whenever the recipe declares one (see
  `self_check`), so a resumed run still knows to pause there.
- On a **`done`** run, `cursor` holds the final step's id (e.g. `format`); there is no null/sentinel
  cursor. (The committed reference run `research-brief-0001` shows `status: done`, `cursor: format`.)
- Timestamps (`created`, `updated`, per-step `started`/`ended`) are stamped by the engine. Artifacts
  are written atomically; `run.json` is updated only after the artifact lands (no
  partial-corruption window).

---

## 3. Execution model

Two modes, mirroring the existing `grain workflow next` vs `grain workflow loop` split:

- **Operator mode (default, safe, offline):** `grain recipe next` renders the current step's
  prompt with its scoped inputs and surfaces it (+ the path to write the output artifact). A human
  or agent runs it and writes the artifact; `grain recipe next` advances the cursor. No network,
  no API key — the deterministic-and-inspectable demo path.
- **Auto mode (live, networked):** `grain recipe run --auto` (or `supervision: autonomous`) shells
  out to the configured agent CLI per step — reusing `WorkflowLoopAgentConfig` (shortcut
  `claude|codex` or `command`, with `model`) — executes the step, writes the artifact, and advances
  to completion or the next gate. This is the risky path (auth/network/can-hang); **pre-record for
  the demo.**

A step "completes" when its declared `output` artifact exists and (if applicable) passes
validation. Gates: when a step declares `gate: review` (or supervision is `supervised`), the run
enters `awaiting_gate`; `grain recipe gate approve|reject` resumes or stops it.

### 3.1 Engine operation outcomes

Every engine operation (`start_run`, `next`, `resume`) returns a result whose `outcome` is one of a
fixed set: `started | prompt_ready | advanced | awaiting_gate | run_complete | noop`. (`awaiting_input`
is a run/step *status*, not an outcome — `next` returns `prompt_ready` with the run status set to
`awaiting_input`.)

- **`start_run`** creates the run (status `pending`, `cursor` = first step) and returns `started`. It
  does **not** auto-advance.
- **`next`** acts on the current step: renders + surfaces its prompt, returning `prompt_ready` with
  the run/step in `awaiting_input` when the `output` is not yet written (operator mode); marks the
  step `done` and advances when its `output` exists, returning `advanced` (or `run_complete` at the
  end); returns `awaiting_gate` at a gated step; `noop` if already paused at a gate.
- **`resume`** re-reads `run.json` and continues from the cursor in the run's recorded `mode`.

`supervision` (`supervised | gated | autonomous`) is **parsed into `RecipeDefinition`** (not
accept-and-ignore) and copied into `run.json` at `start_run`. It governs *where* a run pauses:
`gated` only at steps with `gate: review`; `supervised` after every step; `autonomous` runs straight
through (auto mode).

---

## 4. CLI surface (all support `--format json`)

```
grain recipe list                       # bundled + workspace recipes
grain recipe show <id>                   # steps, params, gates
grain recipe scaffold <id>               # new recipe skeleton in docs/recipes/<id>/
grain recipe run <id> --param k=v ...    # start a run; advance to completion or first gate
grain recipe run <id> --auto             # auto mode (shell to agent per step)
grain recipe next [--run <id>]           # advance ONE step (operator mode)
grain recipe status [--run <id>]         # run state: cursor, per-step status, artifacts
grain recipe resume <id|run-id>          # resume a failed/paused run from the cursor
grain recipe gate approve|reject [--run] # pass/stop a review gate
```

`run` with no open run starts one; with an open run, refuses unless `--run` disambiguates.
Text output for humans, JSON for familiars (same data).

---

## 5. Failure & resume

Failure depends on mode. In **operator mode** a missing `output` is *not* a failure — it is the
normal `awaiting_input` pause (the engine re-surfaces the prompt on the next `next`). A run reaches
`status: failed` only on an **auto-mode** agent error or an explicit validation failure; the cursor
stays on the failed step and the error is recorded in `run.json`. `grain recipe resume` retries from
the cursor in the recorded `mode`. Steps are idempotent: re-running overwrites the step's artifact
and increments `attempts`. No step ever mutates a prior step's artifact.

---

## 6. Relationship to existing systems

- **SDLC loop:** untouched. Recipes are a separate engine; `evaluate_workflow_state` and the
  packet lifecycle are not involved.
- **Packets:** recipes do **not** create task packets. *(This is the explicit reversal of canonical
  §1/§4/§7.)* The old "recipe = one packet, gated at review/close" behavior is expressible as a
  one-step recipe with `gate: review`, so the prior use case is not lost.
- **Adapters:** a step may declare `adapter:` to scope its context (reuse `adapter_profiles`).
- **`workspace_kind`:** recipes are the primary consumer of `knowledge` workspaces, but must
  **degrade gracefully** when `workspace_kind` is absent (so a recipe can run in a pre-staged
  workspace before the full workspace-kind work lands — see demo MVP).
- **MCP / grain-as-engine (#6):** expose `recipe_list/show/run/next/status/gate` as MCP tools so
  familiars drive recipes headlessly. Extends today's 5-tool MCP surface.
- **Marker/manifest:** see the `grain.toml` canonical-marker note in `v0.5.0_contract.md` §2.1.

---

## 7. Demo MVP slice (ship for July 21) vs deferred

**MVP (must ship):**
- `apiVersion: grain.recipe/v2` parser (linear steps, params, `inputs`, `output`, `final`)
- `grain recipe list | show | run | next | status | resume`
- File-backed `RecipeRun` (`run.json` + artifacts) under `docs/recipes/runs/`
- **Operator mode** (the deterministic, offline demo path); auto mode optional/pre-recorded
- One bundled **`research-brief`** recipe (6 steps), runnable on a **pre-staged** workspace
- Resume on failure

**Deferred (post-demo):**
- Gates / `supervised` mode polish (keep `gate:` in the schema so the contract is stable; demo
  recipe uses none or one)
- MCP exposure (#6), branching/conditional steps, parallel steps, loops
- `grain recipe suggest` (#3), `recipe install` (registry)
- Full `workspace_kind` integration (#1) — MVP relies on a pre-staged workspace instead
- Per-step `adapter` scoping, apply/write-back to office docs

**Fallback:** if the engine isn't solid by the ~July 8 GO/NO-GO, the adapter "one loop, any
domain" demo ships instead; the engine lands a week later, designed right rather than rushed.

---

## 8. Resolved design decisions (locked 2026-06-26)

1. **Run storage:** ✅ `docs/recipes/runs/<run-id>/` — engine stays decoupled from packets and
   inspectable.
2. **`recipe run` default mode:** ✅ operator (deterministic, offline); `--auto` is opt-in.
3. **Input scoping:** ✅ declared `inputs:` only (params + named prior artifacts); no auto-include.
4. **Naming:** ✅ `grain recipe` (matches the existing contract surface).
5. **Validation hooks:** ✅ MVP does output-artifact existence-check only; per-step structural
   validators deferred.

---

## 9. Implementation notes (fit Grain's idioms)

- Domain: `RecipeDefinition`, `RecipeStep`, `RecipeRun`, `RecipeStepRecord` dataclasses with
  `__post_init__` validation and `VALID_*` frozensets, mirroring `workflow_loop.py`.
- Reuse `WorkflowLoopAgentConfig` (shortcut/command/model) for auto-mode execution.
- New `src/grain/cli/recipe.py` + `src/grain/services/recipe_service.py`; register the `recipe`
  group via the existing pattern in `cli/__init__.py`.
- `{{param}}` / `{{steps.<id>}}` substitution reuses the existing minimal templating (no control
  flow), consistent with `prompt.md` rendering today.
