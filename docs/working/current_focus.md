# Current Focus

## Current Phase
Phase 10 — Structural Intelligence: Tree-sitter + Knowledge Graph (seeded, planning-ready)

## V1 Status
Complete. All 5 phases closed. 53 tasks done. 379 tests passing at v1 close.

## Phase 6 Status
CLOSED. All 7 tasks done. 399/399 tests passing. Adapter contract proven with `code_adapter`. Phase closed 2026-04-06.

## Phase 7 Status
CLOSED. All 7 tasks done. 419/419 tests passing. Delivered: onboarding prompt entrypoint, seed-file scaffolding, adapter-selection options, starter-packet bootstrap, and Phase 7 integration tests. Phase closed 2026-04-08.

## Phase 8 Status
CLOSED. All 11 tasks done. 494/494 tests passing (+75 new tests from Phase 7 close). Delivered: workflow state evaluator, forge workflow next/run, forge task next/prepare, forge phase next, forge prompt show, machine-readable JSON automation contract, runner integration tests, Sentinel bridge contract, working-doc reconciliation approach. Phase closed 2026-04-09.

## Phase 9 Status
CLOSED. All 7 tasks done. 561/561 tests passing (+67 new tests from Phase 8 close). Delivered: OrchestratorPlan domain model, adapter capability surface protocol, orchestration service (task-level + phase-level), grain adapter list/show, grain orchestrate scope/plan, OrchestratorPlan validator, integration tests. Proposal artifacts written to `docs/working/proposals/`. Phase closed 2026-04-11.

## Immediate Goals
1. Review `P10-T03` graph-assisted context selection and close if accepted
2. Proceed to `P10-T04` graph-aware orchestration adapter capability wiring after `P10-T03` close
3. Keep intelligence-layer outputs deterministic, local-only, and proposal-only

## After Phase 8 — Using the Runner with Agent CLIs

Phase 8 delivers a complete workflow automation runner. The intended operating pattern with an agent CLI (Claude Code, Codex, etc.) is:

**Daily loop:**
1. Run `forge workflow next --format json` to get the current state and next legal step
2. Feed that output into your agent CLI prompt — it tells the agent exactly what to do next and why
3. Agent executes the step (task execute, review, or close)
4. Run `forge workflow run` to execute one guarded step and stop at the next gate
5. At review/close gates: you review, approve, then continue

**Key commands available after Phase 8:**
- `forge workflow next` — next legal step + blockers (JSON-stable)
- `forge workflow run` — execute one step, stop at gates
- `forge task next` — which task to work on
- `forge task prepare` — assemble packet + context prerequisites
- `forge phase next` — whether phase action is needed
- `forge prompt show` — recommended prompt for current state

**What the runner does not yet do after Phase 8:**
- propose what work to create across multiple domains (that is Phase 9 — now done)
- select context using structural dependency graphs (that is Phase 10)

## After Phase 9 — Using the Orchestrator with Agent CLIs

Phase 9 delivers the orchestration service and adapter capability surface. The operating pattern expands:

**Planning with the orchestrator:**
1. Describe a piece of work: `grain orchestrate scope --scope "add payment integration"`
   - Agent CLI gets: which adapters are relevant, which domains are involved, likely cross-domain dependencies
2. Generate a draft plan: `grain orchestrate plan --scope "add payment integration"`
   - Produces an `OrchestratorPlan` in `docs/working/proposals/` — inspectable, reviewable
3. You review and approve the plan
4. Create packets from the approved candidates using `forge task create`
5. Hand back to the Phase 8 runner to drive each packet through the loop

**Key commands added in Phase 9:**
- `grain orchestrate scope` — adapter and domain signal analysis
- `grain orchestrate plan` — draft OrchestratorPlan proposal
- `grain adapter list` — show available adapter profiles
- `grain adapter show --id <adapter-id>` — show one adapter's full contract

## Upcoming Phase Sequence
- **Phase 10** — Structural Intelligence: Tree-sitter + Knowledge Graph (FR-015 Layers 1+3+4, backlog §13) ← active next
- **Phase 11** — Distribution and Global Install (FR-004b, backlog §14)
- **Phase 12** — Automated Workflow Loop (backlog §15)

## Active Constraints
- use local filesystem only
- preserve the stable v1 workflow as the core
- keep workflow automation narrow: one guarded step per runner invocation
- preserve machine-readable CLI outputs for all automation-relevant commands
- all orchestration outputs are proposals — no auto-creation of task packets
- resolve CP-009 (forge→grain rename) before canonical docs are out of sync with implementation

## Do Not Work On Right Now
- Phase 11+ before Phase 10 is closed
- Sentinel implementation (v2 — FR-005)
- advisory/intelligence layer beyond what reconcile and orchestration define
- telemetry automation (v2 — FR-011)
- autonomous multi-step execution without explicit operator gate
- TUI/GUI implementation
- `forge workflow reconcile` CLI implementation (deferred — QD-01, scope in Phase 10+ planning)
