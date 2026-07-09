# Task: Recipe definition model + v2 schema parser

## Metadata
- **ID:** P34-T01
- **Status:** done
- **Phase:** Phase 34 — Recipe Step-Runner MVP
- **Backlog:** P34-T01
- **Packet Path:** tasks/P34-T01/
- **Dependencies:** none
- **Primary Adapter:** code
- **Secondary Adapters:** none
- **Recipe-engine:** definition layer — `recipe.yaml` `apiVersion: grain.recipe/v2`; parallel engine (does NOT create task packets or touch the SDLC review/close loop)

## Objective
Implement the recipe **definition** domain layer: `RecipeDefinition` and `RecipeStep`
dataclasses plus a parser/validator that loads a `recipe.yaml` of
`apiVersion: grain.recipe/v2` into those dataclasses. This is the foundation every other
Phase 34 packet (run state, operator-mode runner, CLI surface) builds on — it owns the
shape of a recipe and the strict validation that the rest of the engine can rely on.

## Why This Task Exists
The recipe step-runner (recipe_engine_spec.md §2.1, §9) reframes a recipe from a
single-packet SDLC entry point into a general, ordered, multi-step workflow engine that
runs **parallel to** the SDLC loop. Before any run state or execution can exist, the
engine needs a typed, validated in-memory model of a recipe definition. This packet
delivers deliverable #2's parsing core (`grain recipe` execution) and honors the
versioned-engine-contract principle (§1.5): the parser is the gate that rejects unknown
majors and unknown keys so downstream tools and familiars can depend on the contract.

## Scope
- New `src/grain/domain/recipe.py`:
  - `RecipeStep` dataclass: `id`, `prompt`, `inputs: list[str]`, `output`, optional
    `name`, optional `gate` (default `"none"`). `__post_init__` validation + `VALID_GATES`
    frozenset.
  - `RecipeDefinition` dataclass: `id`, `name`, `params: list[RecipeParam]`,
    `steps: list[RecipeStep]`, `final`, `supervision` (default `"gated"`), plus optional
    retained-from-v1 metadata (`description`, `category`). `__post_init__` validation +
    `VALID_CATEGORIES` and `VALID_SUPERVISION` frozensets.
  - `RecipeParam` dataclass: `id`, `required: bool`, optional `label`, `type`
    (default `"string"`).
  - `parse_recipe(data: dict) -> RecipeDefinition` and
    `load_recipe(path) -> RecipeDefinition` (read YAML file → `parse_recipe`).
  - `RECIPE_API_VERSION = "grain.recipe/v2"` and a `RecipeSchemaError` exception type.
- Strict schema validation:
  - Reject any unknown top-level key and any unknown per-step / per-param key.
  - Accept `apiVersion` only when it is **exactly** the string `grain.recipe/v2`. Any
    missing, malformed, or other value (`grain.recipe/v1`, `grain.recipe/v3`, major-only
    matches, etc.) → error; do NOT match on major only.
  - Parse and validate `supervision` against `{supervised | gated | autonomous}`
    (default `gated` when absent); reject any other value. (Spec §3.1: supervision is
    parsed into `RecipeDefinition`, not accept-and-ignore.)
  - Validate cross-references: every step `inputs` entry is either the literal `params`
    or the `id` of an **earlier** step; `final` matches some step's `output`.
- New `tests/test_recipe_model.py` covering the criteria below.
- Reuse Grain idioms: `@dataclass` + `__post_init__` + `VALID_*` frozensets, mirroring
  `src/grain/domain/workflow_loop.py`.

## Constraints
- **MVP only.** Parse exactly the keys in scope. Per-step `adapter` and `model` keys and
  `workspace_kind` are NOT parsed/validated here beyond being accepted-and-ignored where
  the spec marks them optional — do not implement their behavior. `supervision` IS parsed
  and validated (value-checked against `VALID_SUPERVISION`) but its run-time pause behavior
  is a later (runner) packet's concern — model it, do not act on it. Gates beyond
  `none | review` are deferred; keep `gate` in the schema but only validate the value.
- This is the **definition** model only — no `run.json` (`grain.recipe-run/v1`), no run
  state, no CLI, no execution, no `{{param}}` rendering, no file I/O beyond reading the
  recipe YAML in `load_recipe`.
- Parallel engine: do not import or touch `workflow_service`, `evaluate_workflow_state`,
  or packet-lifecycle code.
- Validation failures raise `RecipeSchemaError` with a message naming the offending
  key/version — never silently drop or coerce.

## Deliverable
- `src/grain/domain/recipe.py` with the dataclasses, frozensets, `RECIPE_API_VERSION`,
  `RecipeSchemaError`, `parse_recipe`, and `load_recipe` as specified in
  `deliverable_spec.md`.
- `tests/test_recipe_model.py` with the cases enumerated in the acceptance criteria.

## Acceptance Criteria
- `parse_recipe` on the spec's `research-brief` example (recipe_engine_spec.md §2.1)
  returns a `RecipeDefinition` with 6 ordered `RecipeStep`s, one `RecipeParam` (`topic`,
  `required=True`), and `final == "brief.md"`.
- A recipe whose `apiVersion` is `grain.recipe/v1` or `grain.recipe/v3` (or any string
  other than the exact `grain.recipe/v2`) raises `RecipeSchemaError`, and the error message
  names the offending version string; `grain.recipe/v2` parses successfully (asserted in
  tests).
- `supervision: autonomous` (and `supervised`, `gated`) parses and round-trips onto the
  `RecipeDefinition`; an absent `supervision` defaults to `gated`; an invalid value
  (e.g. `supervision: operator`) raises `RecipeSchemaError` naming the value.
- An unknown top-level key (e.g. `foo: bar`) and an unknown per-step key (e.g. a step
  with `widget: 1`) each raise `RecipeSchemaError` naming the offending key.
- A step whose `inputs` references a non-`params`, non-earlier-step id (forward or
  unknown reference) raises `RecipeSchemaError`; a `final` that matches no step `output`
  raises `RecipeSchemaError`.
- A step with `gate: review` parses and round-trips; a step with `gate: approve` (invalid
  value) raises `RecipeSchemaError`.
- `uv run pytest tests/test_recipe_model.py` passes with ≥ 8 tests and the full suite
  shows no regressions.

## Dependencies
- none

## Relevant Files
- `src/grain/domain/recipe.py` (new) — definition model + parser.
- `tests/test_recipe_model.py` (new) — model/parser tests.
- `src/grain/domain/workflow_loop.py` (reference) — dataclass + `__post_init__` +
  `VALID_*` frozenset idiom to mirror; source of `WorkflowLoopAgentConfig` reused later
  by the auto-mode packet (not this one).
- `docs/working/recipe_engine_spec.md` §2.1, §8, §9 (contract for the schema).
- `docs/working/v0.5.0_contract.md` §2 (deliverables #2, #6, #10) (context).

## Escalation Conditions
- If the spec's accept-and-ignore keys (`adapter`, `model`, `workspace_kind`) need defined
  behavior to satisfy a downstream packet, stop and log a change proposal rather than
  implementing it here. (`supervision` is parsed and value-validated here; its run-time
  pause semantics belong to the runner packet — do not implement them in this packet.)
- If reusing `WorkflowLoopAgentConfig` for any definition-layer concern proves necessary
  (it should not be — that is auto-mode), record a blocker; auto-mode is a separate packet.

## Model Recommendation
Opus-class for the validation design (cross-reference checks, strict-key rejection, and
version gating have subtle edge cases worth getting right once). The implementation itself
is mechanical; a Sonnet-class model can execute against this packet if the validation
table in `deliverable_spec.md` is followed literally.
