# Task: Bundled research-brief recipe

## Metadata
- **ID:** P34-T06
- **Status:** draft
- **Phase:** 34 — Recipe step-runner MVP
- **Backlog:** P34-T06
- **Packet Path:** tasks/P34-T06/
- **Dependencies:** P34-T01, P34-T03, P34-T04
- **Primary Adapter:** code
- **Secondary Adapters:** none
- **Recipe-engine:** ships the canonical `grain.recipe/v2` bundled recipe + step prompts; **data only** — does NOT implement the parser, the engine/run, recipe enumeration, or any CLI (those are T01/T03/T04).

## Objective
Author and bundle the `research-brief` recipe so it ships inside the `grain-kit` package and is
discovered by `grain recipe list` (enumeration owned by T03) in any workspace with no install step.
This is the one bundled recipe the v0.5.0 demo runs end-to-end in operator mode. Deliver a valid
`grain.recipe/v2` `recipe.yaml` (6 linear steps: `intake → gather → outline → draft → self_check →
format`, no gates), the six step prompt files it references, and the package-data plumbing so the
files are present in a built/installed wheel. This packet ships **data only** — recipe enumeration
(bundled + workspace) is owned by T03; this packet does not add any discovery helper.

## Why This Task Exists
The recipe engine (parser T01, operator-mode engine + recipe enumeration T03, CLI list/show/scaffold
T04) is inert without a real recipe to run. Spec §7 names exactly one MVP bundled recipe —
`research-brief` (6 steps) — runnable on a pre-staged workspace, and v0.5.0 contract deliverable #2
calls for "bundled starter recipes". This packet supplies that recipe as package data so T03's
enumeration surfaces it alongside workspace recipes.

## Approach / Scope
**In scope**
- New `src/grain/data/recipes/research-brief/recipe.yaml` — `apiVersion: grain.recipe/v2`, the 6
  steps and their `inputs`/`output` exactly as in spec §2.1, `params: [topic]`, `final: brief.md`.
  No `gate:` keys (demo runs gateless); `supervision: autonomous` so the recipe declares a gateless
  default run mode end-to-end (no `gate: review` step means a `gated` run would never pause anyway —
  `autonomous` states the gateless intent explicitly).
- New step prompt files under `src/grain/data/recipes/research-brief/steps/`:
  `intake.md`, `gather.md`, `outline.md`, `draft.md`, `self_check.md`, `format.md`. Each uses the
  existing minimal `{{topic}}` / `{{steps.<id>}}` substitution tokens only (no control flow), and
  instructs the operator/familiar to write the step's declared `output` artifact.
- Package-data confirmation: verify `[tool.setuptools.package-data] grain = ["data/**/*"]` already
  globs the new nested `recipes/research-brief/**` files into a built wheel; if the recursive glob
  does not capture them, add the explicit `data/recipes/**/*` entry. No `MANIFEST.in` change unless
  the build proves files are missing.
- Tests (see Acceptance Criteria).

**Out of scope (deferred / other packets)**
- The v2 parser/dataclasses (T01), the operator-mode engine + `RecipeRun`/`run.json` + recipe
  enumeration (bundled + workspace) (T03), and the `recipe list/show/scaffold` CLI surface (T04) —
  this packet only adds the data they consume; it adds no discovery/enumeration helper.
- Gates / `supervised` polish, auto-mode, MCP, `recipe suggest`/`scaffold`/`install`, branching/
  parallel/loops, per-step `adapter`/`model`, `workspace_kind` integration, apply/write-back.

## Deliverable
- `src/grain/data/recipes/research-brief/recipe.yaml` (valid `grain.recipe/v2`, 6 steps, no gates).
- Six step prompt files under `src/grain/data/recipes/research-brief/steps/`.
- Package-data plumbing verified by building/installing the wheel (and amended only if needed).
- Tests covering schema validity, file presence, packaged inclusion (built wheel), and token
  references.

## Acceptance Criteria
- A test loads `recipe.yaml` through the T01 v2 parser and it validates with zero errors (correct
  `apiVersion: grain.recipe/v2`, exactly 6 steps in order `intake, gather, outline, draft,
  self_check, format`, every step's `prompt` path resolves to an existing file under `steps/`, every
  step's `inputs`/`output` match spec §2.1, every non-`params` `inputs` id refers to an earlier
  step's id, and `final == "brief.md"`).
- A test asserts all seven shipped files exist under
  `src/grain/data/recipes/research-brief/` (`recipe.yaml` + 6 `steps/*.md`), and that
  `intake.md` contains `{{topic}}` and at least one downstream prompt contains a `{{steps.` token.
- A packaging test builds the wheel (or installs into a clean environment) and asserts the recipe
  files (`recipe.yaml` + the 6 `steps/*.md`) are present in the built/installed artifact — verified
  against the wheel contents / installed package, NOT resolved against the source tree.
- `recipe.yaml` contains no `gate:` keys and no deferred keys (`adapter`, per-step `model`,
  `workspace_kind`); strict v2 schema validation rejects nothing.

## Constraints
- Do not implement engine logic owned by T01/T03/T04, and do not add any recipe-enumeration/discovery
  helper — enumeration (bundled + workspace) is owned by T03. This packet ships data only.
- Bundled recipes are read-only package data; never written to at runtime. Runs always live under
  `docs/recipes/runs/<run-id>/` (T03), never inside `data/`.
- Prompts must be operator-mode-safe: deterministic instructions, no network assumptions, each ends
  by telling the runner the artifact path to write.
- Keep substitution to the existing minimal templating (`{{topic}}`, `{{steps.<id>}}`); no new
  template engine.

## Dependencies
- **P34-T01** — `grain.recipe/v2` parser / `RecipeDefinition`+`RecipeStep` dataclasses (validates this recipe).
- **P34-T03** — operator-mode engine + `RecipeRun`/run.json + recipe enumeration (bundled + workspace) that surfaces this recipe.
- **P34-T04** — `grain recipe list/show/scaffold` CLI that displays this bundled recipe (via T03's enumeration).

## Relevant Files
- `src/grain/data/recipes/research-brief/recipe.yaml` (new)
- `src/grain/data/recipes/research-brief/steps/{intake,gather,outline,draft,self_check,format}.md` (new)
- `pyproject.toml` — `[tool.setuptools.package-data]` (`data/**/*`; amend only if a built wheel misses nested files)
- `docs/working/recipe_engine_spec.md` §2.1 (recipe.yaml shape), §7 (MVP slice)
- `tests/` — new test module for bundled recipe + packaging

## Model Recommendation
Sonnet-class. This is bounded, well-specified data authoring grounded in spec §2.1 plus a packaging
check; no novel architecture and no engine/discovery code. Opus-class is not warranted.

## Escalation Conditions
- The T01 parser rejects any spec-§2.1 key this recipe must carry (signals a parser/spec mismatch).
- `data/**/*` does not package the nested `recipes/**` files in a built wheel and a `MANIFEST.in` /
  build-config change is required (cross-cuts packaging beyond this packet's intent).
