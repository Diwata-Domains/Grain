# Changelog

All notable changes to grain-kit are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
Versioning: [Semantic Versioning](https://semver.org/)

---

## [0.1.11] — 2026-04-16

### Added
- `grain upgrade` now seeds missing working docs added in later Grain versions (`tooling_notes.md`, `workflow_metrics.md`) — existing projects get them on next upgrade without overwriting anything
- `grain upgrade` now detects locally customized Grain-managed files (user-added content in prompts/templates) and warns before overwriting with a prompt to use `--interactive`; `customized` field added to JSON output
- `grain workflow next` now distinguishes a phase with no tasks defined yet (`stop_reason: phase_has_no_tasks`) from a completed phase awaiting close (`phase_boundary_review_close_required`)
- `grain workflow next` tips updated: suggests `grain task create` when a ready backlog task has no packet yet

### Changed
- `tooling_notes.md` now has structured columns: `Type` (`bug | friction | question | note`) and `Status` (`open | addressed | wontfix | escalated`) — enables Assay to triage entries later
- `grain upgrade` always computes diffs internally to power customization detection; diffs only surfaced in output when `--diff` or `--interactive` is passed

---

## [0.1.10] — 2026-04-15

### Added
- `grain task create --simple`: minimal packet mode (task.md + results.md only) for small mechanical tasks; sets `Mode: simple` in task metadata so `grain task prepare` skips planning file requirements
- `docs/working/tooling_notes.md` bundled in every onboarded project: lightweight agent-writable inbox for mid-session workflow friction and tool observations (pre-formatted markdown table)
- `docs/working/workflow_metrics.md` now created by `grain onboard` — was missing, causing `docs validate` to fail on freshly onboarded repos

### Changed
- `grain task prepare` now detects stub planning files: if `context.md`, `plan.md`, or `deliverable_spec.md` still contain `TASK-####` template placeholders, they are reported as `stub packet file: <name>` and block `ok` status
- `grain task prepare` outputs a tip suggesting the execute prompt when stub files are detected — non-blocking, user choice
- `grain onboard` no longer triggers the managed-file upgrade staleness hint: suppressed for `onboard` invocations since files are seeded fresh from the current bundled version
- `grain workflow next` now returns `stop_reason: bootstrap_incomplete` with `recommended_prompt: prompts/workflow.onboard.existing.md` after fresh onboarding, instead of a hard parse error
- `docs/working/current_task.md` onboard stub now uses machine-parseable bootstrap fields (`Task ID: none / Task Path: none / Status: unset`) instead of prose placeholder
- `docs/working/current_focus.md` onboard stub now includes `Phase 0 — Bootstrap` marker so the workflow engine parses it cleanly
- `prompts/workflow.onboard.existing.md` now documents the two-phase onboarding boundary and expected bootstrap-state outputs

### Fixed
- `docs validate` no longer fails immediately after `grain onboard` due to missing `workflow_metrics.md`
- `grain workflow next` no longer hard-errors on bootstrap state after fresh onboarding
- Managed-file drift warnings no longer appear at the top of `grain onboard` output

---

## [0.1.9] — 2026-04-14

### Added
- first-class review hardening for conversational workflows:
  - `needs_fix` packet state in the seeded manifest and task lifecycle contract
  - structured `User Review`, `Verification Review`, and `Closure Decision` sections in `results.md`
  - explicit completion-policy fields for user approval and optional verification gating
- review and handoff services now surface `user_review_state` and `verification_state` as first-class output fields

### Changed
- seeded runtime manifests now define the stable close policy explicitly:
  - `require_user_approval: true`
  - `require_verification_pass: false`
  - `allow_close_when_verification_not_run: true`
- task templates and bundled prompts now use the structured review bundle instead of the older `Review Intake` wording
- `grain task close --quick` now writes a closure-ready structured review bundle compatible with the stricter completion policy

### Fixed
- closure, review, and handoff flows now agree on the same review-state model instead of mixing legacy prose-only review fields with newer parser logic
- bundled docs and canonical data-contract docs now document `needs_fix` and the expanded completion policy expected by the stable runtime

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
