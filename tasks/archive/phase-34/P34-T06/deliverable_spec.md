# Deliverable Spec — P34-T06: Bundled research-brief recipe

Concrete done-definition. Grounded in `docs/working/recipe_engine_spec.md` §2.1 (recipe.yaml
`grain.recipe/v2`) and §7 (MVP slice). This packet ships **data only**; the parser (T01), the
operator-mode engine + run/`run.json` `grain.recipe-run/v1` + recipe enumeration (T03), and the
`recipe list/show/scaffold` CLI (T04) are consumers, not deliverables here. This packet adds no
discovery/enumeration helper.

---

## 1. Files created

```
src/grain/data/recipes/research-brief/
├── recipe.yaml                 # apiVersion: grain.recipe/v2
└── steps/
    ├── intake.md
    ├── gather.md
    ├── outline.md
    ├── draft.md
    ├── self_check.md
    └── format.md
```

All seven files are package data (shipped in the wheel via `[tool.setuptools.package-data]`). They
are read-only at runtime; nothing writes into `data/recipes/`.

---

## 2. `recipe.yaml` — exact shape

`apiVersion: grain.recipe/v2`. Mirrors spec §2.1, with the demo-locked change that **no step
declares a gate** (`gate:` keys omitted entirely).

```yaml
apiVersion: grain.recipe/v2
id: research-brief
name: "Research Brief"
description: "Produce a sourced research brief on a topic"
category: research
supervision: autonomous       # gateless default run mode; NOT a per-step gate

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
    name: "Outline the brief"
    prompt: steps/outline.md
    inputs: [intake, gather]
    output: 03-outline.md
  - id: draft
    name: "Draft the brief"
    prompt: steps/draft.md
    inputs: [outline, gather]
    output: 04-draft.md
  - id: self_check
    name: "Self-check the draft"
    prompt: steps/self_check.md
    inputs: [draft, gather]
    output: 05-review.md
  - id: format
    name: "Format the deliverable"
    prompt: steps/format.md
    inputs: [draft, self_check]
    output: brief.md

final: brief.md
```

Field rules (must hold for the T01 v2 parser to accept it):
- `apiVersion == "grain.recipe/v2"`.
- `id`, `name`, `description`, `category` present; `category` ∈ the v1 category set
  (`research | docs | data | ops | content | code | custom`) → `research`.
- `supervision == "autonomous"`: a gateless default run mode (no step declares `gate: review`, so a
  `gated`/`supervised` value would be misleading; `autonomous` states the gateless intent). It is a
  `supervision` value (`supervised | gated | autonomous`) — never an operator/auto `mode` value.
- `params`: one entry, `id: topic`, `required: true`, `type: string`.
- `steps`: ordered list of 6; each has `id`, `prompt` (path relative to the recipe dir resolving to
  an existing file under `steps/`), `inputs` (list), `output` (filename).
- Every `inputs` token is either the literal `params` or the `id` of an **earlier** step
  (`intake, gather, outline, draft, self_check` resolve; no forward refs).
- `final == "brief.md"` and equals the last step's `output`.
- No `gate:`, no per-step `adapter:`/`model:`, no `workspace_kind:` (all deferred); strict schema
  validation passes with zero unknown keys.

---

## 3. Step prompt files

Each `steps/*.md` is plain Markdown with minimal-template tokens only — `{{topic}}` and
`{{steps.<id>}}` — matching today's `prompt.md` rendering (no control flow). Each prompt:
1. states the step's goal,
2. references only its declared `inputs` (via `{{topic}}` and/or `{{steps.<id>}}`),
3. ends by instructing the runner to write the step's declared `output` artifact (operator-mode
   safe: deterministic, no network assumption).

Required token usage (verified by test):

| file           | step       | inputs available            | must reference                | writes        |
|----------------|------------|-----------------------------|-------------------------------|---------------|
| `intake.md`    | intake     | params                      | `{{topic}}`                   | `01-intake.md`|
| `gather.md`    | gather     | params, intake              | `{{topic}}`, `{{steps.intake}}` | `02-sources.md`|
| `outline.md`   | outline    | intake, gather              | `{{steps.intake}}`, `{{steps.gather}}` | `03-outline.md`|
| `draft.md`     | draft      | outline, gather             | `{{steps.outline}}`, `{{steps.gather}}` | `04-draft.md`|
| `self_check.md`| self_check | draft, gather               | `{{steps.draft}}`, `{{steps.gather}}` | `05-review.md`|
| `format.md`    | format     | draft, self_check           | `{{steps.draft}}`, `{{steps.self_check}}` | `brief.md`|

Minimum bar for the test: `intake.md` contains `{{topic}}`; at least one downstream prompt contains
a `{{steps.` token. (Table above is the authoring target.)

---

## 4. Discovery (owned by T03 — not built here)

This packet adds **no** discovery/enumeration code. Recipe enumeration (bundled + workspace) is owned
by **T03** in `src/grain/services/recipe_service.py` (created by T03). T03's enumeration scans the
bundled recipes root (`src/grain/data/recipes/`, mirroring the `_BUNDLED_DATA_ROOT` pattern in
`init_service.py` / `upgrade_service.py`) for directories containing a `recipe.yaml`, tags them
`source: "bundled"`, and merges them with workspace recipes under `docs/recipes/*/recipe.yaml`
(`source: "workspace"`). Resolution must work from an installed wheel (package path), not a
repo-relative path.

This packet's only obligation here is to **place** the bundled recipe under
`src/grain/data/recipes/research-brief/` so T03's enumeration finds it. The T04 CLI
(`recipe list/show`) renders T03's enumeration output; the exact JSON envelope is owned by T04.

A scaffolded fixture (not this bundled recipe) backs the T04 list test, so the CLI tests do not
depend on this packet's data.

---

## 5. Packaging

- `pyproject.toml` already declares `[tool.setuptools.package-data] grain = ["data/**/*"]`, which
  should recursively include `data/recipes/research-brief/recipe.yaml` and `steps/*.md`.
- Done-definition: a packaging test **builds the wheel** (e.g. `python -m build --wheel` / `uv build`)
  or **installs into a clean environment**, then asserts the recipe files (`recipe.yaml` + the 6
  `steps/*.md`) are present **in the built/installed artifact** — by inspecting the wheel's contents
  (the wheel is a zip; check its namelist) or by resolving them from the installed package
  (`importlib.resources.files("grain") / "data" / "recipes" / "research-brief"`). It must NOT pass by
  resolving paths against the source tree.
- Only if that test fails against a built/installed artifact: add an explicit
  `data/recipes/**/*` entry (and `MANIFEST.in` if the build backend needs it) — otherwise no
  packaging-config change.

---

## 6. Tests (new test module)

1. **Schema validity** — load `recipe.yaml` via the T01 v2 parser; assert zero errors,
   `apiVersion == "grain.recipe/v2"`, 6 steps in the exact order, each `inputs`/`output` per §2,
   `final == "brief.md"`, and `supervision == "autonomous"`.
2. **File presence** — assert `recipe.yaml` + all 6 `steps/*.md` exist; assert no `gate:` /
   `adapter:` / per-step `model:` / `workspace_kind:` keys in `recipe.yaml`.
3. **Token references** — `intake.md` contains `{{topic}}`; ≥1 downstream prompt contains `{{steps.`.
4. **Packaging (built artifact)** — build the wheel (or install into a clean env) and assert the
   recipe files (`recipe.yaml` + 6 `steps/*.md`) are present in the built/installed artifact — via
   the wheel namelist or the installed-package path, NOT resolved against the source tree.

---

## 7. Out of scope (restated)

Engine logic, including recipe enumeration (T01/T03); the `recipe list/show/scaffold` CLI (T04);
gates/`supervised` polish; auto-mode; MCP; `recipe suggest`/`scaffold`/`install`;
branching/parallel/loops; per-step `adapter`/`model`; `workspace_kind` integration; apply/write-back.
No discovery/enumeration helper is added here. No task packets are created and the SDLC review/close
loop is untouched (recipes are a parallel engine).
