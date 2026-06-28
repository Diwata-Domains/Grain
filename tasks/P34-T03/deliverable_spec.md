# Deliverable Spec — P34-T03 recipe_service (operator-mode engine)

Concrete done-definition for `src/grain/services/recipe_service.py`. Grounded in
`docs/working/recipe_engine_spec.md` §2 (data model), §3 (execution), §5 (resume), §8/§9.
Shapes from P34-T01 (`grain.recipe/v2`) and P34-T02 (`grain.recipe-run/v1`) are CONSUMED, not
redefined here; where this spec names them it states the assumed interface (confirm per the
Escalation Conditions in `task.md`).

---

## 1. Files created

- `src/grain/services/recipe_service.py` — `RecipeService` + operator-mode result dataclasses.
- `tests/services/test_recipe_service.py` — unit tests (temp workspace + fixture recipe).
- Test fixture: a minimal 2–3 step `grain.recipe/v2` recipe (one step with `gate: review`)
  scaffolded under the test's temp `docs/recipes/<id>/`. Do NOT depend on the bundled
  `research-brief` recipe (that data ships in T06); tests own their fixture. No production source
  created outside `recipe_service.py`.

Run artifacts produced at runtime (NOT committed by this task): `docs/recipes/runs/<run-id>/run.json`
plus per-step output artifacts named by each step's `output:` key.

---

## 2. Consumed interfaces (from P34-T01 / P34-T02)

Assumed shapes; treat as the contract this service is written against.

**P34-T01 — definition (`src/grain/domain/recipe.py`)**
- `RecipeDefinition` with: `api_version: str` (`"grain.recipe/v2"`), `id`, `name`, `params:
  list[RecipeParam]`, `steps: list[RecipeStep]`, `final: str`, optional `supervision`,
  `workspace_kind`.
- `RecipeStep` with: `id`, `name`, `prompt` (path under recipe dir, or `inline:` text),
  `inputs: list[str]`, `output: str`, `gate: str` (`"none" | "review"`, default `"none"`).
- `RecipeParam` with: `id`, `required: bool`, `type: str`.
- Loader entry point, e.g. `load_recipe(recipe_dir: Path) -> RecipeDefinition`, rejecting unknown
  apiVersion majors and unknown keys.

**P34-T02 — run state (`src/grain/domain/recipe_run.py`)**
- `RecipeRun` (mirrors `run.json` §2.2): `api_version` (`"grain.recipe-run/v1"`), `run_id`,
  `recipe`, `recipe_api_version`, `params: dict[str, str]`, `mode` (`"operator" | "auto"`),
  `supervision`, `status`, `cursor`, `steps: list[RecipeStepRecord]`, timestamps (`created`,
  `updated`). Per-step `gate` is persisted on `RecipeStepRecord` when the recipe declares one.
- `RecipeStepRecord`: `id`, `status`, `artifact: str | None`, `attempts: int`, `gate: str`,
  `started`, `ended`.
- I/O: `write_run(run_dir, run)` (atomic), `read_run(run_dir) -> RecipeRun`, and the **run-id
  allocation helper** — the single owner of `<recipe-id>-<NNNN>` allocation; this service CALLS it
  and never reimplements the directory scan. **Atomic-write ordering (artifact-then-run.json) is
  enforced by these primitives;** this service must call them in that order and never persist
  `run.json` ahead of an artifact landing.

If any of the above differs, follow `task.md` Escalation Conditions before coding.

---

## 3. Status vocabularies (VALID_* frozensets)

Defined or re-exported in this module, mirroring `domain/workflow_loop.py`:

```python
VALID_RUN_STATUS:  frozenset[str] = frozenset({"pending", "running", "awaiting_input", "awaiting_gate", "done", "failed"})
VALID_STEP_STATUS: frozenset[str] = frozenset({"pending", "running", "awaiting_input", "awaiting_gate", "done", "failed"})
VALID_GATE_KINDS:  frozenset[str] = frozenset({"none", "review"})
VALID_MODES:       frozenset[str] = frozenset({"operator", "auto"})
RECIPE_RUN_API_VERSION: str = "grain.recipe-run/v1"
RECIPE_API_VERSION: str = "grain.recipe/v2"
RUNS_DIR = "docs/recipes/runs"
RECIPES_DIR = "docs/recipes"
```

`mode` (`operator | auto`) is DISTINCT from `supervision` (`supervised | gated | autonomous`):
`mode` is set at run time (this packet writes `operator`); `supervision` is parsed into
`RecipeDefinition` and copied verbatim into `run.json`. Never cross-store the two vocabularies.
`status: failed` is unreachable in operator mode — a missing output is `awaiting_input`, not a
failure (`recipe_engine_spec.md` §5); `failed` is reserved for the auto-mode runner (T05).

(If P34-T01/T02 already export these, import rather than duplicate.)

---

## 4. Result dataclasses (operator-mode return shapes)

All `@dataclass` with `__post_init__` validation; pure data, no I/O.

```python
@dataclass
class ScopedInput:
    """One declared input surfaced to the step."""
    kind: str            # "params" | "artifact"
    id: str              # "params" or the prior step id
    path: str            # absolute path ("" for params)
    content: str         # rendered/loaded content (params -> formatted k=v block)

@dataclass
class RecipeSummary:
    """One enumerated recipe (for list_recipes / the T04 CLI `list`)."""
    id: str
    name: str
    source: str          # "bundled" | "workspace"
    category: str = ""
    description: str = ""

@dataclass
class NextResult:
    """Outcome of one RecipeService.next() / resume() call."""
    run_id: str
    outcome: str         # see VALID_NEXT_OUTCOMES below
    cursor: str | None   # step id the run now rests on (None when run done)
    step_id: str | None
    run_status: str      # in VALID_RUN_STATUS
    prompt: str = ""             # rendered prompt text, when outcome == "prompt_ready"
    output_path: str = ""        # absolute path the artifact must be written to
    inputs: list[ScopedInput] = field(default_factory=list)
    gate: str = "none"           # in VALID_GATE_KINDS; "review" when awaiting_gate
    message: str = ""

VALID_NEXT_OUTCOMES: frozenset[str] = frozenset({
    "started",          # start_run created the run; status=pending, cursor=first step, no advance
    "prompt_ready",     # step unfulfilled; prompt + output_path surfaced; run/step=awaiting_input
    "advanced",         # cursor step's artifact existed; marked done, cursor moved
    "awaiting_gate",    # step done but gate:review reached; run paused
    "run_complete",     # final step done; run status done
    "noop",             # called on an already-paused run (e.g. awaiting_gate); no write
})
```

This set is exactly `recipe_engine_spec.md` §3.1's outcome vocabulary
`{started | prompt_ready | advanced | awaiting_gate | run_complete | noop}`. `awaiting_input` is a
run/step *status*, NOT an outcome: in operator mode the unfulfilled-step pause is returned as
`outcome == "prompt_ready"` carrying `run_status == "awaiting_input"` (the `awaiting_input` string
appears only in `VALID_RUN_STATUS` / `VALID_STEP_STATUS`, never in `VALID_NEXT_OUTCOMES`).
`noop` replaces the old `noop_gate` and is what `next()` returns on an already-`awaiting_gate` run.

`__post_init__` enforces: `outcome in VALID_NEXT_OUTCOMES`; `run_status in VALID_RUN_STATUS`;
`gate in VALID_GATE_KINDS`; when `outcome == "prompt_ready"`, both `prompt` and `output_path`
are non-empty and `run_status == "awaiting_input"`.

---

## 5. RecipeService API

```python
class RecipeService:
    def __init__(self, workspace_root: Path, bundled_recipes_root: Path | None = None) -> None: ...

    def resolve(self, recipe_id: str) -> RecipeDefinition:
        """Find recipe_id under <workspace>/docs/recipes/<id>/ first, then bundled recipes;
        parse via P34-T01 loader. Raises RecipeNotFoundError if absent."""

    def list_recipes(self) -> list[RecipeSummary]:
        """Enumerate bundled + workspace recipes (this packet owns enumeration; the CLI `list`
        in T04 consumes this). Returns id + summary metadata; T06 ships the bundled
        `research-brief` recipe as DATA only."""

    def start_run(self, recipe_id: str, params: dict[str, str], *, mode: str = "operator") -> NextResult:
        """Validate required params against the definition; allocate <recipe-id>-<NNNN> via the
        P34-T02 run-id allocation helper (single owner; do NOT reimplement the scan); create
        docs/recipes/runs/<run-id>/; write initial run.json (all steps pending, cursor=first step,
        status=pending, mode=<mode>, supervision copied from the parsed definition). Does NOT
        auto-advance: returns NextResult(outcome="started", run_status="pending", cursor=<first
        step id>). Raises MissingParamError and writes no run dir on failure."""

    def next(self, run_id: str) -> NextResult:
        """Advance the run by exactly one step (operator semantics in §6). Re-reads run.json.
        Raises RunNotFoundError for an unknown run_id."""

    def resume(self, run_id: str) -> NextResult:
        """Re-read run.json and continue next() semantics from the persisted cursor, in the run's
        recorded `mode`. No in-memory state carried across calls. In operator mode there is no
        `failed` state to recover from — resume simply re-surfaces (awaiting_input) or advances the
        cursor step. Raises RunNotFoundError for an unknown run_id."""
```

Typed errors (module-level exceptions): `RecipeNotFoundError` (unknown recipe id),
`RunNotFoundError` (unknown run id), `MissingParamError`, `InputNotReadyError` (a *declared*
input references a not-yet-done prior step), `UndeclaredInputError` (a `{{steps.<id>}}` references
a step that is `done` but NOT in the cursor step's `inputs:` — out of scope), `UnknownTokenError`
(`{{...}}` token unresolved by either rule). There is no `GateBlockedError` in this packet:
`next()` on a paused run returns `outcome="noop"` rather than raising, and gate approve/reject is
owned by the T05 runner.

---

## 6. next() operator-mode algorithm (the state machine)

Given `run = read_run(run_dir)` (raise `RunNotFoundError` if the run dir / `run.json` is absent):

1. If `run.status == "awaiting_gate"` → return `NextResult(outcome="noop", gate="review",
   cursor=run.cursor, run_status="awaiting_gate", message="awaiting gate approval")`. (No write.)
2. If `run.status == "done"` → return `outcome="run_complete"`, `cursor=None`. (No write.)
3. Locate `step = step at run.cursor`; `output_path = run_dir / step.output`.
4. **If `output_path` exists** (completion = existence check, §8.5):
   a. Set step `status="done"`, stamp `ended`, set `artifact=step.output`.
   b. If `step.gate == "review"` → set step and run `status="awaiting_gate"`, cursor unchanged;
      `write_run`; return `outcome="awaiting_gate"`, `gate="review"`.
   c. Else advance cursor to the next step. If none remain → set run `status="done"`, `write_run`,
      return `outcome="run_complete"`, `cursor=None`. Otherwise set run `status="running"`,
      `write_run`, return `outcome="advanced"`, `cursor=<next step id>`.
5. **If `output_path` does NOT exist** (operator-mode pause — NOT a failure):
   a. Assemble scoped inputs (§7) for `step.inputs`.
   b. Render `step.prompt` (load path under recipe dir, or use `inline:` text) with `{{param}}` /
      `{{steps.<id>}}` substitution (§8).
   c. Set step and run `status="awaiting_input"` (increment `attempts` on first transition into the
      pause for this step; re-invocation before the artifact lands does NOT double-increment —
      guard on prior status); `write_run`.
   d. Return `outcome="prompt_ready"`, `run_status="awaiting_input"`, `prompt=<rendered>`,
      `output_path=<abs path>`, `inputs=<ScopedInput list>`, `cursor=step.id`.

`status: failed` is never set by this engine — it is reserved for the auto-mode runner (T05).
Idempotency: steps 5a–5d are repeatable; re-calling `next()` before the artifact exists
re-surfaces the same `prompt_ready` / `awaiting_input` result without advancing.

`start_run` (separate from the loop above): after writing the initial `run.json`, return
`NextResult(outcome="started", run_status="pending", cursor=<first step id>)` — no auto-advance.

---

## 7. Scoped declared-input assembly

For `step.inputs` (a list of ids), produce `list[ScopedInput]`:
- `"params"` → one `ScopedInput(kind="params", id="params", path="", content=<formatted
  key=value block of run.params>)`.
- any other id `X` → the prior step with id `X`:
  - if that step's record is not `status == "done"` → raise `InputNotReadyError`.
  - else `ScopedInput(kind="artifact", id="X", path=<abs path to its artifact>,
    content=<read artifact file>)`.
- **No auto-include**: ids NOT in `step.inputs` are never assembled (§1.7, §8.3). A step's own
  `output` is never an input. Asserted by the "does not surface gather" acceptance criterion.

---

## 8. Substitution (minimal, no control flow)

Operates on prompt text only. Two token forms:
- `{{<param-id>}}` → `run.params[<param-id>]`.
- `{{steps.<step-id>}}` → content of that prior step's artifact. The step must be BOTH declared in
  the cursor step's `inputs:` AND `status == "done"` (reuse the §7 resolution):
  - declared-but-not-`done` → raise `InputNotReadyError`;
  - `done` but NOT declared in `inputs:` (out of scope) → raise `UndeclaredInputError` (distinct).
- Any remaining unresolved `{{...}}` token (neither a known param nor a valid `steps.<id>`) → raise
  `UnknownTokenError` (fail loud, no silent passthrough).
- No conditionals, loops, filters, or expressions. Reuse Grain's existing minimal templating
  approach (consistent with `prompt.md` rendering) rather than a new template engine.

---

## 9. run.json shape produced (grain.recipe-run/v1)

Initial state written by `start_run` (example, 3-step fixture with a gate on step 2):

```json
{
  "apiVersion": "grain.recipe-run/v1",
  "run_id": "demo-0001",
  "recipe": "demo",
  "recipe_apiVersion": "grain.recipe/v2",
  "params": {"topic": "X"},
  "mode": "operator",
  "supervision": "gated",
  "status": "pending",
  "cursor": "intake",
  "created": "<iso8601>",
  "updated": "<iso8601>",
  "steps": [
    {"id": "intake",  "status": "pending"},
    {"id": "review",  "status": "pending"},
    {"id": "format",  "status": "pending"}
  ]
}
```

Before `intake` is fulfilled, `next()` sets `intake.status="awaiting_input"` and run
`status="awaiting_input"` (the operator pause). After fulfilling `intake` and one `next()`:
`intake.status="done"`, `intake.artifact` set, `intake.attempts=1`, `cursor="review"`, run
`status="running"`. After fulfilling `review` (`gate: review`) and one `next()`:
`review.status="awaiting_gate"`, run `status="awaiting_gate"`, `cursor="review"` (unchanged).
(Field names match §2.2 of the spec, including `mode`; serialization is owned by P34-T02.)

---

## 10. Test matrix (`tests/services/test_recipe_service.py`)

1. `start_run` happy path → `outcome=="started"`, no auto-advance; run dir + initial `run.json`
   asserted (apiVersion, all pending, cursor=first, status=pending, `mode=="operator"`,
   `supervision` copied from the definition).
2. `start_run` missing required param → `MissingParamError`, no run dir created.
3. `resolve("nope")` → `RecipeNotFoundError`; `next("no-such-run")` and `resume("no-such-run")`
   → `RunNotFoundError`.
4. `next` with no artifact → `prompt_ready` with run/step `status=="awaiting_input"` (NOT failed);
   substituted prompt (assert a `{{param}}` value appears, no literal `{{` remains); `output_path`
   absolute; `inputs` contains only declared ids.
5. Scoping negative: step declaring `inputs:[params, intake]` does NOT surface a later/sibling
   step's artifact.
6. Out-of-scope substitution: a `{{steps.<id>}}` referencing a `done` step NOT in `inputs:` →
   `UndeclaredInputError` (distinct from `InputNotReadyError` for a declared-but-not-done input).
7. Fulfil artifact → `next` → `advanced`; `run.json` shows step `done` + cursor moved.
8. Gate: fulfil a `gate: review` step → `next` → `awaiting_gate`, cursor unchanged; second `next`
   → `noop` (no `GateBlockedError` raised).
9. Final step fulfilled → `next` → `run_complete`, run `status="done"`, `cursor=None`.
10. Resume: drive a run partway, discard the `RecipeService`, build a fresh one, `resume(run_id)`
    reproduces the next expected `NextResult` from the persisted cursor in the recorded `mode`.
11. Idempotency: two consecutive `next()` calls before the artifact lands return the same
    `prompt_ready` / `awaiting_input` result and do not advance cursor or double-increment `attempts`.
12. Offline/decoupling: runs with no network/API key; grep test asserts the module references no
    `evaluate_workflow_state` and no task-packet/review/close service.

---

## 11. Done = all true
- `recipe_service.py` (the single canonical service-module name) exists, imports cleanly, exposes
  `RecipeService.resolve/list_recipes/start_run/next/resume` and the result dataclasses above.
- All acceptance criteria in `task.md` pass via `tests/services/test_recipe_service.py`.
- No auto-mode, CLI, MCP, scaffold, branching, adapter, or structural-validation code present.
- No import of `evaluate_workflow_state` or any SDLC packet/review/close service.
