# Deliverable Spec — P34-T04: CLI `grain recipe list / show / scaffold`

Concrete done-definition. Grounded in `docs/working/recipe_engine_spec.md` §2.1
(`recipe.yaml` = `grain.recipe/v2`), §4 (CLI surface), §9 (idioms). This packet is read-only +
scaffold; it never reads or writes `run.json` (`grain.recipe-run/v1`).

## 1. Files

| Path | Action |
|------|--------|
| `src/grain/cli/recipe.py` | new — `recipe_group` + `list`/`show`/`scaffold` commands |
| `src/grain/cli/__init__.py` | edit — `from .recipe import recipe_group`; `main.add_command(recipe_group)` |
| `tests/test_cli_recipe.py` (or repo's test convention) | new — coverage for the three commands |

No source outside the recipe CLI surface and the one `__init__.py` registration line is touched.

## 2. Consumed interfaces (from P34-T01 / P34-T03 — do not reimplement)

This packet calls into, and only renders, the following (names indicative; bind to the actual
P34-T01/T03 symbols at implementation time):

- `RecipeDefinition` dataclass (P34-T01): fields covering `apiVersion`, `id`, `name`,
  `description`, `category`, `supervision`, `params: list[RecipeParam]`, `steps: list[RecipeStep]`,
  `final: str`. Carries `__post_init__` validation against `VALID_CATEGORY` / `VALID_SUPERVISION`
  frozensets.
- `RecipeStep` dataclass (P34-T01): `id`, `name | None`, `prompt`, `inputs: list[str]`,
  `output: str`, `gate: str | None` (validated against `VALID_GATE = {"none", "review"}`).
- `RecipeParam` dataclass (P34-T01): `id`, `label`, `required: bool`, `type: str`.
- `load_recipe(root, recipe_id) -> RecipeDefinition` (P34-T01 loader) — raises a
  `grain.domain.errors` error on unknown id or malformed/unknown-major `apiVersion`.
- `discover_recipes(root) -> list[RecipeSummary]` (P34-T03) — bundled + workspace enumeration.
  `RecipeSummary` exposes `id`, `name`, `category`, `source` (`"bundled" | "workspace"`),
  `step_count: int`.

If the exact P34-T01/T03 symbol names differ, adapt the calls; the rendering contract below is the
deliverable.

## 3. CLI signatures & behavior

All three attach to `recipe_group = click.Group("recipe")`. Format is taken from the **global**
flag: `fmt = ctx.obj.get("fmt", "text")` (mirrors `cli/workflow.py`). Each command uses
`@click.pass_context` and resolves the workspace via `resolve_repo_root(ctx.obj.get("repo"))`.

### 3.1 `grain recipe list`
```
grain recipe list
grain --format json recipe list
```
- Calls `discover_recipes(root)`.
- Text: a table with columns `ID  NAME  CATEGORY  SOURCE  STEPS`, one row per recipe, bundled
  before workspace; trailing summary line `N recipes (B bundled, W workspace)`.
- JSON: a JSON **array**; each element:
  ```json
  {"id": "research-brief", "name": "Research Brief", "category": "research",
   "source": "bundled", "step_count": 6}
  ```
- Empty workspace + bundled set still lists the bundled recipes. Exit 0.

### 3.2 `grain recipe show <id>`
```
grain recipe show <id>
grain --format json recipe show <id>
```
- `id` is a required positional arg.
- Calls `load_recipe(root, id)`.
- Text sections: header (`id`, `name`, `category`, `supervision`, `description`), a `Params:` block
  (`- <id> (<type>, required|optional): <label>`), and an ordered `Steps:` block
  (`<n>. <id> [<name>]  inputs=[...] -> <output>  gate=<gate>` when `gate` set).
- JSON: the normalized definition object — shape mirrors spec §2.1:
  ```json
  {
    "apiVersion": "grain.recipe/v2",
    "id": "research-brief",
    "name": "Research Brief",
    "description": "...",
    "category": "research",
    "supervision": "gated",
    "params": [
      {"id": "topic", "label": "Topic", "required": true, "type": "string"}
    ],
    "steps": [
      {"id": "intake", "name": "Frame the topic", "inputs": ["params"],
       "output": "01-intake.md"},
      {"id": "self_check", "inputs": ["draft", "gather"],
       "output": "05-review.md", "gate": "review"}
    ],
    "final": "brief.md"
  }
  ```
  **Per-step `prompt` is NOT emitted in `show` output.** `prompt` is an authoring path (where the
  step body lives), not part of the inspect-before-run contract; the worked example above omits it
  deliberately. The serialized step shape is exactly `id`, `name` (when set), `inputs`, `output`,
  and `gate` (when set). Serialize from the dataclass with an explicit drop list so the result
  matches the example: drop the `prompt` field, drop `None`-valued `name`/`gate`, and drop any
  internal/`adapter`/`model` fields (e.g. `dataclasses.asdict(step)` then pop those keys) — do not
  hand-roll a divergent shape, and do not let raw `asdict` leak `prompt` into the output.
- Unknown / malformed id: raise the loader's `grain.domain.errors` exception → routed through
  `handle_error` → non-zero exit, single-line message, no traceback.

### 3.3 `grain recipe scaffold <id>`
```
grain recipe scaffold <id>
grain recipe scaffold <id> --force
grain --format json recipe scaffold <id>
```
- `id` is a required positional arg; `--force` is a boolean flag.
- Creates `docs/recipes/<id>/` containing:
  - `recipe.yaml` — a **valid `grain.recipe/v2`** document (see §4).
  - `steps/<step>.md` prompt stubs for each step referenced by the scaffolded `recipe.yaml`'s
    `prompt:` paths (one-line placeholder body each, with the `{{param}}` substitution hint).
- If `docs/recipes/<id>/` already exists: exit non-zero with a "recipe already exists" error unless
  `--force` is passed (with `--force`, overwrite the scaffolded files).
- Does NOT create anything under `docs/recipes/runs/` (no run is started).
- Text: prints the created file paths. JSON: `{"id": "<id>", "path": "docs/recipes/<id>",
  "files": ["recipe.yaml", "steps/intake.md", "steps/draft.md"], "created": true}`.
- Post-condition: `grain recipe show <id>` succeeds on the scaffolded recipe.

## 4. Scaffolded `recipe.yaml` template (emitted by `scaffold`)

Minimal but valid `grain.recipe/v2`, linear, two steps, no gate (gate key kept loadable but unset):

```yaml
apiVersion: grain.recipe/v2
id: <id>
name: "<Id Title>"
description: "TODO: describe what this recipe produces."
category: custom        # research | docs | data | ops | content | code | custom
supervision: gated      # supervised | gated | autonomous

params:
  - id: topic
    label: "Topic"
    required: true
    type: string

steps:
  - id: intake
    name: "Frame the work"
    prompt: steps/intake.md      # {{topic}} substitution available
    inputs: [params]
    output: 01-intake.md
  - id: draft
    name: "Draft the deliverable"
    prompt: steps/draft.md
    inputs: [params, intake]
    output: draft.md

final: draft.md
```

## 5. Registration (`cli/__init__.py`)

Add alongside the existing import block and the `main.add_command(...)` block (the file already
registers `workflow_group`, `suggest_group`, etc.):

```python
from .recipe import recipe_group
...
main.add_command(recipe_group)
```

`grain recipe --help` then lists `list`, `show`, `scaffold`.

## 6. Tests (must assert, not just smoke)

Use the repo's CLI test convention (click `CliRunner` / the existing harness). Tests must NOT depend
on the bundled `research-brief` recipe (owned by P34-T06); scaffold a fixture recipe into the
workspace first, or write a fixture `recipe.yaml` directly, then assert against it.

1. `recipe list` text mode: after scaffolding a fixture recipe into the workspace, the fixture row
   appears with `SOURCE == workspace`.
2. `recipe list` JSON mode parses to a list; the scaffolded fixture element has
   `source == "workspace"` and a `step_count` matching the fixture's step count. (If the bundled set
   is non-empty at test time, bundled elements carry `source == "bundled"` — but the test does not
   require any specific bundled recipe to exist.)
3. `recipe show <fixture>` JSON has `apiVersion == "grain.recipe/v2"` and a `steps` list whose
   elements carry `id`/`inputs`/`output` and do NOT carry `prompt`; for a fixture step that declares
   `gate: review`, that step carries `gate == "review"` while a non-gated step omits `gate`. (Use a
   hand-written fixture `recipe.yaml` with one gated step, since the `scaffold` template has none.)
4. `recipe show <unknown>` exits non-zero, prints an error, no traceback.
5. `recipe scaffold demo` creates `docs/recipes/demo/recipe.yaml` + `steps/` stubs; a follow-up
   `recipe show demo` succeeds.
6. `recipe scaffold demo` a second time without `--force` exits non-zero and leaves the existing
   files unchanged; with `--force` it succeeds.

## 7. Explicit non-deliverables (deferred to other packets)

`run` / `next` / `status` / `resume` / `gate` subcommands; auto-mode (`--auto`,
`WorkflowLoopAgentConfig`); any `run.json` (`grain.recipe-run/v1`) read/write; MCP exposure;
`recipe suggest`; structural/per-step validators; per-step `adapter` scoping; branching/parallel/
loops; apply/write-back. This packet ships only `list`, `show`, `scaffold`.
