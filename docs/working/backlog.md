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

## Phase 32 — v0.4.0 Proactive Assistance

> **Status:** ACTIVE — 10 tasks (P32-T01–P32-T10). v0.4.0 feature phase; scope reframed 2026-06-24 to a focused Proactive Assistance release (toolkit/recipe/apply moved to v0.5.0 — see `v0.5.0_contract.md`).

### P32 Notes
- v0.4.0 scope: grain suggest, phase close archiving, archive show, workflow next integration, grain notes full, workflow metrics, Pulse telemetry foundation, GitHub feedback (report + publish), docs hygiene
- T01 (spec) is satisfied by the canonical `docs/canonical/suggest_spec.md` → **done**
- T02 (implement) and T05 (workflow next integration) build on the locked spec
- T03, T06, T07, T08, T10 are independent and can run in parallel
- T09 depends on T06 (grain notes full implementation)
- T10 (docs hygiene) is founder-requested; fixes current_focus drift + adds an audit check
- Phase 31 is fully closed; no DX blockers remain

### P32-T01 — Write `grain suggest` spec
- **Status:** done (satisfied by canonical `docs/canonical/suggest_spec.md`)
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

### P32-T03 — Extend `grain phase close` to auto-archive task packets
- **Status:** ready
- **Description:** When a phase is closed, automatically move all `tasks/P{N}-*` packet directories to `tasks/archive/phase-{N}/` alongside the existing doc snapshot. Behavior: (1) detect all packet dirs matching the phase prefix in `tasks/`; (2) create `tasks/archive/phase-{N}/` if absent; (3) move packets; (4) update `docs/archive/phases/phase-{N}/metadata.json` with `tasks_done` count and `tasks_archive` path. Add `--keep-tasks` flag to skip the move when a packet is being carried forward to the next phase.
- **Files:** `src/grain/services/phase_service.py`, `src/grain/services/archive_service.py`, `src/grain/cli/phase.py`, tests
- **Model:** frontier_model
- **Dependencies:** none

### P32-T04 — Extend `grain archive show` to surface packet list from task archive
- **Status:** ready
- **Description:** `grain archive show --phase N` currently shows doc snapshot content. Extend it to also list the task packets in `tasks/archive/phase-{N}/` from the `tasks_archive` field in `metadata.json`. Output: phase metadata, doc snapshot files present, packet list with task ID and title (read from `task.md`). `--format json` output. If no task archive exists for a phase (pre-v0.4.0 close), surface the metadata note gracefully.
- **Files:** `src/grain/cli/archive.py`, `src/grain/services/archive_service.py`, tests
- **Model:** frontier_model
- **Dependencies:** none

### P32-T05 — Integrate `grain suggest` into `grain workflow next`
- **Status:** draft
- **Description:** When `grain workflow next` evaluates the workspace and finds no obvious next task (e.g. `stop_reason: no_ready_tasks` or `backlog_empty`), automatically run the suggest engine and surface the top candidate in the workflow next output. Text output: inline suggestion block. JSON output: `suggestion` field with candidate. Does not write anything — suggestion is surface-only until `grain suggest --accept <id>` is called.
- **Files:** `src/grain/services/workflow_service.py`, `src/grain/services/suggest_service.py`, tests
- **Model:** frontier_model
- **Dependencies:** P32-T01, P32-T02

### P32-T06 — `grain notes` full implementation
- **Status:** ready
- **Description:** Graduate `grain notes` from write-only stub to a queryable, actionable friction inbox. (1) Structured rows in `tooling_notes.md` with `id`, `type`, `status`, `created_at`, `body`; (2) `grain notes list` with `--type` and `--status` filters and `--format json`; (3) `grain notes show <id>` — full note detail; (4) `grain notes resolve <id>` — mark addressed with optional resolution note; (5) open notes with type `bug` or `friction` surface as `low`-severity findings in `grain docs audit`; (6) `grain notes add` improvements — auto-assign incremental ID, timestamp, default status `open`.
- **Files:** `src/grain/services/notes_service.py` (new), `src/grain/cli/notes.py` (extend), `src/grain/services/docs_audit_service.py` (extend), tests
- **Model:** frontier_model
- **Dependencies:** none

### P32-T07 — Workflow metrics — `grain metrics` command
- **Status:** ready
- **Description:** Implement `grain metrics` for per-phase velocity and cost tracking. Reads task archive and docs archive to compute: (1) phase duration (open → close dates from metadata); (2) task count per phase; (3) stop-reason frequency from `.grain/last_workflow_state.json` history; (4) `grain metrics --phase N` for single-phase detail; (5) `grain metrics export` dumps full history as JSON. Writes `.grain/metrics_cache.json` with a 1-hour TTL. `--format json` output on all subcommands.
- **Files:** `src/grain/services/metrics_service.py` (new), `src/grain/cli/metrics.py` (new), tests
- **Model:** frontier_model
- **Dependencies:** none

### P32-T08 — Pulse telemetry foundation — opt-in event emission contract
- **Status:** ready
- **Description:** Lay the Grain-side event emission contract for Pulse (the planned Diwata-wide telemetry layer). (1) Define a `TelemetryEvent` dataclass with `event_type`, `version`, `timestamp`, `payload` fields; (2) implement `telemetry_service.py` with a `emit(event)` method — fire-and-forget, never raises, logs to `.grain/telemetry_queue.jsonl` when endpoint is unreachable; (3) instrument key workflow moments: phase close, task close, `grain suggest --accept`, stop reason on `grain workflow next`; (4) opt-in via `telemetry.enabled: true` in `docs_manifest.yaml` or `GRAIN_TELEMETRY_ENDPOINT` env var; (5) no telemetry emitted unless explicitly enabled — default is off. Transport and aggregation are Pulse's responsibility; Grain only emits.
- **Files:** `src/grain/services/telemetry_service.py` (new), `src/grain/domain/telemetry.py` (new), instrumentation in phase/task/workflow/suggest services, tests
- **Model:** frontier_model
- **Dependencies:** none

### P32-T09 — `grain notes publish` — GitHub issue submission from CLI
- **Status:** draft
- **Description:** Extend `grain notes` with a `publish` subcommand that submits a note directly to GitHub Issues. (1) `grain notes publish <id>` — formats the note as a GitHub issue (title from note body first line, body from full note + metadata); (2) applies appropriate label from note type (`bug` → `bug`, `friction`/`feature` → `enhancement`); (3) GitHub repo configurable in `docs_manifest.yaml` under `github.repo`; (4) token via `GRAIN_GITHUB_TOKEN` env var — never stored in workspace files; (5) prints the created issue URL on success; (6) `grain issue create --title "..." --type bug|feature|friction` as a standalone path that skips the notes log and goes straight to GitHub.
- **Files:** `src/grain/services/github_service.py` (new), `src/grain/cli/notes.py` (extend), `src/grain/cli/report.py` (new), `src/grain/cli/issue.py` (new), tests
- **Model:** frontier_model
- **Dependencies:** P32-T06
- **Note:** implements BOTH the canonical URL-based `grain report` (no token, browser-confirmed, upstream) and the API-based `grain notes publish` (token, headless, files into the user's own repo — the path a familiar/agent can drive without a browser).

### P32-T10 — Docs hygiene — phase_status_consistency audit check + current_focus rewrite
- **Status:** ready
- **Description:** Founder-requested hygiene. (1) Rewrite `docs/working/current_focus.md` from 377 lines of self-contradicting per-phase prose to a single Current Phase block + Closed-Phase Ledger; (2) add a `phase_status_consistency` check to `grain docs audit` (error severity) that fires when a phase is described as both active and closed, or when the Current Phase appears in the closed ledger; (3) document the check in `docs_audit_spec.md`.
- **Files:** `src/grain/services/docs_audit_service.py` (extend), `docs/working/current_focus.md` (rewrite), `docs/working/docs_audit_spec.md` (extend), tests
- **Model:** frontier_model
- **Dependencies:** none

---

## Backlog Maintenance Rules

1. Backlog items must remain concrete and implementable
2. Backlog items should map to one or more future task packets
3. Large backlog items may be split before execution
4. Backlog items must not redefine canonical rules
5. Closed phases are collapsed to a stub entry — verbose task descriptions live in the task archive
