# Deliverable Spec: P34-T02 — RecipeRun state model + file-backed persistence

Done-definition for the run-state layer of the recipe step-runner. Grounded in
`docs/working/recipe_engine_spec.md` §2.2 (run.json), §5 (failure/resume), §8 (locked
decisions), §9 (idioms). Consumes the parsed recipe definition from P34-T01
(`apiVersion: grain.recipe/v2`); produces run state at `apiVersion: grain.recipe-run/v1`.

This packet is **state + I/O only**. No cursor engine, no execution, no CLI, no gate transitions.

---

## 1. Files created

| File | Purpose |
|------|---------|
| `src/grain/domain/recipe_run.py` | `RecipeRun`, `RecipeStepRecord`, status frozensets, dict round-trip |
| `src/grain/services/recipe_store.py` | run-dir layout, run-id allocation, atomic read/write |
| `tests/test_recipe_run.py` | domain dataclass + round-trip + validation tests |
| `tests/test_recipe_store.py` | create/load/save, run-id allocation, atomic-ordering tests |

(Test filenames indicative — match the repo's existing `tests/` naming.)

Runs are written under the **workspace** at `docs/recipes/runs/<run-id>/`. The store takes a
workspace root (or resolves it the same way sibling services do); it never writes under `tasks/`.

---

## 2. Status enums (single set, used by run and step)

```python
VALID_RUN_STATUSES: frozenset[str]  = frozenset(
    {"pending", "running", "awaiting_input", "awaiting_gate", "done", "failed"}
)
VALID_STEP_STATUSES: frozenset[str] = frozenset(
    {"pending", "running", "awaiting_input", "awaiting_gate", "done", "failed"}
)
VALID_MODES: frozenset[str] = frozenset({"operator", "auto"})
RUN_API_VERSION: str = "grain.recipe-run/v1"
```

`awaiting_input` is the operator-mode pause (spec §2.2): the prompt is rendered and the engine is
waiting for the step's `output` artifact to be written. It is a stored status only here — this
packet does not action it.

Unknown status → `ValueError` in `__post_init__`. Unknown `mode` (not in `VALID_MODES`) → raise.
`apiVersion` major mismatch on load → raise (reuse / mirror the engine's existing version-reject
helper if P34-T01 introduces one).

---

## 3. Dataclass shapes (`domain/recipe_run.py`)

Mirror `domain/workflow_loop.py`: plain `@dataclass`, `__post_init__` validation, `VALID_*`
frozensets. Use `from __future__ import annotations`. Carry the repo's SPDX header.

```python
@dataclass
class RecipeStepRecord:
    """State of one recipe step within a run, in recipe step order."""
    id: str                          # matches RecipeStep.id from the recipe def
    status: str = "pending"          # ∈ VALID_STEP_STATUSES
    artifact: str | None = None      # relative filename, e.g. "01-intake.md"; None until produced
    gate: str = "none"               # "none" | "review" (carried from def; not actioned here)
    attempts: int = 0                # incremented by the runner on each (re)run
    started: str | None = None       # ISO-8601 UTC, engine-stamped
    ended: str | None = None         # ISO-8601 UTC, engine-stamped
    error: str | None = None         # set when status == "failed"

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("step record requires non-empty id")
        if self.status not in VALID_STEP_STATUSES:
            raise ValueError(
                f"invalid step status {self.status!r}; expected one of "
                f"{sorted(VALID_STEP_STATUSES)}"
            )
        if self.attempts < 0:
            raise ValueError("attempts must be >= 0")


@dataclass
class RecipeRun:
    """File-backed state of one recipe run; single source of truth for resume."""
    run_id: str                      # "<recipe-id>-NNNN"
    recipe: str                      # recipe id
    recipe_api_version: str          # "grain.recipe/v2" (def the run was created from)
    params: dict[str, str]           # resolved run params
    mode: str                        # ∈ VALID_MODES ("operator" | "auto"); how the run is driven
    supervision: str                 # ∈ {supervised, gated, autonomous}; carried from the def
    status: str                      # ∈ VALID_RUN_STATUSES
    cursor: str                      # id of the current/next step
    steps: list[RecipeStepRecord]    # one per recipe step, in order
    api_version: str = RUN_API_VERSION
    created: str | None = None       # ISO-8601 UTC
    updated: str | None = None       # ISO-8601 UTC

    def __post_init__(self) -> None:
        if not self.run_id:
            raise ValueError("run requires non-empty run_id")
        if self.mode not in VALID_MODES:
            raise ValueError(
                f"invalid mode {self.mode!r}; expected one of {sorted(VALID_MODES)}"
            )
        if self.status not in VALID_RUN_STATUSES:
            raise ValueError(
                f"invalid run status {self.status!r}; expected one of "
                f"{sorted(VALID_RUN_STATUSES)}"
            )
        if not self.steps:
            raise ValueError("run requires at least one step record")
        ids = [s.id for s in self.steps]
        if len(ids) != len(set(ids)):
            raise ValueError("step record ids must be unique within a run")
        if self.cursor not in ids:
            raise ValueError(f"cursor {self.cursor!r} not among step ids {ids}")

    # convenience
    def step(self, step_id: str) -> RecipeStepRecord: ...   # lookup by id; KeyError-equiv if absent
```

### 3.1 Dict round-trip

`to_dict()` emits exactly the §2.2 JSON shape (note JSON uses `apiVersion` /
`recipe_apiVersion`, mapped from the snake-case fields):

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
  "created": "2026-06-26T17:00:00Z",
  "updated": "2026-06-26T17:12:00Z",
  "steps": [
    {"id": "intake",     "status": "done",          "artifact": "01-intake.md", "attempts": 1},
    {"id": "gather",     "status": "done",          "artifact": "02-sources.md", "attempts": 1},
    {"id": "outline",    "status": "done",          "artifact": "03-outline.md", "attempts": 1},
    {"id": "draft",      "status": "done",          "artifact": "04-draft.md",  "attempts": 1},
    {"id": "self_check", "status": "awaiting_gate", "artifact": "05-review.md", "attempts": 1, "gate": "review"},
    {"id": "format",     "status": "pending"}
  ]
}
```

- `from_dict(d)` reconstructs an equal `RecipeRun` (incl. step records and per-step `gate`).
  Round-trip is lossless for all set fields, including `mode`, `supervision`, and any step `gate`.
- `from_dict` rejects a payload whose `apiVersion` major ≠ 1 (`ValueError`).
- Step-record JSON omits `None`/default fields for readability (e.g. a `pending` step needs only
  `{"id": "...", "status": "pending"}`, and `gate` is emitted only when it is not the default
  `"none"` — `self_check` carries `"gate": "review"` so it survives a lossless round-trip); absent
  keys default on load.

---

## 4. Store interface (`services/recipe_store.py`)

Module-level functions (match how sibling services in `src/grain/services/` are structured — a
thin service module, not a class, unless the repo convention is a class). Signatures:

```python
RUNS_SUBDIR = "docs/recipes/runs"

def runs_root(workspace: Path) -> Path:
    """Absolute path to docs/recipes/runs/ (created on demand)."""

def run_dir(workspace: Path, run_id: str) -> Path:
    """docs/recipes/runs/<run-id>/."""

def next_run_id(workspace: Path, recipe_id: str) -> str:
    """'<recipe-id>-NNNN', zero-padded width 4, max existing for that recipe + 1
    (scan run dirs whose name starts with '<recipe-id>-'); first is '<recipe-id>-0001'."""

def create_run(
    workspace: Path,
    definition: "RecipeDefinition",     # parsed by P34-T01
    params: dict[str, str],
    mode: str = "operator",             # ∈ VALID_MODES; "auto" when started with --auto
) -> RecipeRun:
    """Allocate a run_id, build the run dir, write initial run.json:
       run status 'pending', cursor = first step id, run mode = `mode`,
       supervision = definition.supervision (parsed by P34-T01, copied verbatim),
       one pending RecipeStepRecord per definition step (carrying each step's declared gate),
       created/updated stamped now (UTC). Returns the in-memory RecipeRun."""

def load_run(workspace: Path, run_id: str) -> RecipeRun:
    """Read <run-dir>/run.json into a RecipeRun (resume = re-read). Raises if the run
       dir / run.json is missing or apiVersion major is unsupported."""

def save_run(workspace: Path, run: RecipeRun) -> None:
    """Stamp run.updated = now (UTC); atomically write run.json (temp file + os.replace)."""

def list_runs(workspace: Path) -> list[str]:
    """Run ids found under docs/recipes/runs/ (those with a run.json)."""

def write_step_artifact(
    workspace: Path,
    run: RecipeRun,
    step_id: str,
    content: str,
    artifact_name: str,
) -> None:
    """Artifact-first ordering:
         1. atomically write <run-dir>/<artifact_name> (temp + os.replace),
         2. set the step record's artifact = artifact_name,
         3. then save_run(...) (which atomically rewrites run.json).
       Never mutates any other step's artifact. The runner sets status/attempts/cursor on the
       RecipeRun before calling; this function only persists artifact + run.json."""
```

### 4.1 Atomic write protocol (the load-bearing contract)

- Every file write (artifact and `run.json`) goes to a sibling temp file in the same directory,
  is flushed, then `os.replace(tmp, target)` (atomic on POSIX). Reuse any existing atomic-write
  helper in the repo if one exists; otherwise add a small private helper in this module.
- `run.json` is written **only after** the step artifact is durably in place — so a crash between
  steps leaves a consistent, resumable `run.json` that never points at a missing artifact, and
  the prior `run.json` is never observed truncated.
- **Test mechanism:** the atomic-ordering test injects a fault by monkeypatching `os.replace` (or
  the module's temp-write helper) to raise on the `run.json` rename, then asserts the
  previously persisted `run.json` is byte-for-byte intact (parses, not truncated) and the artifact
  written first is present on disk.

---

## 5. Acceptance (objective, testable)

1. Invalid status in either dataclass raises `ValueError` (incl. constructing with valid
   `awaiting_input`); an invalid `mode` (not in `VALID_MODES`) raises; valid constructs cleanly.
2. `RecipeRun.from_dict(run.to_dict())` is lossless — including `mode`, `supervision`, and a step
   carrying `gate: "review"` — and the dict has `apiVersion == "grain.recipe-run/v1"`.
3. `create_run` writes `docs/recipes/runs/<run-id>/run.json` with run `status="pending"`, cursor
   on the first step, N pending step records (N = number of recipe steps), `params` populated,
   `recipe_apiVersion="grain.recipe/v2"`, `mode` set from the caller, `supervision` copied from
   `definition.supervision`, and each step record carrying its declared `gate`.
4. Two `create_run` calls for the same recipe → `...-0001` then `...-0002`, two distinct dirs.
5. Simulated `run.json` write failure (monkeypatched `os.replace`/temp-write raising) leaves the
   previous `run.json` intact (proves temp + `os.replace`); artifact written by
   `write_step_artifact` exists before `run.json` is updated.
6. `load_run` reconstructs a run equal to a prior `save_run`; unsupported `apiVersion` major
   raises.

---

## 6. Explicitly NOT in this deliverable
Cursor advancement / step runner; `grain recipe` CLI + JSON rendering; auto mode & agent
shelling; gate approve/reject transitions; structural output validators (existence check is the
runner's); MCP, branching/parallel/loops, `recipe suggest`, apply/write-back, full
`workspace_kind`, per-step adapters.
