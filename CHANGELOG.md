# Changelog

All notable changes to grain-kit are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
Versioning: [Semantic Versioning](https://semver.org/)

---

## [0.1.8] — 2026-04-14

### Added
- `grain task close --quick` — minimal closure for conversational and voice workflows
  - Accepts `--summary TEXT` and optional `--files PATH` (repeatable)
  - Writes a lightweight `results.md` and marks the packet `done` without requiring `handoff.md` or efficiency metrics
- `grain workflow next` gate for incomplete tasks: if an active task is `in_progress` and has no `results.md`, the workflow surfaces a `execution_in_flight` stop signal before allowing any further action — prevents agents from silently skipping task closure in voice-chat workflows
- `grain onboard` now detects existing code modules and warns of code-ahead-of-backlog risk
  - `CodebaseScanner` detects top-level packages under `src/`, `lib/`, `app/`, and repo root; stored in `ScanResult.detected_modules`
  - `backlog.md` gains a "Retrospective Review Required" section listing detected modules when code is found, with explicit instructions to audit before treating the generated backlog as authoritative
  - `open_questions.md` adds a structured question surfacing detected modules and risk when code is ahead of backlog

### Fixed
- `grain onboard` now pre-populates canonical draft docs from existing repo content instead of leaving blank placeholders
  - `product_scope.md` pulls from README, `package.json` description, or `pyproject.toml` metadata
  - `architecture.md` pulls from existing `architecture.md`, `design.md`, or similar docs if found
  - Both fall back to clearly labelled placeholders when no source is available
- `open_questions.md` now surfaces a structured question listing all existing docs found outside the canonical layer, so maintainers know exactly what to incorporate
- `CodebaseScanner` extended with content extraction: reads README, architecture docs, scope/vision docs, `package.json`, and `pyproject.toml`; content capped at 2000 chars per file
- `ScanResult` gains `existing_doc_content` field (`dict[str, str]`) and `detected_modules` field (`list[str]`) carrying extracted content and module signals into the generator
- Draft marker changed from `# DRAFT` comment to HTML comment (`<!-- DRAFT — ... -->`) so it doesn't render as a heading
- `grain workflow loop` correctly routes `execution_in_flight` state: supervised mode stops with `supervision_required`, autonomous/gated modes invoke the executor so the agent can complete the task

---

## [0.1.7] — 2026-04-14

### Added
- `grain:` config block in `docs_manifest.yaml` — project-level defaults for `default_supervision`, `default_format`, `upgrade_check`, and `embedding_provider`
- `load_grain_config()` in `manifest.py` — reads the `grain:` block with safe defaults for any missing or invalid field
- `upgrade_check: warn` support — when set in project manifest, any `grain` command prints a one-line hint if Grain-managed files are stale
- `--format` now falls back to `grain.default_format` from project config when not passed as a CLI flag

### Fixed
- `PROJECT_RULES.md` §11 "Non-Goals for v1" replaced with a generic placeholder — the previous list described Grain's own non-goals, not the user's project
- `workflow_loop.yaml` — removed internal `Assay (FR-005)` reference; replaced `codex`/`gpt-5.4` example agent config with `claude`/`claude-opus-4-5` and clear comments that these should be customized
- `docs_manifest.yaml` template — `project.name: Grain` and `project.type: cli_toolkit` replaced with user-facing placeholders; `read_when: planning_v2` removed from adapter_profiles entry
- `phase.plan.next.md` — removed hardcoded references to Grain's internal `v2_plan.md`, `v2_adapters.md`, `v2_onboarding.md`; replaced with a generic instruction to read any planning docs declared in the manifest

---

## [0.1.6] — 2026-04-14

### Added
- `grain upgrade --diff` — shows unified diffs (red/green lines) for stale files without writing anything
- `grain upgrade --interactive` (`-i`) — walks each stale file, shows its diff, and prompts accept/skip/quit per file; only accepted files are written
- `grain upgrade --format json` now includes a `diffs` key with per-file diff strings when used with `--diff`

### Fixed
- Bundled `PROJECT_RULES.md` no longer contains "The project is a CLI-first toolkit..." — that line described Grain itself and was wrong in user project contexts
- Bundled `agent_profiles.md` no longer says "routing behavior for Grain" — changed to "for this project"

---

## [0.1.5] — 2026-04-13

### Added
- `grain upgrade` command — updates Grain-managed prompts, task templates, and safe runtime docs to the current installed version without touching user-owned files
  - `--dry-run` to preview what would change
  - `--format json` for machine-readable output
  - Never touches: canonical docs, working docs, task packets, `docs_manifest.yaml`, `adapter_profiles.md`

---

## [0.1.4] — 2026-04-13

### Added
- Wrapper prompts (`task.execute.md`, `task.review.md`, `task.close.md`, `task.plan.next.md`) now explicitly dispatch to their full implementation prompts — no more hollow stubs
- `docs/working/implementation_plan.md` is now seeded by both `grain init` and `grain onboard` — fixes missing file on first execute run
- `context.md` task template now includes an Adapter Context section (primary adapter, secondary adapters, rationale)
- `results.md` efficiency tracking fields now marked optional with `n/a` fallback for non-Grain projects

---

## [0.1.3] — 2026-04-13

### Added
- `grain onboard` now seeds runtime docs, task templates, and prompt files additively — existing project users get a fully functional Grain setup, not just directory stubs
- Codebase scanner now detects specialized project domains and suggests custom adapters in `open_questions.md`:
  - DevOps/infrastructure (Dockerfile, Terraform, HCL) → suggests `devops_adapter`
  - Data science (notebooks, parquet, HDF5) → suggests `data_adapter`
  - Mobile (Swift, Kotlin) → suggests `ios_adapter` / `android_adapter`
- `ScanResult` domain model gains `custom_adapter_hints` field

### Fixed
- `grain onboard` stub files used escaped newlines (`\\n`) instead of real newlines — stubs now render correctly
- Removed residual `forge` references from bundled runtime docs

### Changed
- README rewritten for clarity — tighter structure, added Why Grain section, agent CLI usage guidance
- README badges updated: PyPI version, Python versions, license, CI, downloads

---

## [0.1.2] — 2026-04-13

### Added
- Jupyter notebook (`.ipynb`) support — `NotebookExtractor` extracts markdown cells, code cells with outputs, and raw cells
- `.ipynb` added to `code_adapter` relevant file patterns
- Contributing / Feedback section added to README with GitHub Issues link

### Changed
- `export.py` renders `.ipynb` sources through `NotebookExtractor` alongside existing extractors

---

## [0.1.1] — 2026-04-12

### Fixed
- Bundled runtime, template, and prompt files are now correctly included in the PyPI package — `grain init` and `grain onboard` work after `pip install` or `uv tool install`
- PyPI project URLs corrected in `pyproject.toml`

---

## [0.1.0] — 2026-04-12

Initial public release.

### Included
- `grain init` — scaffold new projects with canonical, working, runtime, task, and prompt layers
- `grain onboard` — additive scaffold for existing repos with codebase scanning and draft doc generation
- `grain workflow next/run/loop` — state-driven workflow runner with supervised, gated, and autonomous modes
- `grain task create/list/show/next/prepare/validate/status` — task packet lifecycle management
- `grain context build/show/export` — minimal context assembly with graph-assisted source selection
- `grain docs validate` — doc manifest and structure validation
- `grain orchestrate scope/plan/accept` — orchestration proposals and plan ordering
- `grain adapter list/show` — adapter profile inspection
- `grain prompt show` — recommended prompt for current workflow state
- Adapters: `code_adapter`, `frontend_adapter`, `docs_adapter`, `spreadsheet_adapter`
- Extractors: `SpreadsheetExtractor`, `DocsExtractor`, `PdfExtractor`
- Tree-sitter knowledge graph for graph-assisted context selection
- Automated workflow loop with per-step logging and supervision levels
- PyPI publish workflow via GitHub Actions with OIDC trusted publishing
