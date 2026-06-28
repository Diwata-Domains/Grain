# Deliverable Spec — P34-T05: CLI `grain recipe run / next / status / resume / gate`

Concrete done-definition for the operator-mode recipe-run CLI. Grounded in
`docs/working/recipe_engine_spec.md` §2 (data model), §3 (execution), §4 (CLI surface).
All shapes use `grain.recipe/v2` for definitions and `grain.recipe-run/v1` for run state.

This packet adds CLI verbs ONLY. Parsing, run state I/O, and step advancement belong to
P34-T03 (domain + service); P34-T04 creates the `recipe` CLI group; the CLI calls them and formats output.

---

## 1. Assumed upstream interfaces (from P34-T03 / P34-T04)

The CLI depends on these. If actual signatures differ, escalate (see task.md).

### Domain (P34-T03) — `src/grain/domain/recipe.py`
Dataclasses with `__post_init__` validation and `VALID_*` frozensets, mirroring
`domain/workflow_loop.py`:

```python
VALID_RUN_STATUS: frozenset[str]  = frozenset({"pending","running","awaiting_input","awaiting_gate","done","failed"})
VALID_STEP_STATUS: frozenset[str] = frozenset({"pending","running","awaiting_input","awaiting_gate","done","failed"})
VALID_GATE_KINDS: frozenset[str]  = frozenset({"none","review"})
VALID_MODES: frozenset[str]       = frozenset({"operator","auto"})
VALID_SUPERVISION: frozenset[str] = frozenset({"supervised","gated","autonomous"})

@dataclass
class RecipeStep:        # id, name, prompt, inputs: list[str], output, gate="none"
@dataclass
class RecipeDefinition:  # apiVersion, id, name, params, steps: list[RecipeStep], final, supervision
@dataclass
class RecipeStepRecord:  # id, status, artifact="", attempts=0, gate="none", started="", ended="", error=""
@dataclass
class RecipeRun:         # apiVersion, run_id, recipe, recipe_apiVersion, params, mode, supervision,
                         # status, cursor, steps: list[RecipeStepRecord], created, updated
```

`mode` (`operator | auto`) is DISTINCT from `supervision` (`supervised | gated | autonomous`):
`mode` records how the run is driven (set at `run` time; `--auto` ⇒ `auto`, default ⇒ `operator`),
`supervision` is parsed from the recipe and governs where the run pauses. Never store an
operator/auto value as supervision (or vice-versa).

### Service (P34-T03) — `src/grain/services/recipe_service.py`
The CLI treats the service as the only source of truth (no direct file parsing in CLI):

```python
def start_run(root, recipe_id: str, params: dict[str, str], *, mode: str = "operator") -> RecipeRun
def advance_run(root, run_id: str, *, single_step: bool) -> RecipeRun   # next=True, run=False
def load_run(root, run_id: str | None) -> RecipeRun                     # None => sole open run
def resume_run(root, run_id: str) -> RecipeRun
def gate_decision(root, run_id: str | None, decision: str) -> RecipeRun # decision in {"approve","reject"}
def list_open_runs(root) -> list[str]                                   # for ambiguity check
def run_to_dict(run: RecipeRun) -> dict                                 # json serialization
```

`run_to_dict` MUST round-trip `mode`, `supervision`, and the `created`/`updated` timestamps (so
`--format json` exposes them and a re-loaded run preserves them). `start_run` returns the run in
`status: pending` with `cursor` on the first step (the `started` engine outcome) and does NOT
auto-advance; the `run` verb calls `advance_run` separately.

If the service does not already raise on ambiguous open runs, the CLI enforces it via
`list_open_runs(root)` before resolving an implicit run.

---

## 2. CLI signatures (Click, registered on existing `recipe` group)

`fmt = ctx.obj.get("fmt", "text")` and `repo = ctx.obj.get("repo")`; `root = resolve_repo_root(repo)`
— identical to `cli/workflow.py`.

```
grain recipe run <recipe_id> [--param/-p k=v ...] [--run <run-id>]
grain recipe next [--run <run-id>]
grain recipe status [--run <run-id>]
grain recipe resume <id_or_run_id>
grain recipe gate <approve|reject> [--run <run-id>]
```

- `--param/-p` is repeatable; each value is `key=value`. Malformed pairs → `UsageError`.
- `--run` is the run-id selector; required only when >1 open run exists.
- `gate` takes a positional `decision` constrained to `{"approve","reject"}` (Click `Choice`).
- Global `--format json` is read from `ctx.obj` (set by the root group), NOT a per-verb flag.

### Verb semantics
| verb | calls | operator-mode behavior |
|------|-------|------------------------|
| `run` | `start_run(mode="operator")` then `advance_run(single_step=False)` | start a run; advance cursor until `awaiting_input` (first un-authored step), `awaiting_gate`, or `run_complete` (`done`). A fresh run pauses at `awaiting_input` — it does NOT reach `done` by itself. No network. |
| `next` | `advance_run(single_step=True)` | advance EXACTLY one step when the current step's `output` exists (cursor moves to the next step; the `steps` array length is unchanged); otherwise re-surface the prompt with the step in `awaiting_input`. Existence check only. |
| `status` | `load_run` | report current run state; no mutation. |
| `resume` | `resume_run` | re-enter a `failed`/paused run from `cursor` in the recorded `mode`; RE-RUNS the cursor step and increments its `attempts`. On an `awaiting_gate` run it does NOT pass the gate (stays `awaiting_gate`). |
| `gate` | `gate_decision` | `approve` → advance PAST the gated step (cursor moves on; the step is not re-run); `reject` → leave run stopped at the gate (`awaiting_gate`). |

---

## 3. Output shapes

### Text (human)
`run` / `next` / `resume` / `gate`:
```
recipe run: <status>
  run_id   research-brief-0001
  recipe   research-brief
  cursor   self_check
  steps    intake=done gather=done outline=done draft=done self_check=awaiting_gate format=pending
```
`status` additionally lists per-step `artifact` paths. Gate-paused runs print the path of the
artifact awaiting review and the `grain recipe gate approve` hint.

### JSON (`grain --format json recipe ...`)
Emitted via the shared output helper; the run payload is `run_to_dict(run)`, matching the
`grain.recipe-run/v1` shape in spec §2.2:
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
  "created": "2026-06-26T14:00:00Z",
  "updated": "2026-06-26T14:05:00Z",
  "steps": [
    {"id": "intake", "status": "done", "artifact": "01-intake.md", "attempts": 1},
    {"id": "self_check", "status": "awaiting_gate", "artifact": "05-review.md", "attempts": 1, "gate": "review"},
    {"id": "format", "status": "pending"}
  ]
}
```
JSON must always include `run_id`, `mode`, `supervision`, `status`, `cursor`, `created`, `updated`,
and the `steps` array (each with `id`, `status`, and — when produced — `artifact`/`attempts`, plus
`gate` when the step declares one). On error, a non-zero exit with a `{"error": "..."}`-shaped JSON
payload, consistent with other CLI verbs.

---

## 4. Files created / modified

| path | change |
|------|--------|
| `src/grain/cli/recipe.py` | extend the existing `recipe` Click group with `run`, `next`, `status`, `resume`, `gate` subcommands (this packet). |
| `tests/cli/test_recipe_run_cli.py` (or repo's test layout) | `CliRunner` tests for all verbs + JSON shapes + ambiguity error. |

Runtime artifacts (written by the service, asserted by tests, NOT created by CLI code):
`docs/recipes/runs/<run-id>/run.json` and step output artifacts (`01-intake.md` … `final`).

The CLI writes nothing outside what the service produces, and never creates task packets or
touches `docs/runtime/` SDLC state.

---

## 5. Done when

1. All five verbs registered on the `recipe` group (created/registered in P34-T04) and invokable
   via `CliRunner`.
2. Operator `run` on a no-gate recipe (test fixture / pre-staged workspace) records `mode: operator`
   and pauses at `status: awaiting_input` on the first step; interleaving artifact authoring with
   `next` then drives the run to `status: done` with `final` written — offline, no API key.
3. A `gate: review` recipe halts at `awaiting_gate`; `gate approve` advances PAST the gate (step not
   re-run), `gate reject` stops, and `resume` does NOT pass the gate.
4. `next` advances exactly one step per call: the `cursor` moves to the next step id (done-count +1)
   while the `steps` array length is unchanged.
5. `--format json` on every verb yields `json.loads`-able output with the §3 keys (including `mode`,
   `created`, `updated`).
6. Ambiguous open runs without `--run` raise `UsageError` (non-zero exit) on `run`/`next`/`status`/`gate`.
7. `resume` on a `failed` run re-enters from cursor and increments `attempts`, never mutating a
   prior step's artifact.
8. CLI contains no recipe parsing or run-state file I/O — all delegated to the P34-T03 service.
