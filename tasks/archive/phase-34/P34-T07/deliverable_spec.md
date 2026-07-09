# Deliverable Spec — P34-T07: Pre-staged knowledge workspace + demo runbook

Concrete done-definition. No source code is written by this packet; the runner is supplied by
P34-T05 (the `grain recipe run/next/status/resume/gate` runner) and the recipe data by P34-T06 (the
bundled `research-brief` recipe). This packet stages a workspace + reference run + runbook so the
demo is offline, deterministic, and `workspace_kind`-free.

---

## 1. Files created (exact tree)

```
examples/recipe-demo/
├── README.md                              # venue-style demo-code runbook (§5)
├── grain.toml                             # minimal marker, workspace_kind OMITTED (§2)
└── docs/
    └── recipes/
        ├── research-brief/
        │   ├── recipe.yaml                # copy of P34-T06 bundle, grain.recipe/v2 (§3)
        │   └── steps/
        │       ├── intake.md
        │       ├── gather.md
        │       ├── outline.md
        │       ├── draft.md
        │       ├── self_check.md
        │       └── format.md
        └── runs/
            ├── .gitkeep                    # live runs land here
            └── research-brief-0001/        # committed reference run (§4)
                ├── run.json                # grain.recipe-run/v1
                ├── 01-intake.md
                ├── 02-sources.md
                ├── 03-outline.md
                ├── 04-draft.md
                ├── 05-review.md
                └── brief.md                # final artifact
```

No files outside `examples/recipe-demo/` (and this packet dir) are created or modified.

---

## 2. `examples/recipe-demo/grain.toml` (workspace marker)

Minimal marker sufficient for the resolver to treat the dir as a Grain workspace, with
`workspace_kind` deliberately **absent** to exercise spec §6 graceful degradation.

```toml
# Pre-staged demo workspace for the Grain recipe step-runner (P34).
# workspace_kind is intentionally omitted: the recipe engine must degrade gracefully
# (recipe_engine_spec.md §6) so the demo runs before the full workspace_kind work lands.
name = "recipe-demo"
# workspace_kind = "knowledge"   # intentionally commented out — do NOT enable for the MVP demo
```

Done-check: `grep -c '^workspace_kind' examples/recipe-demo/grain.toml` returns `0`, and a fresh
`grain recipe run` + `grain recipe next` from this dir still renders step 1 and pauses at
`awaiting_input` (graceful degradation). (A bare run does not auto-complete offline — completion is
shown via the committed reference run.)

---

## 3. `docs/recipes/research-brief/recipe.yaml` (`apiVersion: grain.recipe/v2`)

Byte-identical copy of the bundled recipe from P34-T06. The T06 bundle is **gateless** (no
`gate: review` on any step), so the operator-mode demo reaches `brief.md` without an approval stop.
Shape it must conform to (per spec §2.1):

```yaml
apiVersion: grain.recipe/v2
id: research-brief
name: "Research Brief"
description: "Produce a sourced research brief on a topic"
category: research
supervision: gated            # default carried; demo overrides to operator mode at run time
params:
  - id: topic
    label: "Topic"
    required: true
    type: string
steps:
  - id: intake
    name: "Frame the topic"
    prompt: steps/intake.md
    inputs: [params]
    output: 01-intake.md
  - id: gather
    name: "Gather sources"
    prompt: steps/gather.md
    inputs: [params, intake]
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
  - id: format
    prompt: steps/format.md
    inputs: [draft, self_check]
    output: brief.md
final: brief.md
```

`workspace_kind` is NOT set on the recipe (matches the workspace's degraded mode). `steps/*.md`
are the prompt bodies with `{{topic}}` / `{{steps.<id>}}` substitution markers; copied verbatim
from the P34-T06 bundle.

Done-check: `diff examples/recipe-demo/docs/recipes/research-brief/recipe.yaml <bundled recipe>`
exits 0; `grain recipe show research-brief` (run from the workspace) parses and lists 6 steps.

**Demo-flow note (gateless):** the P34-T06 bundle declares no `gate: review` on any step, so the
operator-mode demo runs straight through to `brief.md` with no approval stop and no on-stage `grain
recipe gate` beat. The demo copy must remain byte-identical to that gateless bundle — do not add a
gate to the demo copy. (`gate:` stays in the engine schema for post-demo recipes; the bundled demo
recipe simply uses none, per spec §7 "demo recipe uses none.")

---

## 4. Reference run — `docs/recipes/runs/research-brief-0001/run.json` (`grain.recipe-run/v1`)

A complete, committed `done` run (spec §2.2) produced once in operator mode (the engine renders each
step via `grain recipe next`; a human/agent authors each `output` artifact, since the engine never
writes artifacts in operator mode) with `topic: "GLP-1 obesity market"`, then committed as the
structure-proof + offline fallback. Note `mode` and
`supervision` are distinct fields (spec §2.2): `mode: "operator"` records how the run was driven,
while `supervision` carries a valid level (`supervised | gated | autonomous`) copied from the recipe
at `start_run`. Never store `"operator"`/`"auto"` as a `supervision` value — it would fail
`__post_init__` validation. Final shape:

```json
{
  "apiVersion": "grain.recipe-run/v1",
  "run_id": "research-brief-0001",
  "recipe": "research-brief",
  "recipe_apiVersion": "grain.recipe/v2",
  "params": {"topic": "GLP-1 obesity market"},
  "mode": "operator",
  "supervision": "gated",
  "status": "done",
  "cursor": "format",
  "steps": [
    {"id": "intake",     "status": "done", "artifact": "01-intake.md",  "attempts": 1},
    {"id": "gather",     "status": "done", "artifact": "02-sources.md", "attempts": 1},
    {"id": "outline",    "status": "done", "artifact": "03-outline.md", "attempts": 1},
    {"id": "draft",      "status": "done", "artifact": "04-draft.md",   "attempts": 1},
    {"id": "self_check", "status": "done", "artifact": "05-review.md",   "attempts": 1},
    {"id": "format",     "status": "done", "artifact": "brief.md",      "attempts": 1}
  ]
}
```

- Engine-stamped timestamps (`created`, `updated`, per-step `started`/`ended`) are present as written
  by the P34-T05 runner; their exact values are not asserted, only their presence + `status: done`.
- `cursor` is pinned to the committed final step `"format"` (status `done`); there is no past-final
  sentinel value.
- Each `artifact` filename in `steps[]` exists as a sibling file in the run dir and is non-empty.
- `run.json` exactly mirrors the recipe's per-step `inputs` scoping (no extra artifacts pulled in).

Done-check (`scripts`-free, inline): a verifier reads `run.json`, asserts
`apiVersion == "grain.recipe-run/v1"`, `mode == "operator"`, `supervision in {supervised,gated,autonomous}`,
`status == "done"`, `cursor == "format"`, `len(steps) == 6`, every `step.status == "done"`, and
`os.path.exists(run_dir/step.artifact)` for each step.

---

## 5. `examples/recipe-demo/README.md` (the demo-code runbook)

Venue-style runnable artifact (matches https://github.com/Jacob-Barhak/EveningOfPythonCoding example
format). Required sections:

1. **Title + one-liner** — "Grain — research-brief recipe demo (Evening of Python Coding)."
2. **Install** — `uv tool install grain-kit` (and `pip install grain-kit`) + `grain --version`.
3. **What this is** — one paragraph: a deterministic, offline, multi-step workflow; no network needed.
4. **Run it — reference run + live next (operator mode)** — two offline beats, both copy-pasteable.
   **(a) Show the committed reference run** (proves the finished structure, zero network, zero risk):
   ```
   cd examples/recipe-demo
   grain recipe show research-brief
   cat docs/recipes/runs/research-brief-0001/run.json    # status: done, cursor: format, 6 steps done
   cat docs/recipes/runs/research-brief-0001/brief.md     # the finished deliverable artifact
   ```
   **(b) Drive the live state machine** on a fresh run (narratable on stage):
   ```
   grain recipe run research-brief --param topic="GLP-1 obesity market"   # outcome: started; pauses
   grain recipe next       # renders step 1 (intake) prompt; run -> awaiting_input
   grain recipe status     # shows the cursor (intake) + per-step state
   ```
   A bare `grain recipe run` only *starts* the run (status `pending`, cursor = first step); in operator
   mode the engine never writes artifacts. A human/agent authors each step's `output`, then `grain
   recipe next` advances. The run does NOT auto-complete offline.
5. **What you'll see** — the reference run shows the finished shape: 6 ordered artifacts ending at
   `brief.md`, each step reading only its declared prior `inputs`. On the live fresh run, `grain recipe
   next` renders step 1's prompt and the run enters `awaiting_input` (operator-mode pause for the
   human/agent to author the artifact); `grain recipe status` shows the cursor. The *process* (step
   order + input scoping) is fixed and replayable; only content varies.
6. **Offline fallback** — the committed `docs/recipes/runs/research-brief-0001/` reference run is the
   always-available, zero-network proof of the finished structure: `cat brief.md` from it any time a
   live run is undesirable (mirrors the demo-script "if the live run hangs" beat). Auto mode (`grain
   recipe run --auto`) is the OPTIONAL "watch the artifacts appear" beat — it shells to an agent per
   step and writes the artifacts itself — but it is networked/risky and intentionally out of scope to
   execute here; pre-record it for the demo.
7. **Reference values** — a short table of the demo's public-facing facts: PyPI name (`grain-kit`),
   exact CLI commands (§5.4), workflow file (`docs/recipes/research-brief/recipe.yaml`), repo URL
   (`https://github.com/Diwata-Labs/Grain`). Do **not** include any path to the private
   `Diwata-Infra` presentation script — that cross-reference lives in this packet's internal note
   (task.md), not in the shipped README.
8. **Failure/resume note** — one line: a failed step keeps the cursor; `grain recipe resume` retries.

Tone constraints: open-source framing only; no "best tool", no pricing, no competitor comparison.

Done-check: `grep` finds the install line, the reference-run beat (`research-brief-0001`), the live
operator-mode commands from §5.4 (`grain recipe show` / `run` / `next` / `status`), and the "Offline
fallback" heading; the README makes no claim that a bare `grain recipe run` produces 6 artifacts or
reaches `done`; and `grep -c grain_demo_script examples/recipe-demo/README.md` equals `0` (the
private script path must not ship in the README). The cross-reference to `grain_demo_script.md` is
verified instead in this packet's internal note (task.md).

---

## 6. Out of scope (restated, for the implementer)

Auto mode execution/commit; engine source; full `workspace_kind`; per-step adapters; gate-polish;
MCP; `recipe suggest`; registry/install; branching/parallel/loops; apply/write-back; structural
validators (MVP = output-artifact existence check only). This packet does not create task packets or
touch `evaluate_workflow_state` / the review-close loop — recipes are a parallel engine.
