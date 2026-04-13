# Changelog

All notable changes to grain-kit are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
Versioning: [Semantic Versioning](https://semver.org/)

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
