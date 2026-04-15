# Implementation Plan

## 1. Purpose

This document defines the execution sequence for building `Forge`.

It is derived from the canonical docs and is limited to:
- implementation sequencing
- phase objectives
- major deliverables
- dependencies between phases

It does not redefine:
- product scope
- architecture boundaries
- workflow semantics
- canonical data contracts

---

## 2. Execution Strategy

Build v1 in five phases.

Sequencing rule:
- finish the minimum stable foundation of each phase before expanding breadth
- prefer validation and inspectability before automation convenience
- keep Phase 1 and Phase 2 narrow so task packet execution can start early
- treat token efficiency as an execution-quality metric: reduce unnecessary context loads, retries, and artifact rewrites as the workflow stabilizes

---

## 3. Phase Breakdown

## Phase 1 — Repository Foundation and Core CLI ✓ CLOSED

### Objective
Establish the minimum runnable repository structure and CLI shell required to support the rest of the system.

### Major Deliverables
- base source tree under `src/forge/` ✓
- CLI entrypoint (Click, `forge` command) ✓
- command group scaffolding (all 6 groups, 18 subcommands) ✓
- repository root resolution (`adapters/filesystem.py`) ✓
- repository init command (`forge init`) ✓
- template directory structure and loader ✓
- CLI output formatting base (`CommandResult`, `--format text|json`) ✓
- exit code and error handling conventions (7 typed exceptions, exit codes 1–7) ✓
- initial test harness for CLI smoke checks (63 tests, subprocess smoke suite) ✓

### Output Focus
This phase should make it possible to:
- initialize a repo structure
- run a CLI command successfully
- establish a stable location for services, validators, adapters, and templates

### Dependencies
- depends only on canonical docs
- no upstream implementation dependencies

---

## Phase 2 — Documentation Registry and Validation ✓ CLOSED

### Objective
Implement manifest parsing and repository document validation.

### Major Deliverables
- docs manifest loader ✓ (TASK-0010)
- manifest schema validator ✓ (TASK-0011)
- document existence validator ✓ (TASK-0013)
- authority-aware document registry model ✓ (TASK-0012)
- docs validation CLI commands (`forge docs validate`) ✓ (TASK-0015)
- docs inspection command (`forge docs show`) ✓ (P2-T07-TASK-0016)
- validator test fixtures ✓ (P2-T09-TASK-0017)
- `forge docs index` baseline behavior ✓ (P2-T08-TASK-0018)

### Output Focus
This phase should make it possible to:
- load and validate `docs_manifest.yaml` from the CLI ✓
- inspect document metadata through CLI ✓
- detect missing or malformed required docs ✓

### Notes
- 154/154 tests passing at phase close
- CP-001/CP-002 applied: packet directory naming now uses `P<N>-T<NN>-TASK-####` consistently across runtime and canonical docs
- Q5 resolved: manifest primary, `docs_index.md` generated — unblocked and completed P2-T08
- Q4 resolved: parse ID, status, phase only from task.md metadata block

### Dependencies
- requires Phase 1 CLI foundation ✓

---

## Phase 3 — Task Packet System ✓ CLOSED

### Objective
Implement task packet creation, validation, and lifecycle state handling.

### Major Deliverables
- task ID generation ✓ (P3-T01-TASK-0019)
- packet templates ✓ (P3-T02-TASK-0020)
- packet directory creation ✓ (P3-T03-TASK-0021)
- `forge task create` ✓ (P3-T04-TASK-0022)
- `forge task list` ✓ (P3-T05-TASK-0023)
- `forge task show` ✓ (P3-T06-TASK-0024)
- packet status parser/updater ✓ (P3-T07-TASK-0025)
- `forge task status` ✓ (P3-T08-TASK-0026)
- packet file validation ✓ (P3-T09-TASK-0027)
- `forge task validate` ✓ (P3-T10-TASK-0028)
- closure validation rules ✓ (P3-T11-TASK-0029)
- `forge task close` ✓ (P3-T12-TASK-0030)
- packet lifecycle tests ✓ (P3-T13-TASK-0031)

### Output Focus
This phase should make it possible to:
- create a valid packet ✓
- move it through lifecycle states ✓
- validate whether a packet is execution-ready or closeable ✓

### Notes
- 272/272 tests passing at phase close
- Q4 resolved: parse ID, status, phase only from task.md metadata block
- Q9 resolved: plain markdown templates, simple string replace (no rendering engine)
- Exit code 5 (InvalidTransitionError) requires subprocess tests — established pattern for Phase 4+
- Metadata format: colon inside bold markers (`**key:**`) — enforced by `_METADATA_LINE` regex

### Dependencies
- requires Phase 1 CLI foundation ✓
- depends on Phase 2 contract/manifest validation for shared validation patterns ✓

---

## Phase 4 — Context Assembly and Model Routing ✓ CLOSED

### Objective
Implement minimal-context preparation and model-class selection support.

### Major Deliverables
- context selection service ✓ (P4-T01–T03)
- packet context bundle builder ✓ (P4-T04)
- context build/show/export commands ✓ (P4-T05–T07)
- model profile loader ✓ (P4-T08)
- model selection logic ✓ (P4-T09)
- `forge model show` / `select` / `escalate` ✓ (P4-T10–T12)
- context and routing tests ✓ (P4-T13)

### Output Focus
This phase should make it possible to:
- assemble task-local execution context ✓
- export context for external tools ✓
- map work to `open_model`, `frontier_model`, or `reviewer_model` ✓

### Notes
- 349/349 tests passing at phase close (77 new tests added)
- Rework count: 2 (T09 review cycle, T12 self-loop bug)
- First-pass success: 11/13
- CP-005 applied: placeholder command behavior now canonical
- CP-008 applied: ModelProfile fields aligned with v1 implementation
- Q11 resolved: no-tag context invocation defaults to `running_tasks`
- Major architectural additions this phase: layered subsystem model, proposal objects, advisory/intelligence layer, product ladder, open-core model

### Dependencies
- requires Phase 2 document registry ✓
- requires Phase 3 task packet system ✓

---

## Phase 5 — Review, Handoff, and Hardening ✓ CLOSED

### Objective
Complete the operational workflow with review support, handoff artifacts, and baseline reliability improvements.

### Major Deliverables
- review check command
- handoff generation/validation support
- summary command for packet state
- expanded validation coverage
- golden-path tests across init/docs/task/context/review flows
- CLI ergonomics cleanup

### Output Focus
This phase should make it possible to:
- review packet outputs consistently
- support packet closure and handoff
- run core v1 workflows with confidence

### Notes
- Phase 5 complete: 9/9 tasks done
- Phase 5 closed the v1 core workflow and enables promotion of v2 planning into scoped implementation work

### Dependencies
- requires Phases 1 through 4

---

## 4. High-Level Sequencing

Recommended sequence:

1. create runnable CLI shell
2. scaffold repository initialization
3. implement docs manifest loading and validation
4. implement packet creation and lifecycle handling
5. implement context selection and export
6. implement model routing
7. implement review/handoff support
8. harden with tests and CLI cleanup

---

## 5. Dependency Summary

### Hard Dependencies
- Phase 2 depends on Phase 1
- Phase 3 depends on Phase 1 and benefits from Phase 2
- Phase 4 depends on Phases 2 and 3
- Phase 5 depends on Phases 1 through 4

### Soft Dependencies
- test coverage should begin in Phase 1 and expand each phase
- template work begins in Phase 1 and evolves in Phases 2 and 3
- adapter boundaries should be established in Phase 1 even if full integration waits until Phase 4

---

## 6. Implementation Priorities

Priority order inside the plan:

1. CLI entrypoint and repository structure
2. manifest/document validation
3. task packet creation and validation
4. context assembly
5. model routing

---

## 7. Design Guardrails

Keep the working system minimal and non-duplicative.

Guardrails:
- each document layer should have one clear job
- working docs should guide execution, not restate canonical truth
- prompts should stay narrow and command-shaped
- add backlog items only for concrete work, not general concerns
- if a concern is about process or clarity rather than implementation, record it here instead of the backlog
- if prompt, runtime, or workflow-contract docs change mid-conversation, restart the relevant agent conversation instead of assuming context refreshed automatically

---

## 8. Out-of-Sequence Work to Avoid

Do not start these before their prerequisite phases are stable:
- advanced provider-specific integrations before Phase 4
- rich review automation before basic packet validation exists
- complex prompt systems before context export exists
- plugin abstractions before core flows are working
- database or service-backed state at any point in v1

---

## 9. Phase Completion Standard

A phase is complete when:
- its major deliverables exist
- the core CLI path for that phase works end-to-end
- its outputs are validated at least at a basic level
- downstream phases can proceed without reworking the phase foundation

---

## Phase 6 — Adapter System Foundation (V2) ✓ CLOSED

### Objective
Implement the minimal v2 adapter contract: adapter profiles runtime doc, loader, packet-level adapter field, and adapter hint wiring into context assembly and packet generation.

### Major Deliverables
- `docs/runtime/adapter_profiles.md` — human-readable adapter contract and initial `code_adapter` + `frontend_adapter` profiles
- Adapter domain model (`AdapterProfile`)
- Adapter profile loader/parser
- `primary_adapter` and optional `secondary_adapters` fields in task packet metadata
- Adapter hint wiring into context assembly (file-pattern biasing, context priority rules)
- Adapter hint wiring into packet context.md output (review and validation hints surface)
- Adapter tests covering loading, packet metadata, and context selection with/without adapter

### Output Focus
After this phase, Forge can operate with adapter-awareness:
- task packets can declare their domain
- context assembly can bias file selection toward the declared adapter
- review surfaces domain-specific hints
- no adapter declared = adapter-neutral behavior (safe degradation)

### Dependencies
- Phase 3 stable task packet contract ✓
- Phase 4 stable context assembly ✓
- v2_adapters.md planning doc ✓
- v2 readiness gates met (Phase 5 closed) ✓

### Sequencing Notes
- begin by resolving open planning questions in v2_adapters.md §9 (P6-T01)
- prove the adapter contract with code_adapter first, frontend_adapter second
- do not start onboarding flow work (Phase 7) until adapter contract is stable
- if packet metadata changes require a data_contracts.md update, capture as a change proposal before editing canonical docs

### Notes
- Phase 6 complete: 7/7 tasks done
- 399/399 tests passing at phase close (+20 new tests)
- Adapter contract proven with `code_adapter`; `frontend_adapter` profile exists as a starter but is implementation-deferred
- No canonical change proposals raised during Phase 6

---

## Phase 7 — New-Project Onboarding Flow ✓ CLOSED

### Objective
Implement the minimal onboarding flow for new projects: guided `forge init` with adapter selection, starter packet generation, and basic project scaffolding that uses the stable adapter contract from Phase 6.

### Major Deliverables
- Stable new-project onboarding prompt entrypoint with question-first intake and explicit adapter-selection inputs
- `forge init` scaffolding that creates baseline seed files from templates while preserving additive-only and dry-run behavior
- Adapter-selection support in onboarding initialization (`primary` + `secondary`) with runtime-profile-aware validation
- Optional starter task-packet bootstrap during onboarding to reduce time-to-first-execution
- Integration tests and user-facing docs updates proving the minimal new-project onboarding path end-to-end

### Output Focus
After this phase, a new project can be initialized with adapter-awareness from the start.

### Dependencies
- Phase 6 stable adapter contract ✓
- v2_onboarding.md planning doc

### Sequencing Notes
- Phase 7 initial backlog slice is seeded in `docs/working/backlog.md` (first ready task: `P7-T01`)
- `P7-T01` locks the minimal onboarding decisions in `docs/working/v2_onboarding.md`:
  - hybrid surface (prompt entrypoint + thin CLI support)
  - optional starter packet bootstrap (not mandatory by default)
  - provider-generic onboarding (no provider-specific branching in first slice)
  - existing-project adoption remains deferred in `P7-T07`
- scope narrowly: prove onboarding with one adapter before generalizing
- keep existing-project adoption flow implementation deferred until new-project onboarding is stable
- route any required canonical contract changes through `docs/working/change_proposals.md` before canonical edits

### Notes
- Phase 7 complete: 7/7 tasks done
- 419/419 tests passing at phase close (+20 new tests since Phase 6 close)
- New-project onboarding is proven with `code_adapter`; existing-project adoption remains deferred to future phase planning
- No canonical change proposals were required

---

## Phase 8 — Workflow Automation Runner Foundation ✓ CLOSED

### Objective
Implement a state-driven CLI layer that tells agents and operators the next legal workflow step, executes one guarded step per invocation, stops cleanly at review and verification gates, and emits stable machine-readable JSON for automation.

### Major Deliverables
- Workflow state evaluator service (`workflow_state_service.py`) ✓
- `forge workflow next` — next legal step + blockers ✓
- `forge workflow run` — guarded one-step runner ✓
- `forge task next` — deterministic task-selection surface ✓
- `forge task prepare` — packet/context prerequisite check ✓
- `forge phase next` — phase-level action surface ✓
- `forge prompt show` — recommended prompt for current state ✓
- Runner integration tests across all six automation commands ✓
- Sentinel bridge contract: `forge verify` command group in `cli_spec.md §6.9`, result payload schema + verification gate in `v2_plan.md §11` ✓
- Working-doc reconciliation approach: manual checklist + `forge workflow reconcile` spec (QD-01) ✓

### Notes
- Phase 8 complete: 11/11 tasks done
- 494/494 tests passing at phase close (+75 new tests from Phase 7 close)
- Machine-readable JSON contract stable across all six automation commands
- Sentinel bridge contract defined; FR-006 implementation target established
- No canonical change proposals raised except the explicitly scoped `cli_spec.md §6.9` addition (P8-T10)
- Phase closed 2026-04-09

### Dependencies
- Phase 7 stable new-project onboarding ✓

---

## Phase 9 — Orchestration Service Foundation ✓ CLOSED

### Objective
Implement the orchestration service (task and phase-level), adapter capability surface protocol, `OrchestratorPlan` domain model, and `orchestrate`/`adapter` CLI commands.

### Major Deliverables
- `OrchestratorPlan` domain model with `PacketCandidate` and `CrossDomainDependency` types
- Adapter capability surface protocol (`detect_scope`, `collect_context`, `analyze_impact`, `validate_changes`, `export_artifacts`, `suggest_followups`) with graceful degradation
- `orchestration_service.py` — task-level orchestration (scope detection, split recommendation, dependency identification)
- `orchestration_service.py` — phase-level orchestration (phase shape proposals, dependency chains, replan candidates)
- `grain adapter list` and `grain adapter show` commands
- `grain orchestrate scope` and `grain orchestrate plan` commands
- `OrchestratorPlan` validator and full integration tests

### Notes
- Phase 9 complete: 7/7 tasks done
- 561/561 tests passing at phase close (+67 new tests from Phase 8 close)
- OrchestratorPlan domain model and adapter capability surface in `src/forge/domain/`; orchestration service, adapter CLI, orchestrate CLI, and validator in `src/grain/` (see CP-009 for package rename tracking)
- Proposal artifacts written to `docs/working/proposals/` as inspectable JSON
- CP-009 applied: full product rename Forge → Grain, Sentinel → Assay (package, CLI, all docs, all source)
- CP-010 raised by closer and resolved: superseded by CP-009, no action required
- Phase closed 2026-04-11
- Roadmap reference: FR-014

### Dependencies
- requires Phase 8 workflow runner primitives ✓
- requires Phase 8 context assembly service ✓

---

## Phase 10 — Structural Intelligence: Tree-sitter + Knowledge Graph ✓ CLOSED

### Objective
Add deterministic structural intelligence: tree-sitter entity extraction, a JSON knowledge graph, and graph-assisted context selection to replace glob-pattern loading.

### Major Deliverables
- Tree-sitter structural entity extraction (functions, classes, imports, call sites) for code, frontend, docs, and devops adapters
- NetworkX knowledge graph builder — nodes for files, modules, classes, functions, packets, docs, adapters; typed edges; persisted as inspectable JSON artifact
- Graph-assisted context selection in `context_service.py` replacing glob patterns
- Graph wired into orchestration adapter capabilities (`detect_scope`, `analyze_impact`)
- Integration tests across full path: tree-sitter extraction → graph build → context selection → orchestration scope

### Notes
- Phase 10 complete: 6/6 tasks done (T01-T05 + T06 remediation)
- 575/575 tests passing at phase close (same count as T05 — T06 replaced T01's tests in-place)
- Phase 10 was reopened after initial close: T01 review accepted AST+pattern matchers as equivalent, but phase-level review determined tree-sitter spec was not satisfied; T06 remediation replaced extraction layer with proper tree-sitter bindings
- T06: 1 conversation restart during execute; all downstream graph/context/orchestration contracts unaffected
- Layer 1 extraction now uses tree-sitter for all supported languages; `parser = "none"` only for unsupported grammars
- Absorbs FA-T01 (tree-sitter proof-of-concept)
- Phase closed 2026-04-11
- Roadmap reference: FR-015, FR-011

### Dependencies
- requires Phase 9 orchestration service and adapter capability surface ✓

---

## Phase 11 — Distribution and Global Install ✓ CLOSED (T05 deferred)

### Objective
Make Grain installable globally by anyone. This is the public usability gate.

### Major Deliverables
- Finalized `pyproject.toml` packaging metadata (classifiers, license, homepage, keywords) ✓
- PyPI publish workflow (`pip install grain` from PyPI, GitHub Actions OIDC publish) ✓
- `uv tool install grain` verified and documented ✓
- Install verification and troubleshooting docs ✓
- Homebrew formula for macOS — deferred (P11-T05 blocked; resume when tap/release flow prioritized)

### Notes
- Phase 11 complete: 4/5 tasks done (T05 Homebrew deferred by operator)
- 577/577 tests passing at phase close (+2 new tests from Phase 10 close)
- Primary install paths active: `pip install grain`, `uv tool install grain`
- Homebrew path (P11-T05) deferred — no blocking external infrastructure available in-repo at phase time
- Phase closed 2026-04-11
- Roadmap reference: FR-004b

### Dependencies
- requires Phase 10 close (stable CLI surface, no further breaking changes expected) ✓

---

## Phase 12 — Automated Workflow Loop

### Objective
Eliminate manual conversation handoffs by automating the execute→review→close cycle. Allow per-stage configuration of which external agent and model to use.

### Major Deliverables
- Per-stage agent/model config (`workflow_loop.yaml` + CLI flag overrides); named shortcuts (`claude`, `codex`) and raw `command` mode
- Supervision level config: `supervised` (approve each action), `gated` (stop at review/close gates — default), `autonomous` (minimal stops, escalation-only)
- `grain workflow loop` command — drives full execute→review→close cycle, behavior varies by supervision level
- `--dry-run` mode, `--steps N` limit, structured per-step logging
- Loop safety guardrails and documentation (explicitly noting `autonomous` is unverified automation — Assay is the future verification layer)
- Orchestrator/loop integration — approved OrchestratorPlan feeds loop task ordering; `grain orchestrate accept` command; fallback to backlog order when no plan accepted

### Architectural boundary
- Loop handles *how to execute* workflow stages; orchestrator handles *what to build and how to structure it*
- Loop uses `grain workflow next` as its state machine; orchestrator is a separate planning layer
- These are decoupled — loop works fully without orchestrator; orchestrator integration (P12-T04) is additive

### Notes
- ✓ CLOSED. All 4 tasks done (TASK-0090 through TASK-0093). 595 tests passing at phase close (+18 from Phase 11 close).
- `grain workflow loop` implemented with supervised/gated/autonomous modes, --dry-run, 25-step cap, per-step logging
- `grain orchestrate accept --plan <id>` added; loop consults accepted plan for conflicting-ready task ordering
- No new safety infrastructure required — Phase 8 workflow gates are the stop points
- v0.1.0 scope

### Dependencies
- requires Phase 11 close (stable public install — loop is a user-facing feature) ✓
- requires Phase 8 workflow runner primitives ✓

---

## Phase 13 — Existing Project Adoption

### Objective
Give existing repos a first-class adoption path into Grain. Produce a usable draft canonical doc set in one agent-driven pass without overwriting anything.

### Major Deliverables
- `prompts/workflow.onboard.existing.md` — agent-driven prompt that scans repo structure, asks targeted follow-up questions, generates draft canonical docs
- `grain onboard` CLI command — scaffolds Grain directory structure into an existing repo additively (no overwrites)
- Auto-generated draft `product_scope.md`, `architecture.md`, and initial backlog from codebase signals
- Auto-generated `open_questions.md` entries for every gap or undocumented decision found
- Auto-generated `change_proposals.md` stubs for structural issues or canonical conflicts identified
- All generated docs marked `draft` — human review required before treating as canonical

### Task Sequence
- **P13-T01 (TASK-0094)** — `grain onboard` CLI + additive scaffold engine ← active
- **P13-T02 (TASK-0095)** — Codebase scanner service (`CodebaseScanner`, `ScanResult`)
- **P13-T03 (TASK-0096)** — Draft canonical doc generation from scan results
- **P13-T04 (TASK-0097)** — `workflow.onboard.existing.md` agent prompt
- **P13-T05 (TASK-0098)** — Phase 13 integration tests (≥ 15 tests)

### Notes
- ✓ CLOSED. All 5 tasks done (TASK-0094 through TASK-0098). 638 tests passing at phase close (+43 from Phase 12 close).
- `grain onboard` CLI + `OnboardService` scaffold engine — additive only, dry-run support, JSON/text output
- `CodebaseScanner` detects languages, applicable adapters, key files, CI config, existing docs
- `OnboardDocGenerator` writes draft canonical docs from scan results — all output marked `# DRAFT`
- `workflow.onboard.existing.md` prompt walks full adoption flow with mandatory CLI call steps
- Phase 13 integration tests: 16 new tests covering onboard, scanner, doc generator, and e2e flow
- Scan is additive only — never overwrites existing files
- Frontend codebases and existing backend projects are primary target use cases
- v0.1.0 scope
- Roadmap reference: FR-013

### Dependencies
- requires Phase 12 close ✓
- requires stable Phase 7 onboarding surfaces ✓

---

## Phase 14 — Document and Spreadsheet Adapters

### Objective
Make Grain context-aware for Excel, Word, and PDF files. Extract readable content from binary and formatted document types into the existing context assembly pipeline so agents can work with these files the same way they work with code and markdown.

### Major Deliverables
- `spreadsheet_adapter` — full profile in `adapter_profiles.md`; reads `.xlsx`, `.xls`, `.csv`; extracts sheet names, headers, cell data, and formula summaries via `openpyxl`
- `docs_adapter` — full profile in `adapter_profiles.md`; reads `.docx` and `.md`; extracts headings, paragraphs, and table content via `python-docx`
- PDF document reader — reads `.pdf`; extracts text content via `pdfplumber` (text-first PDFs) with graceful degradation for layout-heavy files
- Context assembly integration — all three feed extracted text into the existing context pipeline; file pattern rules wired into adapter profiles
- New dependencies declared in `pyproject.toml`: `openpyxl`, `python-docx`, `pdfplumber`
- Tests covering extraction, context selection, and graceful degradation for unsupported layouts

### Task Sequence
- **P14-T01 (TASK-0099)** — `spreadsheet_adapter`: `SpreadsheetExtractor`, openpyxl, adapter profile ← active
- **P14-T02 (TASK-0100)** — `docs_adapter`: `DocsExtractor`, python-docx, .docx + .md profile
- **P14-T03 (TASK-0101)** — PDF reader: `PdfExtractor`, pdfplumber, graceful degradation
- **P14-T04 (TASK-0102)** — Phase 14 integration tests (≥ 12 tests, mixed-type context bundles)

### Notes
- ✓ CLOSED. All 4 tasks done (TASK-0099 through TASK-0102). 662 tests passing at phase close (+24 from Phase 13 close). v0.1.0 scope complete.
- `SpreadsheetExtractor`: reads .xlsx, .xls, .csv via openpyxl; sheet names, headers, cell data, formula summaries
- `DocsExtractor`: reads .docx and .md via python-docx; headings, paragraphs, table content
- `PdfExtractor`: reads .pdf via pdfplumber; graceful degradation for layout-heavy files
- All three feed extracted text into existing context assembly pipeline; adapter profiles updated
- Phase 14 integration tests: 12 tests covering extraction, context selection, mixed-type bundles, graceful degradation
- Extraction is read-only — adapters never modify source files

### Dependencies
- requires Phase 13 close ✓
- requires stable Phase 4/10 context assembly service ✓

---

---

## Phase 15 — Semantic Enrichment Layer

### Objective
Replace static file-pattern context selection with scored, relevance-ranked candidate selection. Introduce an `EmbeddingProvider` protocol that supports four pluggable backends — BM25 (default, no deps), Ollama (local server), Local (sentence-transformers), and OpenAI (cloud API). Wire scoring into the existing context assembly pipeline.

### Background
Grain's current context selection uses tree-sitter graph edges and adapter file-pattern rules to build context bundles. This is structural — it understands shape but not meaning. A task about "authentication middleware" may miss semantically relevant files if they aren't directly linked in the graph or matched by file pattern.

The semantic layer adds relevance scoring: given the active task's objective, rank candidate files by how relevant they are to that task. BM25 covers keyword-based relevance (no new infrastructure). Ollama, Local, and OpenAI providers add embedding-based semantic similarity when the operator configures them.

The provider model follows the same pattern as `AdapterProfile` and `ModelProfile` — resolved from `grain.embedding_provider` in `docs_manifest.yaml`, gracefully degrades to BM25 if the configured provider is unavailable.

### Provider Summary

| Provider | Config value | Dependencies | Notes |
|----------|-------------|--------------|-------|
| BM25 | `none` (default) | none | Keyword scoring, always available, deterministic |
| Ollama | `ollama` | Ollama running at `localhost:11434` | Local server, no API key, recommended for local-first setups |
| Local | `local` | `sentence-transformers` (optional dep) | Downloads model on first use (~100–300MB), runs on CPU/GPU |
| OpenAI | `openai` | `openai` SDK + `GRAIN_OPENAI_API_KEY` env var | Cloud API, highest quality, per-call cost |

### Major Deliverables
- `EmbeddingProvider` protocol (`src/grain/domain/embedding.py`) — defines `score(query, candidates) -> list[ScoredCandidate]` interface
- `BM25Provider` — keyword scoring using TF-IDF, no new dependencies, always the fallback
- `OllamaProvider` — calls `http://localhost:11434/api/embeddings`, graceful degradation if server not running
- `LocalProvider` — `sentence-transformers` optional dependency, lazy model load on first use, graceful degradation if not installed
- `OpenAIProvider` — `openai` SDK optional dependency, reads `GRAIN_OPENAI_API_KEY`, graceful degradation if key absent
- `EmbeddingProviderResolver` — reads `grain.embedding_provider` from manifest config, instantiates correct provider, falls back to BM25 on any error
- Context service integration — scored candidates replace/augment the current glob-pattern candidate list in `context_service.py`
- `grain embedding show` command — reports active provider, reachability status, model in use, and whether fallback is active
- Integration tests covering all four providers, graceful degradation paths, and context selection with scoring

### Task Sequence

- **P15-T01** — `EmbeddingProvider` protocol, `ScoredCandidate` domain model, `EmbeddingProviderResolver`, config wiring
- **P15-T02** — `BM25Provider` — TF-IDF keyword scoring, no new deps, deterministic output
- **P15-T03** — `OllamaProvider` — local server integration, graceful degradation when server unreachable
- **P15-T04** — `LocalProvider` — sentence-transformers optional dep, lazy load, graceful degradation when not installed
- **P15-T05** — `OpenAIProvider` — openai SDK optional dep, env-var key, graceful degradation when key absent
- **P15-T06** — Context service integration — wire `EmbeddingProviderResolver` into `context_service.py`, scored candidates augment graph-assisted selection
- **P15-T07** — `grain embedding show` command — active provider, reachability, model, fallback status
- **P15-T08** — Phase 15 integration tests (≥ 16 tests across all providers, degradation paths, and context selection)

### Architectural Notes
- All providers implement the same `score(query: str, candidates: list[str]) -> list[ScoredCandidate]` interface — context service never knows which provider is active
- Scoring is additive and advisory — it reranks existing candidates, never invents new ones
- BM25 fallback is always silent — no warnings unless `--verbose` is passed
- Optional dependencies (`sentence-transformers`, `openai`) are not added to `pyproject.toml` core deps — they are extras or runtime-checked imports
- `OllamaProvider` uses `nomic-embed-text` as the default model; configurable via `grain.ollama_embedding_model` in manifest
- `OpenAIProvider` uses `text-embedding-3-small` as the default model; configurable via `grain.openai_embedding_model` in manifest

### Dependencies
- requires Phase 14 close (stable context assembly pipeline) ✓
- requires stable `load_grain_config()` from v0.1.7 ✓
- `grain.embedding_provider` config field already in place ✓

---

---

## Phase 16 — Adapter Write-Back

### Objective
Close the read→write loop for all currently supported extractors. Agents can read structured files via context; this phase lets them deliver changes back into those formats as a formal task output, gated behind task closure.

### Major Deliverables
- `SpreadsheetExtractor.write()` — applies row/cell changes back to `.xlsx` / `.csv` via `openpyxl`
- `DocsExtractor.write()` — applies paragraph, heading, and table updates back to `.docx` via `python-docx`
- `NotebookExtractor.write()` — applies cell content updates back to `.ipynb`
- Deliverable handler in `grain task close` — reads `deliverable_spec.md` for declared output type, routes to the correct writer
- Structured change format — shared schema agents use to declare changes (JSON patch-style: target file, target element, new content)
- `grain task close --apply-deliverable` flag — explicit opt-in to run write-back during closure
- Integration tests covering round-trip read→write for each supported format

### Task Sequence
- **P16-T01** — Define shared change schema and `WritableExtractor` protocol
- **P16-T02** — `SpreadsheetExtractor.write()` — xlsx/csv write-back with openpyxl
- **P16-T03** — `DocsExtractor.write()` — docx write-back with python-docx
- **P16-T04** — `NotebookExtractor.write()` — ipynb cell write-back
- **P16-T05** — Deliverable handler in `task_service.close_packet()` — detects declared deliverable type, dispatches to writer
- **P16-T06** — `grain task close --apply-deliverable` CLI flag
- **P16-T07** — Phase 16 integration tests (round-trip read→write for each format, invalid change handling, missing file graceful failure)

### Architectural Notes
- Write-back is strictly gated behind task closure — writers are never invoked mid-execution
- The change schema is agent-agnostic — any agent that can produce structured JSON can use it
- Writers validate the change schema before applying; bad schema returns a closure error, not a partial write
- `openpyxl` and `python-docx` are already in scope as optional deps (used by existing extractors); no new core dependencies
- PDF remains read-only — no write-back planned

### Dependencies
- requires Phase 14 close (stable context assembly pipeline) ✓
- requires existing extractor implementations (`SpreadsheetExtractor`, `DocsExtractor`, `NotebookExtractor`) ✓
- can run in parallel with Phase 15 (Semantic Enrichment) — no shared dependencies

---

## 10. Post-v1 Transition Planning

With Phase 5 closed, v2 items may now be promoted into active implementation when they are:
- concrete
- scoped
- dependency-ready

Rules:
- promote the smallest adapter-system slice first
- do not begin with broad onboarding automation
- do not run multiple major v2 workstreams in parallel until the adapter contract is proven
- continue routing canonical or runtime contract changes through change proposals when needed
- prefer CLI/state-runner primitives and machine-readable command outputs before interface-layer work
- do not begin TUI/GUI work before workflow automation runner primitives exist

v0.2.0 planning is active. See Phase 15 above and `docs/working/current_focus.md` for current status.

---

## 11. Phase Retrospective Rule

Use phase review and close to improve the system deliberately, not continuously at random.

At phase review or phase close, classify system-level findings into:
- `fix_now` — workflow bugs or drift that will likely harm the next task or next phase if left unresolved
- `batch_next_phase` — repeated friction, validator ideas, prompt cleanup, metrics cleanup, or ergonomics improvements that are real but not urgent
- `ignore` — one-off noise or issues not worth system change

Rules:
- apply `fix_now` items during phase close or immediately after if they block safe continuation
- record `batch_next_phase` items in working docs and create backlog items only when the work is already concrete and scoped
- do not create backlog work from general opinions alone
- route unresolved decisions to `open_questions.md`
- route canonical or runtime authority gaps to `change_proposals.md`
