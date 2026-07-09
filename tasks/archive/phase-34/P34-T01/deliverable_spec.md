# Deliverable Spec: P34-T01 — Recipe definition model + v2 schema parser

## Required Output

### New Files
- `tasks/P34-T01/task.md` — packet metadata/scope ✓
- `tasks/P34-T01/deliverable_spec.md` — this file ✓
- `src/grain/domain/recipe.py` — definition dataclasses + parser/validator
- `tests/test_recipe_model.py` — tests (≥ 8)

### Modified Files
- none (definition layer only; CLI registration and run state are later P34 packets)

## Module contract: `src/grain/domain/recipe.py`

### Constants / errors
```python
RECIPE_API_VERSION = "grain.recipe/v2"   # the only accepted apiVersion

VALID_GATES: frozenset[str] = frozenset({"none", "review"})
VALID_CATEGORIES: frozenset[str] = frozenset(
    {"research", "docs", "data", "ops", "content", "code", "custom"}
)
VALID_SUPERVISION: frozenset[str] = frozenset(
    {"supervised", "gated", "autonomous"}
)

class RecipeSchemaError(ValueError):
    """Raised when a recipe.yaml violates the grain.recipe/v2 schema."""
```

### Dataclasses (mirror `workflow_loop.py`: `@dataclass` + `__post_init__`)

```python
@dataclass
class RecipeParam:
    id: str
    required: bool = False
    label: str = ""
    type: str = "string"          # MVP: not enumerated/validated beyond non-empty

@dataclass
class RecipeStep:
    id: str
    prompt: str                   # path (e.g. "steps/intake.md") or "inline:..." string
    output: str                   # artifact filename this step must produce
    inputs: list[str] = field(default_factory=list)   # "params" or earlier step ids
    name: str = ""
    gate: str = "none"            # one of VALID_GATES

    def __post_init__(self) -> None:
        # id, prompt, output non-empty; gate in VALID_GATES else RecipeSchemaError

@dataclass
class RecipeDefinition:
    id: str
    name: str
    final: str                    # must equal some step.output
    params: list[RecipeParam] = field(default_factory=list)
    steps: list[RecipeStep] = field(default_factory=list)
    supervision: str = "gated"     # one of VALID_SUPERVISION; default per spec §2.1
    description: str = ""          # retained v1 metadata, optional
    category: str = ""             # if set, must be in VALID_CATEGORIES

    def __post_init__(self) -> None:
        # id/name non-empty; >=1 step; unique step ids; category check;
        # supervision in VALID_SUPERVISION; inputs reference validation;
        # final-resolves-to-an-output check
```

### Validation rules (each violation raises `RecipeSchemaError` with a naming message)

1. **apiVersion gate.** Input dict must have `apiVersion`. Accept it **only** when it is
   exactly the string `"grain.recipe/v2"` (equality against `RECIPE_API_VERSION`). Any
   other value — including `grain.recipe/v1`, `grain.recipe/v3`, a major-only match, a
   malformed string, or missing — raises, and the error message names the offending version
   string. Do NOT match on major only.
2. **Strict unknown-key rejection.**
   - Allowed top-level keys: `apiVersion`, `id`, `name`, `description`, `category`,
     `workspace_kind`, `supervision`, `params`, `steps`, `final`.
     (`workspace_kind` is accepted-and-ignored in MVP — present in the allow-set so valid
     spec files parse, but not modeled. `supervision` IS modeled and value-validated —
     see rule 9.)
   - Allowed per-step keys: `id`, `name`, `prompt`, `inputs`, `output`, `gate`,
     `adapter`, `model`. (`adapter`/`model` accepted-and-ignored.)
   - Allowed per-param keys: `id`, `label`, `required`, `type`.
   - Any key outside these sets raises, naming the key and its location.
3. **Required keys.** Top-level `id`, `name`, `final`, and a non-empty `steps` list are
   required. Each step requires `id`, `prompt`, `output`. Each param requires `id`.
4. **Unique step ids.** Duplicate step `id` raises.
5. **Inputs reference integrity.** For each step, every entry in `inputs` must be the
   literal `"params"` OR the `id` of a step appearing **earlier** in the list. Forward
   references, self-references, and unknown ids raise.
6. **final resolves.** `final` must equal the `output` of at least one step.
7. **gate values.** `gate` (when present) must be in `VALID_GATES` (`none | review`).
8. **category.** When set, must be in `VALID_CATEGORIES`.
9. **supervision.** When present, must be in `VALID_SUPERVISION`
   (`supervised | gated | autonomous`); when absent, defaults to `gated`. Any other value
   raises, naming the value. (Spec §3.1: parsed into `RecipeDefinition`, never
   accept-and-ignore; never stored as an `operator`/`auto` mode value.)

### Functions
```python
def parse_recipe(data: dict) -> RecipeDefinition:
    """Validate a parsed-YAML dict against grain.recipe/v2 and build the model.
    Raises RecipeSchemaError on any violation above."""

def load_recipe(path: str | Path) -> RecipeDefinition:
    """Read a recipe.yaml file, YAML-parse it, and return parse_recipe(data).
    Raises RecipeSchemaError (wrapping YAML errors) on unreadable/invalid files."""
```

Ordering guarantee: `parse_recipe` preserves the YAML `steps` order; the returned
`steps` list is index-aligned with the file so a later run cursor can walk it linearly.

## Out of scope for this packet (do NOT build here)
- `run.json` / `grain.recipe-run/v1` model, `RecipeRun`, `RecipeStepRecord` (later packet).
- Any CLI (`grain recipe ...`) or service wiring, command registration.
- Operator-mode/auto-mode execution, `WorkflowLoopAgentConfig` reuse, agent shell-out.
- `{{param}}` / `{{steps.<id>}}` prompt rendering.
- Reading prompt files referenced by `step.prompt` (only the recipe.yaml itself is read).
- Behavioral handling of `workspace_kind`, `supervision`, per-step `adapter`/`model`.
- Output-artifact existence validation (that is a runner concern, not a definition concern).

## Acceptance Checklist
- [ ] `parse_recipe(<research-brief example>)` → 6 steps in order, 1 param (`topic`,
      required), `final == "brief.md"`.
- [ ] `grain.recipe/v1` and `grain.recipe/v3` each raise `RecipeSchemaError` whose message
      names the offending version string; `v2` parses.
- [ ] `supervision` parses onto the model (`supervised|gated|autonomous`), defaults to
      `gated` when absent, and an invalid value raises naming the value.
- [ ] Unknown top-level key raises, naming the key.
- [ ] Unknown per-step key raises, naming the key.
- [ ] Step `inputs` with forward/unknown id raises; valid `params` + earlier-id passes.
- [ ] `final` not matching any step `output` raises.
- [ ] `gate: review` parses; `gate: approve` raises.
- [ ] Duplicate step id raises.
- [ ] `uv run pytest tests/test_recipe_model.py` ≥ 8 tests pass; full suite no regressions.

## Test cases to include (`tests/test_recipe_model.py`)
1. Happy path: full `research-brief` spec example parses with expected shape.
2. apiVersion v1 rejected; v3 rejected; missing apiVersion rejected; v2 accepted. Assert
   the rejection message names the offending version string (parallel to the unknown-key
   test).
2b. `supervision` accepted for each of `supervised|gated|autonomous` and round-trips onto
   the model; absent → defaults to `gated`; an invalid value (e.g. `operator`) rejected,
   message naming the value.
3. Unknown top-level key rejected (message names the key).
4. Unknown per-step key rejected.
5. Unknown per-param key rejected.
6. Forward/unknown `inputs` reference rejected; `["params", "<earlier-id>"]` accepted.
7. `final` with no matching step output rejected.
8. Invalid `gate` value rejected; `none`/`review` accepted.
9. Duplicate step id rejected; missing required step key (`output`) rejected.
10. `load_recipe` round-trips a written temp YAML file to an equal `RecipeDefinition`.
