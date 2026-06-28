# Deliverable Spec — P34-T09: (stretch) Auto-mode step execution

Concrete done-definition for the **auto (live, networked) execution mode** of the recipe
step-runner. Grounded in `docs/working/recipe_engine_spec.md` §3 (execution model), §5
(failure & resume), §7 (MVP vs deferred — auto is optional/pre-recorded), and §9 (reuse
`WorkflowLoopAgentConfig`). Definitions are `grain.recipe/v2`; run state is
`grain.recipe-run/v1`.

**STRETCH — not on the July 21 critical path.** Operator mode (P34-T03/T05) is the demo.
This packet layers auto mode on top of it; it must not change operator-mode behavior.

This packet extends the existing service and the existing `recipe run` verb ONLY. The
operator-mode state machine (P34-T03) and the CLI verbs (P34-T05) already exist; this packet
reuses them and adds the agent-execution path + `--auto`.

---

## 1. Assumed upstream interfaces (from P34-T03 / P34-T05)

If actual signatures differ, escalate (see task.md).

### Operator-mode service (P34-T03) — `src/grain/services/recipe_service.py`
Auto mode reuses the operator state machine. It must NOT reimplement render / completion /
gate / cursor / persist logic. Assumed reusable seams:

```python
class RecipeService:
    def resolve(self, recipe_id: str) -> RecipeDefinition: ...
    def start_run(self, recipe_id: str, params: dict[str, str]) -> RecipeRun: ...
    def next(self, run_id: str) -> StepResult: ...      # operator: render + surface prompt
    def resume(self, run_id: str) -> StepResult: ...
    # StepResult exposes (at least): the cursor step, its rendered prompt text,
    # the absolute output-artifact path, the scoped declared-input paths,
    # and a flag for "prompt ready" vs "step completed/advanced" vs "awaiting_gate".
```

### Agent config (existing) — `src/grain/domain/workflow_loop.py`
Reused as-is; do NOT redefine:

```python
VALID_SUPERVISION_LEVELS = frozenset({"supervised", "gated", "autonomous"})
VALID_AGENT_SHORTCUTS    = frozenset({"claude", "codex"})

@dataclass
class WorkflowLoopAgentConfig:
    mode: str            # "shortcut" | "command"
    shortcut: str = ""   # "claude" | "codex"  (when mode == "shortcut")
    model: str = ""      # optional model bias
    command: str = ""    # raw invocation       (when mode == "command")
    # __post_init__ validates mode/shortcut/command exclusivity
```

### CLI (P34-T05) — `src/grain/cli/recipe.py`
The `recipe` Click group and `run` verb exist. This packet adds the `--auto` flag to `run`.

---

## 2. New / extended interfaces (this packet)

All new helpers are dataclasses with `__post_init__` validation and reuse the existing
`VALID_*` frozensets — no new status vocabulary.

### 2.1 Agent resolution helper — in `recipe_service.py`

```python
def resolve_recipe_agent(
    root: Path,
    *,
    step_model: str = "",        # per-step recipe.yaml `model:` (spec §2.1), overrides config model
) -> WorkflowLoopAgentConfig:
    """Load the agent config (reuse docs/runtime/workflow_loop.yaml shape) and return a
    validated WorkflowLoopAgentConfig. step_model, when set, biases the model passed to the
    agent. Raises (typed) on an invalid/missing config BEFORE any step runs."""
```

### 2.2 Auto-mode advance — in `RecipeService`

```python
@dataclass
class AutoStepOutcome:
    step_id: str
    status: str                  # in VALID_STEP_STATUS: "done" | "awaiting_gate" | "failed"
    artifact: str = ""           # relative artifact name when produced
    attempts: int = 0
    error: str = ""              # captured stderr/summary on failure
    # __post_init__: status must be in VALID_STEP_STATUS

def run_auto(
    self,
    run_id: str,
    *,
    agent: WorkflowLoopAgentConfig,
    timeout_s: int = ...,        # bounded; default sane value
) -> RecipeRun:
    """Advance the run by executing each cursor step via the configured agent until the run
    is `done`, hits a gate (`awaiting_gate`), or `failed`. Per step:
      1. render the cursor step's scoped prompt (reuse operator-mode render).
      2. shell to the agent (subprocess, no shell injection, cwd=root, bounded timeout),
         delivering the prompt and expecting the step's declared `output` artifact to be
         written at its absolute path.
      3. completion = output-artifact **existence check only** (locked, spec §8.5; no
         non-empty or structural validation — a present-but-empty artifact counts as produced).
         - exists -> reuse operator advance/gate logic (cursor advance, or enter
           `awaiting_gate` on `gate: review` / `gated`/`supervised` supervision — supervised is
           treated as gated-equivalent for this MVP, see §3 note below).
         - missing, non-zero exit, or timeout -> step+run `status: failed`, record
           error + increment `attempts`, leave cursor on the failed step.
      4. persist run.json ONLY after the artifact lands (no partial-corruption window).
    Never advances past a gate; never mutates a prior step's artifact."""
```

Auto mode is selected when supervision is `autonomous` OR the CLI passes `--auto`; otherwise
the service stays on the operator path.

### 2.3 Subprocess contract
- Invoke via `subprocess.run([...], cwd=root, capture_output=True, text=True, timeout=timeout_s)`
  — argument list (no `shell=True`) for `command` mode; shortcut mode maps `claude`/`codex` to
  their argv with `--model <model>` appended when a model is set.
- The rendered step prompt is delivered to the agent (via stdin or a temp prompt file under the
  run dir — pick one and document it); the agent is expected to write the step's `output`
  artifact at the absolute path the operator-mode render already computes.
- On `TimeoutExpired` or non-zero return code: capture stdout+stderr (truncated) into the step
  `error` field; mark `failed`.

---

## 3. CLI change (extend P34-T05 `run`)

```
grain recipe run <recipe_id> [--param/-p k=v ...] [--run <run-id>] [--auto]
```

| flag | behavior |
|------|----------|
| (none) | operator mode (default): start + advance to completion or first gate WITHOUT invoking an agent (unchanged from P34-T05). |
| `--auto` | resolve the agent (`resolve_recipe_agent`) and drive the run via `run_auto`. |
| supervision `autonomous` | implies `--auto` even if the flag is omitted. |

**Supervision (MVP):** `autonomous` runs straight through non-gated steps; `gated` pauses at
`gate: review` steps. **`supervised` is treated as gated-equivalent for this MVP** (pauses at a
gate, not after every step) — full supervised-mode pause-after-every-step polish is deferred per
spec §7. Both `gated` and `supervised` resolve to the same `awaiting_gate` path here.

`--format json` continues to emit `run_to_dict(run)` (the `grain.recipe-run/v1` shape, spec
§2.2); auto mode adds no new run-payload keys beyond the existing per-step `error`/`attempts`.
On agent failure the verb exits non-zero with the run left at `status: failed` and (for json)
an `{"error": "..."}`-consistent payload.

---

## 4. JSON / run.json shape (unchanged contract)

Auto mode writes the same `grain.recipe-run/v1` run.json as operator mode; a failed step
populates the existing per-step `error` and bumps `attempts`:

```json
{
  "apiVersion": "grain.recipe-run/v1",
  "run_id": "research-brief-0002",
  "recipe": "research-brief",
  "recipe_apiVersion": "grain.recipe/v2",
  "params": {"topic": "GLP-1 obesity market"},
  "mode": "auto",
  "supervision": "autonomous",
  "status": "failed",
  "cursor": "gather",
  "steps": [
    {"id": "intake", "status": "done", "artifact": "01-intake.md", "attempts": 1},
    {"id": "gather", "status": "failed", "attempts": 1,
     "error": "agent exited 1: <captured stderr>"},
    {"id": "outline", "status": "pending"}
  ]
}
```

No new top-level keys are introduced by auto mode.

---

## 5. Files created / modified

| path | change |
|------|--------|
| `src/grain/services/recipe_service.py` | EXTEND: add `resolve_recipe_agent`, `AutoStepOutcome`, and `RecipeService.run_auto` (the auto path); reuse operator render/advance/gate/persist. |
| `src/grain/cli/recipe.py` | EXTEND: add `--auto` to the existing `run` verb; wire to `run_auto`. |
| `tests/services/test_recipe_service.py` | EXTEND: auto-mode unit tests with a FAKE agent command. |
| `tests/cli/test_recipe_run_cli.py` | EXTEND: `--auto` CliRunner tests (success, gate halt, failure→resume, opt-in guard). |

Runtime artifacts (written by the agent/service, asserted by tests, not by new code paths
beyond the service): `docs/recipes/runs/<run-id>/run.json` and step outputs.

The test "agent" is a local script/command that writes (or fails to write) the step's output
artifact — NEVER a real network/API call. No API key is required to run the test suite.

---

## 6. Done when

1. `run_auto` drives a no-gate recipe to `status: done` using a fake agent command, offline,
   writing every step artifact + `final` — asserted via `run.json` and files.
2. `--auto` is opt-in: a default (non-`autonomous`) `grain recipe run` takes the operator path
   and invokes NO agent subprocess (test fails if the fake agent is called).
3. A `gate: review` step (or `gated`/`supervised` supervision) halts an `--auto` run at
   `awaiting_gate` with the cursor on the gated step; the agent is not run past it.
4. A failing fake agent (non-zero exit OR missing output — completion is the existence check
   only, so a present-but-empty artifact is NOT a failure) → step+run `status: failed`,
   error recorded, cursor on the failed step; `grain recipe resume` re-enters and bumps
   `attempts`, never mutating a prior artifact.
5. `resolve_recipe_agent` returns a validated `WorkflowLoopAgentConfig` (shortcut `claude|codex`
   or `command`, optional `model`, per-step `model:` honored) and raises on an invalid config
   before any step runs.
6. Auto mode reuses the operator-mode render/advance/gate/persist logic (no duplicated state
   machine), and `recipe_service.py` references neither `evaluate_workflow_state` nor any
   task-packet/review/close service (test + grep).
7. Operator-mode behavior (P34-T03/T05) is unchanged — existing operator tests still pass.
