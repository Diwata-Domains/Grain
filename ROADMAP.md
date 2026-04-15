# Roadmap

This document outlines the planned direction for Grain. It is intentionally high-level — no release dates, no feature promises. It reflects current intent and will change as the project evolves.

---

## Now — v0.1.x (Active)

Stabilization and distribution quality. Each patch is small and targeted.

- `grain upgrade` — update Grain-managed prompts and templates in existing projects
- `grain upgrade --diff` / `--interactive` — review changes before applying
- `grain:` config block in `docs_manifest.yaml` — project-level defaults for supervision, format, upgrade checks
- Bundled runtime doc content fixes — removing Grain-specific language from files seeded into user projects
- Jupyter notebook (`.ipynb`) support via `code_adapter`
- Existing project adoption improvements (`grain onboard`)

---

## Next — v0.2.0

The intelligence and domain expansion release.

### Semantic Enrichment Layer
- Embedding-based document and code search to complement the tree-sitter knowledge graph
- Semantic similarity scoring for context selection — move beyond file-pattern matching
- Local-first: runs without a cloud provider when `embedding_provider: local` is set in project config
- Provider-agnostic: `local`, `openai`, or `none` via `grain.embedding_provider` in `docs_manifest.yaml`

### Ranking and Decision Layer
- Score and rank candidate context sources by relevance to the active task
- Replace static adapter priority rules with weighted, evidence-backed selection
- Depends on the Semantic Enrichment Layer

### Adapter Write-Back
Close the read→write loop for the currently supported extractors. Agents can already *read* structured files via context; write-back lets them deliver changes back into those formats as a formal task output.

- `SpreadsheetExtractor.write(changes)` — agent-produced row/cell changes applied back to `.xlsx` / `.csv`
- `DocsExtractor.write(changes)` — paragraph, heading, and table updates applied back to `.docx`
- `NotebookExtractor.write(changes)` — cell content updates applied back to `.ipynb`
- PDF remains read-only (no write-back planned)
- Deliverable handler in `grain task close` — routes structured agent output to the correct writer based on declared deliverable type in `deliverable_spec.md`
- Write-back is gated behind task closure, not mid-execution — changes only apply when the agent formally closes the task
- External app agents and embedded document assistants are treated as execution surfaces, not workflow authorities
- Grain remains the source of truth through task packets, review artifacts, and closure state
- Bridge app-native editing back into repo task packets so spreadsheet and document changes participate in the normal execute → review → close workflow

### Data Adapter
- First-class support for data science and ML workflows
- Richer `.ipynb` context: cell outputs, dataset references, model training artifacts
- File patterns: `.ipynb`, `.parquet`, `.h5`, `.hdf5`, `model_card.md`, `requirements.txt`
- `.ipynb` migrated from `code_adapter` to `data_adapter` as its primary home
- Suggested automatically by `grain onboard` when ML/data signals are detected in the repo

### Community Adapter Registry
- Discovery and distribution pipeline for community-contributed adapter profiles
- Adapter contract is already stable — community adapters follow the same schema as official adapters
- Tiers: **Official** (shipped with Grain), **Verified** (reviewed by maintainer), **Community** (PR-based, schema-validated)
- `grain adapter install <source>` — fetch and apply a community adapter from a URL or registry handle
- Automated schema validation in CI for community adapter PRs

### Homebrew Formula
- Deferred from v0.1.x — resume when the Homebrew tap and release flow is ready
- Install path: `brew install diwata-labs/tap/grain`

---

## Companion Project — Assay

Assay is an independent application built by the same team, using Grain as its own workflow system.

**What it is:** an independent verification layer for AI-assisted software builds. Where Grain orchestrates the build workflow, Assay verifies the output — running tests, checking contracts, and surfacing issues before a human reviews.

**How it relates to Grain:** Grain ships a bridge contract (`grain verify` command group stub and a result payload schema) that Assay will implement. The two are decoupled — Grain works fully without Assay, and Assay is useful beyond Grain-managed projects.

**Status:** planned. The bridge contract is defined. Assay is being scoped and built as a separate project in the same organization.

---

## Under Consideration

These are not committed. They represent directions that may become roadmap items once current work stabilizes.

- **`grain workflow reconcile`** — working-doc reconciliation CLI (currently a manual checklist step)
- **Multi-adapter cross-cutting task support** — tasks that span code, docs, and data domains simultaneously
- **TUI interface** — terminal UI for workflow state inspection; not before core CLI surface is stable
- **Telemetry and workflow metrics automation** — structured per-phase cost and quality tracking
- **Multi-user coordination** — explicitly out of scope for v1 and v2; may be revisited later

---

## Not on the Roadmap

These are explicit non-goals for the foreseeable future:

- GUI or web dashboard
- Database-backed state
- Cloud-hosted workflow execution
- Vendor lock-in to any specific AI provider
