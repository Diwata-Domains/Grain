# Current Focus

## Current Phase
Phase 12 — Automated Workflow Loop (seeded, planning-ready)

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
CLOSED. 4/5 tasks done (T01-T04). 577/577 tests passing. T05 (Homebrew formula) deferred by operator — resume when Homebrew tap/release flow is prioritized. Primary install paths are `pip install grain` and `uv tool install grain`. Phase closed 2026-04-11.

## Immediate Goals
1. Review `P12-T03` (`TASK-0092`) and close if accepted
2. Execute `P12-T04` (orchestrator/loop integration) after `P12-T03` close

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
- Homebrew formula exists at `contrib/homebrew/Formula/grain.rb` — deferred, not yet validated

## v0.1.0 Scope
- Phase 12 — Automated Workflow Loop ← active next
- Phase 13 — Existing Project Adoption (FR-013)
- Phase 14 — Document and Spreadsheet Adapters (Excel, docx, PDF)
- Cut v0.1.0 after Phase 14 closes

## Upcoming Phase Sequence
- **Phase 12** — Automated Workflow Loop (backlog §15) ← active next
- **Phase 13** — Existing Project Adoption (backlog §16, FR-013)
- **Phase 14** — Document and Spreadsheet Adapters (backlog §17, Excel/docx/PDF)
- **Phase 15+** — Semantic Enrichment, Ranking (v0.2.0, requires embedding infrastructure decision)
- **Phase 11-T05 (deferred)** — Homebrew formula, resume when tap/release flow is prioritized

## Active Constraints
- use local filesystem only
- preserve the stable v1 workflow as the core
- keep workflow automation narrow: one guarded step per runner invocation
- preserve machine-readable CLI outputs for all automation-relevant commands
- all orchestration outputs are proposals — no auto-creation of task packets
- keep intelligence-layer outputs deterministic, local-only, and proposal-only

## Do Not Work On Right Now
- P11-T05 Homebrew formula until tap/release flow is prioritized
- Assay (formerly Sentinel) implementation (v2 — FR-005)
- advisory/intelligence layer beyond what orchestration and Phase 10 define
- telemetry automation (v2 — FR-011)
- autonomous multi-step execution without explicit operator gate
- TUI/GUI implementation
- `grain workflow reconcile` CLI implementation (deferred — QD-01, scope in Phase 12+ planning)
