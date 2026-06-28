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

**`output` constraints (write-safety + uniqueness).** Each step's `output` must be a **safe
relative filename** that resolves *inside* the run dir: absolute paths, `..` traversal, and
backslash separators are rejected by the parser (and re-checked defensively at the join site, so a
malformed name can never write outside `docs/recipes/runs/<run-id>/`). Two steps must **not** declare
the same `output:` filename — output names are unique within a recipe, like step ids — so no step can
clobber another's artifact.

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

A step "completes" when its declared `output` artifact **exists, is non-empty, and the step is not
`failed`** (and the run is not `failed`) — bare existence is *not* completion (a zero-byte artifact is
treated as not-yet-done). Gates: when a step declares `gate: review` (or supervision is
`supervised`), the run enters `awaiting_gate`. `grain recipe gate approve` advances **past** the
gated step without re-running it (its artifact stands); `grain recipe gate reject` sends the step
**back for rework** — it is not a dead-end (see §5).

### 3.1 Engine operation outcomes

Every engine operation (`start_run`, `next`, `resume`) returns a result whose `outcome` is one of a
fixed set: `started | prompt_ready | advanced | awaiting_gate | run_complete | noop`. (`awaiting_input`
is a run/step *status*, not an outcome — `next` returns `prompt_ready` with the run status set to
`awaiting_input`.)

- **`start_run`** creates the run (status `pending`, `cursor` = first step) and returns `started`. It
  does **not** auto-advance.
- **`next`** acts on the current step: renders + surfaces its prompt, returning `prompt_ready` with
  the run/step in `awaiting_input` when the `output` is not yet written, is empty, or the step is
  re-entered after a failure (operator mode); marks the step `done` and advances when its `output`
  exists **and is non-empty** (and neither the step nor the run is `failed`), returning `advanced`
  (or `run_complete` at the end); returns `awaiting_gate` at a gated step; `noop` if already paused at
  a gate.
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
grain recipe gate approve|reject [--run] # approve (advance past) or reject (send back for rework)
```

`run` with no in-progress run starts one. A new run is refused **only** while a genuinely
**in-progress** run exists (status `pending | running | awaiting_input | awaiting_gate`); a
`failed` run (park it / `resume` it / start fresh) and a `done` run do **not** block a new run.
The refusal is **accurate**: with a single in-progress run it reports "a recipe run is already in
progress: <run-id>" (not "ambiguous: multiple…"); with more than one it reports the genuinely
ambiguous case and lists them. Pass `--run` to drive a specific run instead.
Text output for humans, JSON for familiars (same data).

---

## 5. Failure & resume

Failure depends on mode. In **operator mode** a missing *or empty* `output` is *not* a failure — it
is the normal `awaiting_input` pause (the engine re-surfaces the prompt on the next `next`). A run
reaches `status: failed` only on an **auto-mode** agent error (non-zero exit, timeout, or a
missing/empty `output` artifact) or an explicit validation failure; the cursor stays on the failed
step and the error is recorded in `run.json`. `grain recipe resume` retries from the cursor in the
recorded `mode`.

**Failed runs never auto-complete from a left-behind output.** When the run or the cursor step is
`failed`, `next` does **not** treat any artifact already on disk as completion — it takes the
explicit re-run path instead (operator: re-render + re-author the artifact, incrementing `attempts`;
auto: re-invoke the agent, which overwrites the artifact). Only after a fresh, non-empty artifact is
produced does the step advance.

**Atomic writes are live in both modes.** Operator mode never writes a step artifact (the human/agent
authors it). Auto mode writes each artifact through the atomic temp-file + rename protocol
(`recipe_store.write_step_artifact`): the artifact lands first, then `run.json` is rewritten — so a
crash never leaves `run.json` referencing a missing artifact.

Steps are idempotent: re-running overwrites the step's artifact and increments `attempts`. No step
ever mutates a prior step's artifact.

**Gate reject → rework (not a dead-end).** `grain recipe gate reject` on an `awaiting_gate` run
sends the gated step back for rework rather than freezing the run: the gated step is reset to a
re-runnable state (status back to `pending`, its artifact reference cleared and the rejected output
discarded from disk), the run returns to `running`, and the cursor stays on the gated step. The next
`grain recipe next` (operator) re-renders the step's prompt to be re-authored — or `grain recipe
resume` (auto) re-invokes the agent — after which the step re-enters its gate. `gate approve`, by
contrast, marks the gated step `done` without re-running it and advances the cursor.

**Definition / run robustness (typed errors, no strand).** The engine never lets a raw
`KeyError` / `FileNotFoundError` / `UnicodeDecodeError` escape:

- A recipe's `id` MUST equal its `docs/recipes/<id>/` directory name; resolution keys on the
  directory while persistence keys on `id`, so requiring them equal means a started run can always
  be re-resolved (no orphaned-run class). A mismatch is rejected at resolve/start time.
- Each path-based step `prompt:` is validated to **exist at parse/start** (fail-fast typed error),
  not discovered missing mid-run via an unguarded read.
- A `recipe.yaml` edited mid-run (its step set/order, or the run's captured `recipe_apiVersion`
  major, diverging from the run's persisted steps) raises a **typed** definition-changed error
  instead of stranding the run; the captured `recipe_apiVersion` is actually checked on every
  re-resolve.
- A non-UTF8 / binary prior artifact (or auto-mode step output) yields a **typed** decode error
  (operator: a clean failure surfaced at the CLI; auto: the step is marked `failed`), never a raw
  `UnicodeDecodeError`.
- A `{{steps.<id>}}` token whose id is a **legal `inputs` entry but not a step** (notably
  `{{steps.params}}` — `params` is an inputs keyword, not a step) raises a **typed** token error
  (`UnknownTokenError`), never a raw `KeyError` from a `run.step('params')` lookup.

**Typed errors translate at the CLI (no leak to the catch-all).** Every engine error subclasses a
single base `RecipeEngineError`, and **all** the run verbs (`run` / `next` / `resume` / `gate`)
translate that whole family to the spec `ValidationError`/exit code (a few map to the more specific
missing-path / usage codes) — exactly as `show`/`run` already translate schema errors. No typed
engine error, present or added later, leaks to the CLI catch-all as a bare `Error: …` exit 1.

**Unreadable runs are surfaced, not swallowed.** A `run.json` that is malformed, carries an
unsupported `apiVersion` major, or is **missing a required key** (e.g. `cursor`) is surfaced as a
clean "unreadable run" `ValidationError` — at the single-run load site (`status` / `next` / `gate`
with `--run`) **and** in the open-run scan. The scan must **not** silently skip an unreadable run:
swallowing it would let "no open recipe run" be reported falsely and would let a conflicting second
run start over a broken one. Targeting a readable run explicitly with `--run` bypasses the scan.

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
   This applies to **params too**: a `{{param}}` token renders only when the step lists `params` in
   its `inputs:` — otherwise it is an `UndeclaredInputError`, exactly like an out-of-scope
   `{{steps.<id>}}` reference. The surfaced `ScopedInput` list reflects only what is declared.
4. **Naming:** ✅ `grain recipe` (matches the existing contract surface).
5. **Validation hooks:** ✅ MVP completion check = output artifact **exists + is non-empty + the step
   is not `failed`** (and the run is not `failed`); per-step structural validators deferred. A step
   `output` is additionally constrained to a safe relative filename (no absolute paths / `..`
   traversal) that stays inside the run dir, and output names are unique within a recipe. At
   parse/start the engine also validates that every path-based step `prompt:` exists and that the
   recipe `id` equals its directory name, so a run cannot start against a broken or mis-located
   definition (see §5).

---

## 9. Implementation notes (fit Grain's idioms)

- Domain: `RecipeDefinition`, `RecipeStep`, `RecipeRun`, `RecipeStepRecord` dataclasses with
  `__post_init__` validation and `VALID_*` frozensets, mirroring `workflow_loop.py`.
- Reuse `WorkflowLoopAgentConfig` (shortcut/command/model) for auto-mode execution.
- New `src/grain/cli/recipe.py` + `src/grain/services/recipe_service.py`; register the `recipe`
  group via the existing pattern in `cli/__init__.py`.
- `{{param}}` / `{{steps.<id>}}` substitution reuses the existing minimal templating (no control
  flow), consistent with `prompt.md` rendering today.
