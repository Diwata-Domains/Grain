# Current Focus

## Current Phase
Phase 21 — v0.3.0 Planning and Operator Surface Definition

v0.2.0 COMPLETE

## Phase 15 Status
CLOSED. All 6 tasks done (T01-T06). 775/775 tests passing. Delivered: `grain phase close` (hard lifecycle gate), `grain workflow run` auto-packet bootstrap, `grain workflow reconcile` (drift detection + --fix), Phase 15 integration tests, `AGENTS.md` generation (`grain init` / `grain onboard`), `grain phase archive`. Phase closed 2026-04-17.

## V1 Status
Complete. All 5 phases closed. 53 tasks done. 379 tests passing at v1 close.

## Phase 6 Status
CLOSED. All 7 tasks done. 399/399 tests passing. Adapter contract proven with `code_adapter`. Phase closed 2026-04-06.

## Phase 7 Status
CLOSED. All 7 tasks done. 419/419 tests passing. Delivered: onboarding prompt entrypoint, seed-file scaffolding, adapter-selection options, starter-packet bootstrap, and Phase 7 integration tests. Phase closed 2026-04-08.

## Phase 8 Status
CLOSED. All 11 tasks done. 494/494 tests passing (+75 new tests from Phase 7 close). Delivered: workflow state evaluator, grain workflow next/run, grain task next/prepare, grain phase next, grain prompt show, machine-readable JSON automation contract, runner integration tests, Assay bridge contract, working-doc reconciliation approach. Phase closed 2026-04-09.

## Phase 9 Status
CLOSED. All 7 tasks done. 561/561 tests passing (+67 new tests from Phase 8 close). Delivered: OrchestratorPlan domain model, adapter capability surface protocol, orchestration service (task-level + phase-level), grain adapter list/show, grain orchestrate scope/plan, OrchestratorPlan validator, integration tests. Phase closed 2026-04-11.

## Phase 10 Status
CLOSED. All 6 tasks done (T01-T05 + T06 remediation). 575/575 tests passing. Phase required reopening — T01 review accepted AST fallback; T06 replaced extraction layer with proper tree-sitter bindings. Phase closed 2026-04-11.

## Phase 11 Status
CLOSED. 4/5 tasks done (T01-T04). 577/577 tests passing. T05 (Homebrew formula) was intentionally dropped from the active release story. Primary install paths are `pip install grain-kit` and `uv tool install grain-kit`. Phase closed 2026-04-11.

## Phase 12 Status
CLOSED. All 4 tasks done (T01-T04). 595/595 tests passing (+18 new tests from Phase 11 close). Delivered: per-stage agent/model config (`workflow_loop.yaml`), `grain workflow loop` command, supervised/gated/autonomous supervision levels, --dry-run mode, 25-step cap, per-step logging, `grain orchestrate accept --plan <id>`, accepted-plan loop ordering for conflicting ready tasks. Phase closed 2026-04-10.

## Phase 13 Status
CLOSED. All 5 tasks done (T01-T05). 638/638 tests passing (+43 new tests from Phase 12 close). Delivered: `grain onboard` CLI + additive scaffold engine, `CodebaseScanner` (language/adapter/key-file/CI detection), `OnboardDocGenerator` (draft canonical docs from scan), `workflow.onboard.existing.md` prompt, Phase 13 integration tests (16 tests). Phase closed 2026-04-12.

## Phase 14 Status
CLOSED. All 4 tasks done (T01-T04). 662/662 tests passing (+24 new tests from Phase 13 close). Delivered: `SpreadsheetExtractor` (xlsx/xls/csv via openpyxl), `DocsExtractor` (docx + md via python-docx), `PdfExtractor` (pdf via pdfplumber, graceful degradation), context assembly integration, adapter profiles updated, Phase 14 integration tests (12 tests). Phase closed 2026-04-12. **v0.1.0 scope complete.**

## v0.1.x Patch Series Status
COMPLETE. Released v0.1.0 through v0.1.11. 713+ tests passing. PyPI published.
- v0.1.2 — Jupyter notebook support (NotebookExtractor)
- v0.1.3 — grain onboard seeding fixes, custom adapter hints
- v0.1.4 — hollow wrapper prompt fixes, implementation_plan seeding
- v0.1.5 — grain upgrade command
- v0.1.6 — grain upgrade --diff / --interactive, bundled doc content fixes
- v0.1.7 — grain: config block, upgrade_check wiring, bundled doc cleanup
- v0.1.8 — grain task close --quick, execution_in_flight gate, code-ahead-of-backlog detection
- v0.1.9 — review state hardening (needs_fix, structured review bundle, completion policy)
- v0.1.10 — grain task create --simple, stub detection in task prepare, bootstrap state fix
- v0.1.11 — tooling_notes structure, upgrade customization guard, empty-phase fix

## v0.2.0 Status
COMPLETE — Phases 15 through 19 are closed on `dev`. v0.2.0 implementation scope is complete as of 2026-04-22.

### Branching strategy (established 2026-04-16)
- `main` — release-only; no direct commits during v0.2.0 development
- `dev` — all v0.2.0 phase work; PR to main on release
- `hotfix` — v0.1.x patches only; PR to main after hotfix release

### Embedding infrastructure decision: RESOLVED (applies to Phase 16)
- `none` (BM25) — default, always available, no deps
- `ollama` — local server, recommended for local-first setups
- `local` — sentence-transformers, optional dep, downloads model on first use
- `openai` — cloud API, opt-in, requires `GRAIN_OPENAI_API_KEY`
- Config field: `grain.embedding_provider` in `docs_manifest.yaml` (already shipped in v0.1.7)

## Phase 20 Status
CLOSED. All 6 tasks done (P20-T01 through P20-T06). Delivered: review routing after execution artifacts exist, archived-packet-aware task IDs, done-task stale-pointer handling, terminal project-complete workflow state, safer upgrade behavior for customized repos, and packet-first guardrails across prompts and agent instructions. Phase closed 2026-04-23.

## Immediate Goals
1. Execute the locked v0.3.0 milestone contract on `dev`
2. Define the first TUI/operator slice, writable office-surface strategy, and desktop-app integration path
3. Make Obsidian support explicit before implementation starts
4. Ensure non-code artifact writes are reviewable through diffs, validators, and safety modes
5. Capture high-value reusable workflow recipes only if the core milestone lands cleanly

## v0.3.0 Contract
- Theme: `Operator Surface for Structured Knowledge Work`
- Core:
  - first usable TUI for workflow navigation and common actions
  - writable `.docx` and spreadsheet flows
  - reviewable non-code artifact changes with validators and safety modes
  - desktop invocation strategy for Claude-style MCP and Codex-style CLI usage
  - explicit Obsidian support shape
  - `database_adapter`
  - `crawler_adapter`
- Stretch:
  - reusable workflow recipes
  - richer TUI inspection surfaces
  - contract-freshness warnings
- Non-goals:
  - broad GUI beyond the first TUI slice
  - cloud/backend collaboration features
  - Sentinel work
  - broad new adapter expansion beyond office/document and Obsidian surfaces

## Writable Office Workflow
- Write modes:
  - `propose` by default
  - `apply` for explicit in-place updates
  - `export-as-new-file` for cautious comparison-first workflows
- Workflow rules:
  - every write belongs to an active task packet
  - every write emits a human-readable review surface before close
  - validators must pass before the artifact update is considered ready
- Artifact expectations:
  - `.docx` should surface structural/textual change summaries
  - spreadsheets should surface touched sheets, ranges, and formula-sensitive changes

## Desktop Integration Strategy
- Canonical surface: Grain CLI
- Codex-style path: direct CLI invocation
- Claude/Desktop-style path: thin local MCP wrapper over the same Grain actions
- ChatGPT/OpenAI app-style path: reuse the same shared tool contract through an MCP/app-server boundary
- Constraint: local-first, file-backed, compatible with the broader toolkit contract layer

## Obsidian Decision
- Shape: dedicated `obsidian_adapter`
- Why:
  - wiki-links are not generic markdown links
  - frontmatter and vault metadata affect safe edits
  - `.obsidian/` config, canvases, attachments, and daily-note conventions are vault-specific
- Boundary:
  - `docs_adapter` remains generic markdown/docx/pdf
  - `obsidian_adapter` owns vault-aware note workflows

## Future Adapter Direction
- `database_adapter` is in-scope for v0.3.0
- `crawler_adapter` is in-scope for v0.3.0 and is the preferred name over `scraping_adapter`

## Non-Code Review Model
- Every non-code write must emit a review bundle before close
- Review bundle minimum:
  - touched artifact paths
  - operation mode
  - structured change summary
  - validator results
  - residual risk notes when validation is partial
- Validators:
  - structure validators
  - reference validators
  - policy validators
- Grain must force `propose` or `export-as-new-file` instead of `apply` when risk is high or validation is partial

## Workflow Recipes
- Recipes are thin entrypoints over the normal packet/workflow model
- Initial v0.3.0 recipe targets:
  - update PRD or planning docs from source inputs
  - revise meeting or research notes
  - update spreadsheet or report artifacts
  - fix Obsidian vault links or metadata drift
  - plan a database schema or migration change
  - review crawler config, selector, or extraction-schema changes

## First TUI Slice
- Shape: thin terminal operator shell over the existing CLI and file-backed workflow
- Stack: Python + Textual
- Required views:
  - workflow dashboard
  - current task and phase view
  - backlog-by-phase list
  - packet artifact inspector
  - prompt preview
  - context bundle inspector
- Required actions:
  - launch execute/review/close flows
  - open packet artifacts and blockers
  - trigger safe review-oriented actions for non-code artifacts once those flows land
- Explicit deferrals:
  - embedded agent terminals
  - multi-project views
  - live collaboration
  - broad canonical editing UI
  - separate JS/TS or Electron-style TUI stack

## After Phase 8 — Using the Runner with Agent CLIs

Phase 8 delivers a complete workflow automation runner. The intended operating pattern with an agent CLI (Claude Code, Codex, etc.) is:

**Daily loop:**
1. Run `grain workflow next --format json` to get the current state and next legal step
2. Feed that output into your agent CLI prompt — it tells the agent exactly what to do next and why
3. Agent executes the step (task execute, review, or close)
4. Run `grain workflow run` to execute one guarded step and stop at the next gate
5. At review/close gates: you review, approve, then continue

**Key commands available after Phase 8:**
- `grain workflow next` — next legal step + blockers (JSON-stable)
- `grain workflow run` — execute one step, stop at gates
- `grain task next` — which task to work on
- `grain task prepare` — assemble packet + context prerequisites
- `grain phase next` — whether phase action is needed
- `grain prompt show` — recommended prompt for current state

## After Phase 9 — Using the Orchestrator with Agent CLIs

Phase 9 delivers the orchestration service and adapter capability surface:

- `grain orchestrate scope --scope "..."` — adapter and domain signal analysis
- `grain orchestrate plan --scope "..."` — draft OrchestratorPlan written to `docs/working/proposals/`
- `grain adapter list` / `grain adapter show --id <id>` — inspect adapter profiles

## After Phase 10 — Graph-Backed Intelligence

Phase 10 adds deterministic structural intelligence. Context selection is now graph-assisted:
- Every adapter source included in a context bundle has a traceable graph path
- Orchestration scope/impact signals consume graph-derived adapter data when available
- Graph artifacts are inspectable JSON, always rebuildable from source artifacts
- Extraction uses tree-sitter for all supported languages

## After Phase 11 — Global Install Ready

Phase 11 makes Grain installable globally. Active install paths:
- `pip install grain` — PyPI publish workflow in place (GitHub Actions, OIDC trusted publishing)
- `uv tool install grain` — verified, installs `grain` CLI into global tool path without venv
- `grain --version`, `grain init --help` — verified as install confirmation commands
- Homebrew is not part of the active release story; `pip` and `uv` are the supported install paths

## After Phase 12 — Automated Workflow Loop

Phase 12 delivers the full execute→review→close automation loop:
- `grain workflow loop` — drives the full cycle; stops at gates by default (`gated` mode)
- `docs/runtime/workflow_loop.yaml` — per-stage agent/model config
- Supervision levels: `supervised` (approve each action), `gated` (stop at review/close gates — default), `autonomous` (minimal stops, escalation-only)
- `--dry-run` mode, `--steps N` limit, structured per-step logging
- `grain orchestrate accept --plan <id>` — marks OrchestratorPlan proposals as accepted for loop ordering

## After Phase 13 — Existing Project Adoption

Phase 13 makes Grain adoptable by existing repos:
- `grain onboard [path]` — scaffolds Grain directory structure additively; skips existing files; dry-run mode; JSON/text output
- `CodebaseScanner` — detects languages, applicable adapters, key files (README, package.json, pyproject.toml, CI config), existing docs
- `OnboardDocGenerator` — writes draft `product_scope.md`, `architecture.md`, initial backlog, open_questions stubs from scan; all output marked `# DRAFT`
- `prompts/workflow.onboard.existing.md` — agent-driven full adoption flow prompt with mandatory CLI call steps

## After Phase 14 — Document and Spreadsheet Adapters

Phase 14 completes v0.1.0 by making Grain context-aware for binary/formatted document types:
- `SpreadsheetExtractor` — reads .xlsx, .xls, .csv via openpyxl; extracts sheet names, headers, cell data, formula summaries
- `DocsExtractor` — reads .docx and .md via python-docx; extracts headings, paragraphs, table content
- `PdfExtractor` — reads .pdf via pdfplumber; graceful degradation for layout-heavy files
- All three feed extracted text into existing context assembly pipeline via updated adapter profiles

## v0.2.0 Scope
All five phases must ship for v0.2.0 to close.

- **Phase 15** — Workflow Hardening and Automation (`grain phase close`, `grain workflow run` auto-packet, `grain workflow reconcile`) ✓ closed 2026-04-17
- **Phase 16** — Semantic Enrichment Layer (EmbeddingProvider protocol, BM25 + Ollama + Local + OpenAI providers, context scoring) ✓ closed 2026-04-21
- **Phase 17** — Ranking and Decision Layer (weighted candidate scoring, replaces static adapter priority rules, depends on Phase 16) ✓ closed 2026-04-21
- **Phase 18** — Data Adapter (richer .ipynb context, ML artifact patterns, .ipynb migrated from code_adapter) ✓ closed 2026-04-21
- **Phase 19** — Community Adapter Registry (`grain adapter install`, schema validation, discovery pipeline) ✓ closed 2026-04-22
- **Phase 11-T05 (deferred indefinitely)** — Homebrew formula remains out of scope unless distribution priorities change

## Upcoming Phase Sequence
1. **Phase 21** — v0.3.0 planning and operator surface definition ← active now
2. **Phase 22** — TUI foundation and workflow surfaces
3. **Phase 23** — writable office artifacts (`.docx`, spreadsheets)
4. **Phase 24** — desktop integrations and Obsidian support

## Active Constraints
- use local filesystem only
- preserve the stable v1 workflow as the core
- keep workflow automation narrow: one guarded step per runner invocation
- preserve machine-readable CLI outputs for all automation-relevant commands
- all orchestration outputs are proposals — no auto-creation of task packets
- keep intelligence-layer outputs deterministic, local-only, and proposal-only

## Branching Plan
- `main` — release-state and approved planning truth
- `dev` — v0.3.0 execution and planning refinement before coding starts
- `hotfix` — quick fixes to the released v0.2.x line only

## Do Not Work On Right Now
- Homebrew/tap distribution work unless release priorities change materially
- Assay — independent companion project, separate repo, not a Grain feature
- broad Phase 21 implementation before task planning is written
- telemetry automation (v2 — FR-011)
- autonomous multi-step execution without explicit operator gate
- broad GUI work beyond the first required TUI slice

Phase 15 closed: 2026-04-17 — 6 tasks done (grain-verified)

Phase 16 closed: 2026-04-21 — 8 tasks done (grain-verified)

Phase 17 closed: 2026-04-21 — 6 tasks done (grain-verified)

Phase 18 closed: 2026-04-21 — 6 tasks done (grain-verified)

Phase 19 closed: 2026-04-22 — 6 tasks done (grain-verified)

Phase 20 closed: 2026-04-23 — 6 tasks done (grain-verified)
