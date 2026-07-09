# Task: CLI — grain recipe list / show / scaffold

## Metadata
- **ID:** P34-T04
- **Status:** done
- **Phase:** Phase 34 — Recipe Step-Runner MVP
- **Backlog:** P34-T04
- **Packet Path:** tasks/P34-T04/
- **Recipe-engine:** parallel step-runner — read-only/scaffold surface; consumes `grain.recipe/v2` definitions, does NOT touch `run.json` (`grain.recipe-run/v1`), the SDLC packet loop, or `evaluate_workflow_state`
- **Dependencies:** P34-T01, P34-T03
- **Primary Adapter:** code
- **Secondary Adapters:** none

## Objective
Add the read-only and bootstrap CLI surface for the recipe step-runner: `grain recipe list`,
`grain recipe show <id>`, and `grain recipe scaffold <id>`. These three commands let a human or a
familiar discover which recipes exist (bundled + workspace), inspect a recipe's steps/params/gates
before running it, and bootstrap a new recipe skeleton under `docs/recipes/<id>/`. The `recipe`
click group is created here and registered in `cli/__init__.py` via the existing CLI-group pattern
so that P34-T05+ (run/next/status/resume) can attach their subcommands to the same group. All three
commands support `--format json` so the surface is fully familiar-drivable.

## Why This Task Exists
v0.5.0 contract deliverable #2 (`grain recipe` execution) and #6 (grain-as-engine / familiar-
drivable). The recipe engine spec §4 lists `list | show | scaffold` in the full CLI surface; `list`
and `show` are also in the §7 "MVP must ship" slice, while `scaffold` is the bootstrap authoring
command that the rest of the surface (and the bundled-recipe packet P34-T06) depends on. These are
the discovery/inspection/bootstrap commands that precede running anything: without `list`/`show` no
one can find or vet a recipe, and without `scaffold` there is no supported way to author a new
`grain.recipe/v2` definition. They are pure (read + skeleton-write) and have no run-state
dependency, so they are isolated from the run-loop packets.

## Scope
- New `src/grain/cli/recipe.py` defining the `recipe` click group (`@click.group("recipe")`) and the
  three subcommands `list`, `show`, `scaffold`.
- **`grain recipe list`** — enumerate bundled recipes plus workspace recipes (`docs/recipes/<id>/`),
  via the recipe discovery/loader from P34-T01/P34-T03. Text table (id, name, category, source,
  step count); `--format json` emits a list of recipe summary objects.
- **`grain recipe show <id>`** — load and render one recipe definition: id/name/description/
  category/supervision, params (id, label, required, type), and the ordered steps (id, name, inputs,
  output, gate). Text is human-readable; `--format json` emits the normalized definition shape.
- **`grain recipe scaffold <id>`** — create `docs/recipes/<id>/` with a minimal valid
  `recipe.yaml` (apiVersion `grain.recipe/v2`, one example param, two linear example steps with
  `inputs`/`output`, and `final`) plus a `steps/` dir holding the referenced prompt stubs. Refuses
  to overwrite an existing recipe dir unless `--force`.
- Register the group: `from .recipe import recipe_group` + `main.add_command(recipe_group)` in
  `src/grain/cli/__init__.py`, matching the existing `add_command` block.
- Tests under `tests/` covering all three commands in text and JSON modes plus the error/refusal
  paths.

## Constraints
- **MVP only.** No `run`/`next`/`status`/`resume`/`gate` here (later P34 packets), no auto-mode, no
  MCP, no `recipe suggest`, no branching/parallel/loops, no per-step adapter scoping, no
  apply/write-back.
- `--format json` is the **global** flag read from `ctx.obj["fmt"]` (same idiom as
  `cli/workflow.py`); do not add a per-command `--format` option.
- `list`/`show` are **read-only** — they must not create or mutate `run.json` or any run directory,
  and must not call `evaluate_workflow_state` or the SDLC packet loop.
- Reuse the loader/domain dataclasses from P34-T01 (`RecipeDefinition`, `RecipeStep`) and the
  discovery service from P34-T03; this packet adds no parsing or validation logic of its own beyond
  surfacing what the loader returns.
- `scaffold` must emit a `recipe.yaml` that `grain recipe show <id>` can immediately load without
  error (i.e. a valid `grain.recipe/v2` document).
- Errors (unknown recipe id, malformed definition, scaffold collision) go through the existing
  `grain.domain.errors` types and `handle_error`, returning a non-zero exit code.

## Acceptance Criteria
- `grain recipe list` enumerates recipes via the P34-T03 discovery service, with `source`
  distinguishing bundled vs workspace; the test scaffolds a fixture recipe (via `grain recipe
  scaffold`) into the workspace and asserts that fixture appears with `source == "workspace"` — the
  test does NOT depend on the bundled `research-brief` recipe (owned by P34-T06).
- `grain --format json recipe list` emits a JSON array where each element has `id`, `name`,
  `category`, `source`, and `step_count`; assertable by a test parsing the output.
- `grain recipe show <id>` prints the recipe's params and ordered steps for a workspace fixture
  recipe; `grain --format json recipe show <id>` emits an object whose `apiVersion` is
  `grain.recipe/v2` and whose `steps[]` carry `id`, `inputs`, `output` (and `gate` when present, for
  a fixture step that declares a gate), matching spec §2.1. Tests use a fixture recipe written into
  the workspace, not the bundled `research-brief`.
- `grain recipe show <unknown-id>` exits non-zero with a clear error and does not traceback; tested.
- `grain recipe scaffold demo` creates `docs/recipes/demo/recipe.yaml` (valid `grain.recipe/v2`)
  plus the referenced `steps/` prompt stubs, and a subsequent `grain recipe show demo` succeeds;
  re-running `scaffold demo` without `--force` exits non-zero without overwriting; tested.
- `recipe_group` is importable from `grain.cli` and `grain recipe --help` lists `list`, `show`,
  `scaffold` (group registered in `cli/__init__.py`).

## Dependencies
- **P34-T01** — recipe domain dataclasses + `grain.recipe/v2` loader/parser (`RecipeDefinition`,
  `RecipeStep`, `VALID_*` frozensets). `show`/`list` render what this produces.
- **P34-T03** — recipe discovery service (bundled + workspace enumeration). `list` consumes it.

## Relevant Files
- `src/grain/cli/recipe.py` *(new)* — `recipe` group + `list`/`show`/`scaffold` commands.
- `src/grain/cli/__init__.py` *(edit)* — import and `main.add_command(recipe_group)`.
- `src/grain/cli/workflow.py` *(reference)* — `ctx.obj["fmt"]` JSON-output idiom + group pattern.
- `src/grain/services/recipe_service.py` *(consumed, from P34-T01/T03)* — loader + discovery.
- `src/grain/domain/` recipe dataclasses *(consumed, from P34-T01)*.
- `docs/working/recipe_engine_spec.md` §2.1, §4, §7, §9 — data model + CLI contract.
- `tests/` *(new tests)* — CLI behavior for the three commands.

## Model Recommendation
Claude Sonnet (claude-sonnet-4-5). This is a contained CLI packet over already-specified domain
types and an established click-group idiom — mechanical surface work, no novel design. Escalate to
Opus only if the P34-T01/T03 loader/discovery interfaces turn out to be unstable when implementing.
