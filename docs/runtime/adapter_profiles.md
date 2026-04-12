# Adapter Profiles

## 1. Purpose

This runtime document defines the v2 adapter profile contract for Forge.

Adapter profiles guide:
- context prioritization
- execution and validation hints
- review focus hints

## 1.1 Supported Adapter Inventory

Supported today:
- `code_adapter`
- `frontend_adapter`
- `spreadsheet_adapter`
- `docs_adapter`

Planned:
- `pdf extraction under docs_adapter`

Possible later:
- content-specific variants for editorial or knowledge-base systems
- additional project-specific adapters where reuse is justified

Adapter profiles must not change:
- packet lifecycle states
- review/close semantics
- canonical authority order

---

## 2. Contract Summary

### Required Fields

- `adapter_id`
- `domain_type`
- `applies_to` (at least one signal)

### Required Hint Presence

Each adapter profile must include at least one of:
- `context_priority_rules`
- `test_or_validation_hints`

Other hint sections are optional and may be empty.

---

## 3. Multi-Adapter and Fallback Rules

### Adapter Selection Shape

- packet metadata uses one `primary_adapter`
- packet metadata may include `secondary_adapters`

### Context Selection Defaults

- by default, prioritize `primary_adapter` hints only
- include `secondary_adapters` hints only when explicitly requested by task context or future CLI flags
- do not load all adapter hints by default

### No-Adapter Behavior

- when no adapter is declared, remain adapter-neutral
- do not infer an adapter during execution by default
- onboarding may recommend adapters, but execution remains explicit

---

## 4. Profile Structure

Each profile should follow this section structure:

- `adapter_id`
- `domain_type`
- `applies_to`
- `relevant_file_patterns`
- `ignore_file_patterns`
- `build_or_run_hints`
- `test_or_validation_hints`
- `review_focus_hints`
- `context_priority_rules`
- `default_model_bias`

---

## 5. Adapter Profiles

### code_adapter

- `adapter_id`: `code_adapter`
- `domain_type`: `code`
- `applies_to`:
  - Python
  - Rust
  - backend services
  - CLI tooling
- `relevant_file_patterns`:
  - `src/**`
  - `tests/**`
  - `pyproject.toml`
  - `Cargo.toml`
  - `Makefile`
- `ignore_file_patterns`:
  - `node_modules/**`
  - `dist/**`
  - `build/**`
- `build_or_run_hints`:
  - prefer project-native CLI entrypoints (`forge`, `python -m`, `cargo`, `make`)
  - keep execution local and deterministic
- `test_or_validation_hints`:
  - run focused tests before full suite
  - prefer explicit test files for changed modules
- `review_focus_hints`:
  - behavior regressions
  - state transition correctness
  - error handling and exit semantics
- `context_priority_rules`:
  - prioritize touched source files, then nearby tests
  - include only canonical/runtime docs needed for the current command family
  - **planned enhancement:** use tree-sitter import/call graph to select only structurally connected files rather than broad glob patterns — reduces context size and token cost without LLM overhead (applies across code_adapter, frontend_adapter, docs_adapter, devops_adapter; not applicable to spreadsheet_adapter)
- `default_model_bias`:
  - `open_model` for narrow edits
  - `frontier_model` for ambiguous or structural work

### frontend_adapter

- `adapter_id`: `frontend_adapter`
- `domain_type`: `frontend`
- `applies_to`:
  - TypeScript
  - JavaScript
  - React
  - Storybook
  - Tauri UI
- `relevant_file_patterns`:
  - `src/**/*.tsx`
  - `src/**/*.ts`
  - `src/**/*.jsx`
  - `src/**/*.js`
  - `*.css`
  - `*.scss`
  - `vite.config.*`
  - `next.config.*`
  - `storybook/**`
- `ignore_file_patterns`:
  - `coverage/**`
  - `dist/**`
  - `build/**`
  - snapshot or generated bundles unless debugging test drift
- `build_or_run_hints`:
  - prefer package-manager scripts declared by the repo
  - separate lint/typecheck/test/build when possible
- `test_or_validation_hints`:
  - include component or integration tests near changed views
  - verify desktop and mobile layout behavior when UI changes are included
- `review_focus_hints`:
  - UI regressions and interaction breakage
  - accessibility and responsive behavior
  - test coverage for changed interaction paths
- `context_priority_rules`:
  - prioritize modified UI modules and their co-located tests/styles
  - include design-system tokens/components before unrelated app areas
- `default_model_bias`:
  - `open_model` for scoped UI copy/layout fixes
  - `frontier_model` for larger interaction or architecture changes

### spreadsheet_adapter

- `adapter_id`: `spreadsheet_adapter`
- `domain_type`: `data`
- `applies_to`:
  - Excel spreadsheets
  - CSV datasets
  - tabular data review
- `relevant_file_patterns`:
  - `**/*.xlsx`
  - `**/*.xls`
  - `**/*.csv`
- `ignore_file_patterns`:
  - `node_modules/**`
  - `dist/**`
  - `build/**`
- `build_or_run_hints`:
  - treat extracted values as read-only context
  - validate data shape changes before downstream code updates
- `test_or_validation_hints`:
  - confirm header and row-count expectations
  - spot-check representative rows for schema drift
- `review_focus_hints`:
  - column additions/removals
  - row-shape or type inconsistencies
  - unintended delimiter or encoding changes in CSV
- `context_priority_rules`:
  - prioritize sheets with explicit headers first
  - include representative row content when datasets are large
- `default_model_bias`:
  - `open_model` for simple data formatting checks
  - `frontier_model` for schema-impact or cross-file reasoning

### docs_adapter

- `adapter_id`: `docs_adapter`
- `domain_type`: `docs`
- `applies_to`:
  - markdown documents
  - Word `.docx` documents
  - documentation-heavy repositories
- `relevant_file_patterns`:
  - `**/*.md`
  - `**/*.docx`
  - `**/*.pdf`
- `ignore_file_patterns`:
  - `node_modules/**`
  - `dist/**`
  - `build/**`
- `build_or_run_hints`:
  - treat extracted doc text as read-only context
  - preserve source-of-truth boundaries between canonical and working docs
- `test_or_validation_hints`:
  - verify critical headings and key requirement statements after edits
  - check table content for missing or reordered cells
- `review_focus_hints`:
  - requirement drift in heading/section changes
  - accidental deletion of acceptance criteria or constraints
  - table content regressions in structured docs
  - PDF extraction gaps for layout-heavy or image-only pages
- `context_priority_rules`:
  - prioritize canonical and requirements-bearing docs first
  - extract `.docx` headings, paragraphs, and table cells via docs extractor
  - treat PDF extraction as best-effort; include page-level no-text markers when needed
- `default_model_bias`:
  - `open_model` for scoped text edits and formatting checks
  - `frontier_model` for structural documentation refactors

---

## 6. Deferred Items

Deferred from P6-T01:
- provider CLI command mapping (for example `claude -p`, `codex -p`) remains outside `agent_profiles.md`
- dedicated provider runtime config location to be decided in a later phase
