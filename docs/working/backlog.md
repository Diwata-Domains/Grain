# Backlog

## Purpose

This document is the execution inventory for Grain.

It contains:
- concrete implementation tasks
- grouped by phase
- task status
- short execution-oriented descriptions

Status values: `draft` | `ready` | `in_progress` | `blocked` | `review` | `done`

Default status for new backlog items: `draft`

---

## Phase 1 — Repository Foundation and Core CLI ✓ CLOSED
9 tasks done — archived to `tasks/archive/phase-1/`

---

## Phase 2 — Documentation Registry and Validation ✓ CLOSED
9 tasks done — archived to `tasks/archive/phase-2/`

---

## Phase 3 — Task Packet System ✓ CLOSED
13 tasks done — archived to `tasks/archive/phase-3/`

---

## Phase 4 — Context Assembly and Model Routing ✓ CLOSED
13 tasks done — archived to `tasks/archive/phase-4/`

---

## Phase 5 — Review, Handoff, and Hardening ✓ CLOSED
9 tasks done — archived to `tasks/archive/phase-5/`

---

## Phase 6 — Adapter System Foundation ✓ CLOSED
7 tasks done — archived to `tasks/archive/phase-6/`

---

## Phase 7 — New-Project Onboarding Flow ✓ CLOSED
7 tasks done — archived to `tasks/archive/phase-7/`

---

## Phase 8 — Workflow Automation Runner Foundation ✓ CLOSED
11 tasks done — archived to `tasks/archive/phase-8/`

Key deliverables: `grain workflow next`, `grain workflow run`, `grain workflow explain`, `grain task prepare`, `grain prompt show`, verify bridge contract.

---

## Phase 9 — Orchestration Service Foundation ✓ CLOSED
7 tasks done — archived to `tasks/archive/phase-9/`

Key deliverables: `grain orchestrate scope/plan/accept`, `grain adapter list/show`, `OrchestratorPlan` domain model.

---

## Phase 10 — Structural Intelligence: Tree-sitter + Knowledge Graph ✓ CLOSED
6 tasks done — archived to `tasks/archive/phase-10/`

Key deliverables: tree-sitter structural extraction, NetworkX JSON knowledge graph, graph-assisted context selection. Absorbed FA-T01.

---

## Phase 11 — Distribution and Global Install ✓ CLOSED
5 tasks done (T05 deferred) — archived to `tasks/archive/phase-11/`

Key deliverables: PyPI publish flow, `uv tool install grain-kit`, Homebrew formula scaffold (deferred).

---

## Phase 12 — Automated Workflow Loop ✓ CLOSED
7 tasks done — archived to `tasks/archive/phase-12/`

Key deliverables: `grain workflow loop --steps N`, loop stop-condition hardening, machine-readable automation outputs.

---

## Phase 13 — Existing Project Adoption ✓ CLOSED
8 tasks done — archived to `tasks/archive/phase-13/`

Key deliverables: `grain onboard` for existing repos, bootstrap state detection, onboarding prompt hardening.

---

## Phase 14 — Document and Spreadsheet Adapters ✓ CLOSED
7 tasks done — archived to `tasks/archive/phase-14/`

Key deliverables: `docs_adapter`, `spreadsheet_adapter`, `.docx` and `.xlsx` extraction, `data_adapter` scaffold.

---

## Phase 15 — Workflow Hardening and Automation ✓ CLOSED
Tasks done — archived to `tasks/archive/phase-15/`

Key deliverables: phase-close enforcement, `grain workflow reconcile --fix`, runner resilience improvements.

---

## Phase 16 — Semantic Enrichment Layer ✓ CLOSED
Key deliverables: embedding-based document and code search, semantic similarity scoring for context selection, provider-agnostic embedding support (`local`, `openai`, `none`).

---

## Phase 17 — Ranking and Decision Layer ✓ CLOSED
Key deliverables: scored and ranked context source selection, weighted evidence-backed selection replacing static adapter priority rules.

---

## Phase 18 — Data Adapter ✓ CLOSED
Key deliverables: `data_adapter`, richer `.ipynb` context (cell outputs, dataset references), `.parquet`/`.h5`/`.hdf5` file patterns.

---

## Phase 19 — Community Adapter Registry ✓ CLOSED
Key deliverables: `grain adapter install <source>`, community adapter registry foundation, `contrib/community_adapter_registry/` structure, schema validation in CI.

---

## Phase 20 — Workflow Drift Remediation ✓ CLOSED
Key deliverables: field-reported bug fixes from production Grain usage (Assay + Obsidian), `grain workflow reconcile` improvements, bootstrap state robustness.

---

## Phase 21 — v0.3.0 Planning and Operator Surface Definition ✓ CLOSED
Key deliverables: v0.3.0 milestone contract, TUI scope locked, office artifact write-back scoped, verification bridge scoped.

---

## Phase 22 — TUI Foundation and Workflow Surfaces ✓ CLOSED
Key deliverables: `grain tui` — Textual-based terminal operator shell, workflow dashboard, backlog-by-phase view, packet artifact inspector, prompt preview.

---

## Phase 23 — Writable Office Artifacts ✓ CLOSED
Key deliverables: `.docx` and spreadsheet `propose`/`export`/`apply` write modes, review bundles, structural validators, packet-scoped write safety.

---

## Phase 24 — Desktop Integrations and Obsidian Support ✓ CLOSED
Key deliverables: `obsidian_adapter`, vault note context selection via wiki-link graph, MCP wrapper surface.

---

## Phase 25 — Database Adapter ✓ CLOSED
Key deliverables: `database_adapter`, schema/migration/query context selection, migration risk review guidance.

---

## Phase 26 — Crawler Adapter ✓ CLOSED
Key deliverables: `crawler_adapter`, crawl config/selector/extraction context selection, robots and rate-limit review guidance.

---

## Phase 27 — Recipe Layer and Operator Ergonomics ✓ CLOSED
Key deliverables: recipe execution primitives, operator ergonomics improvements, `grain workflow explain` hardening.

---

## Phase 28 — Assay Verification Integration ✓ CLOSED
Key deliverables: `grain verify submit/status/ingest`, verification-aware review/close gating, `verification_request.json` and `verification_result.json` packet artifacts.

---

## Phase 29 — Workflow Compliance Hardening ✓ CLOSED
Key deliverables: workflow compliance checks, `grain workflow guard` stub, `PROJECT_RULES.md` hardening.

---

## Phase 30 — v0.4.0 Planning and Toolkit Boundary Definition ✓ CLOSED
14 tasks done (TASK-0190 through TASK-0203). Doc snapshot at `docs/archive/phases/phase-30/`.

Key deliverables: v0.4.0 milestone contract locked, `grain suggest` spec, enforcement model spec, scaffold audit, docs audit spec, archive spec, CLI ergonomics spec, branch policy spec, upgrade enforcement spec.

---

## Phase 31 — DX Hardening and v0.4.0 Foundation ✓ CLOSED
8 tasks done (TASK-0204 through TASK-0211). Shipped as v0.3.1. Doc snapshot at `docs/archive/phases/phase-31/`.

Key deliverables: `grain workflow guard`, `grain hooks install/list/remove`, `grain docs audit`, `grain archive`, `grain status`, `grain doctor`, `grain upgrade --add-missing`, `upgrade_policy` and `branch_policy` manifest blocks, 13 new scaffold templates, `workflow.resume.md` prompt, stop reason constants.

---

## Phase 32 — `grain suggest` and Proactive Assistance

> **Status:** ready to plan — this is the first v0.4.0 feature phase.

### P32 Notes
- `grain suggest` is the primary v0.4.0 deliverable
- Planning should produce a spec doc before task creation
- DX bugs from Phase 31 must be fully closed before feature work begins
- Phase 32 depends on stable archive and docs audit outputs from Phase 31

### P32-T01 — Write `grain suggest` spec
- **Status:** draft
- **Description:** Define the `grain suggest` command contract. Inputs: workspace state (open questions, doc gaps, backlog shape, recent closures). Outputs: ranked candidate tasks with draft context and plan seeds. Human approval gate: `grain suggest --accept <id>` promotes to a real packet; `grain suggest --prune` clears stale suggestions. Spec should cover output format, storage location, approval flow, and integration with `grain workflow next`.
- **Files:** `docs/working/suggest_spec.md` (new)
- **Model:** frontier_model
- **Dependencies:** none

### P32-T02 — Implement `grain suggest`
- **Status:** draft
- **Description:** Implement `grain suggest` from the spec. Core logic: read workspace state, score candidate task types, generate ranked suggestions with draft context/plan seeds, write to `.grain/suggestions.json`. `grain suggest --accept <id>` creates a packet from the suggestion. `grain suggest --prune` clears stale entries. `--format json` output.
- **Files:** `src/grain/services/suggest_service.py` (new), `src/grain/cli/suggest.py` (new), tests
- **Model:** frontier_model
- **Dependencies:** P32-T01

---

## Backlog Maintenance Rules

1. Backlog items must remain concrete and implementable
2. Backlog items should map to one or more future task packets
3. Large backlog items may be split before execution
4. Backlog items must not redefine canonical rules
5. Closed phases are collapsed to a stub entry — verbose task descriptions live in the task archive
