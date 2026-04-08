# Backlog

## 1. Purpose

This document is the execution inventory for `Forge`.

It contains:
- concrete implementation tasks
- grouped by phase
- default task status
- short execution-oriented descriptions

Status values used here:
- `draft`
- `ready`
- `in_progress`
- `blocked`
- `review`
- `done`

Default status for new backlog items in this file: `draft`

---

## 2. Phase 1 — Repository Foundation and Core CLI ✓ CLOSED
9 tasks done — archived to `tasks/archive/phase-1/`

---

## 3. Phase 2 — Documentation Registry and Validation ✓ CLOSED
9 tasks done — archived to `tasks/archive/phase-2/`

---

## 4. Phase 3 — Task Packet System ✓ CLOSED
13 tasks done — archived to `tasks/archive/phase-3/`

---

## 5. Phase 4 — Context Assembly and Model Routing ✓ CLOSED
13 tasks done — archived to `tasks/archive/phase-4/`

---

## 6. Phase 5 — Review, Handoff, and Hardening ✓ CLOSED
9 tasks done — archived to `tasks/archive/phase-5/`

---

## 8. Phase 6 — Adapter System Foundation (V2) ✓ CLOSED
7 tasks done — archived to `tasks/archive/phase-6/`

---

## 9. Phase 7 — New-Project Onboarding Flow ✓ CLOSED
7 tasks done — archived to `tasks/archive/phase-7/`

---

## 10. Phase 8 — Workflow Automation Runner Foundation

> **Status:** in_progress — P8-T01 through P8-T08 done; `workflow run` implemented. P8-T09 (harden outputs + integration tests) in review; P8-T10 blocked; P8-T11 draft.

### P8 Planning Notes
- Scope: state-driven workflow guidance and automation primitives for agents and operators
- Depends on: stable new-project onboarding artifacts and prompt surfaces from Phase 7
- Planning doc: `docs/working/v2_plan.md`
- Keep the first slice CLI-first and machine-readable; do not start TUI/GUI work in this phase

### P8-T01 — Lock minimal workflow automation slice and stop-condition rules
- **Status:** done
- **Description:** Resolve the first runner slice boundaries: what counts as the next legal step, where the runner must stop, how review and verification gates are surfaced, and which commands must return machine-readable outputs for agents/operators.
- **Files:** `docs/working/v2_plan.md`, `docs/working/backlog.md`, `docs/working/current_focus.md`, `docs/working/open_questions.md`
- **Model:** frontier_model
- **Dependencies:** P7-T06
- **Ready:** yes

### P8-T02 — Implement workflow state evaluator service
- **Status:** done
- **Description:** Add a service/domain layer that inspects repo state and determines the next legal workflow action, blockers, and stop conditions without mutating state.
- **Files:** `src/forge/services/` (new workflow service), `src/forge/domain/` (runner/state types), `tests/` (new service tests)
- **Model:** frontier_model
- **Dependencies:** P8-T01
- **Ready:** yes

### P8-T03 — Add `forge workflow next`
- **Status:** done
- **Description:** Add a CLI command that reports the next legal workflow step, current blockers, and the minimal follow-up action in both text and JSON forms.
- **Files:** `src/forge/cli/` (new workflow group), `src/forge/services/`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P8-T02
- **Ready:** yes

### P8-T04 — Add `forge task next`
- **Status:** done
- **Description:** Add a task-selection command that identifies the next actionable task packet candidate or reports that planning/splitting is required first.
- **Files:** `src/forge/cli/task.py`, `src/forge/services/`, `docs/working/backlog.md` (if task selection rules need clarification), `tests/`
- **Model:** frontier_model
- **Dependencies:** P8-T02
- **Ready:** yes

### P8-T05 — Add `forge phase next`
- **Status:** done
- **Description:** Add a phase-level command that reports whether phase planning, review, close, or no phase action is currently appropriate.
- **Files:** `src/forge/cli/` (workflow or phase surface), `src/forge/services/`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P8-T02
- **Ready:** yes

### P8-T06 — Add `forge task prepare`
- **Status:** done
- **Description:** Add a command that ensures packet/context/prompt prerequisites are assembled for one task and reports missing inputs without making hidden decisions.
- **Files:** `src/forge/cli/task.py` or `src/forge/cli/context.py`, `src/forge/services/`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P8-T02
- **Ready:** yes

### P8-T07 — Add `forge prompt show`
- **Status:** done
- **Description:** Add a command that surfaces the recommended stable prompt entrypoint for the current state plus required inputs, without making prompts the source of truth.
- **Files:** `src/forge/cli/` (prompt or workflow surface), `src/forge/services/`, `prompts/README.md`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P8-T01, P8-T02
- **Ready:** yes

### P8-T08 — Add `forge workflow run`
- **Status:** done
- **Description:** Add a guarded one-step runner that can execute one legal workflow action or stop with an explicit gate reason when human review, planning, or verification is required.
- **Files:** `src/forge/cli/` (workflow group), `src/forge/services/`, `tests/`
- **Model:** frontier_model
- **Dependencies:** P8-T03, P8-T04, P8-T05, P8-T06, P8-T07
- **Ready:** yes

### P8-T09 — Harden machine-readable automation outputs and runner integration tests
- **Status:** done
- **Description:** Ensure automation-relevant commands emit stable JSON and add integration coverage across `workflow next`, `task next`, `phase next`, `task prepare`, and `workflow run`.
- **Files:** `src/forge/cli/output.py`, `tests/` (new runner integration coverage), `docs/working/current_focus.md`
- **Model:** open_model
- **Dependencies:** P8-T03 through P8-T08
- **Ready:** after P8-T08

### P8-T10 — Define Forge-side verification bridge contract for Sentinel handoff
- **Status:** blocked
- **Description:** Define the minimal Forge command contract for verification submission/status/result ingestion so Sentinel can plug into the workflow runner once its surface exists.
- **Files:** `docs/working/v2_plan.md`, `docs/working/future_roadmap.md`, `docs/working/open_questions.md`
- **Model:** frontier_model
- **Dependencies:** P8-T01, FR-005 planning maturity
- **Ready:** blocked — after runner stop conditions and Sentinel bootstrap expectations are clearer

### P8-T11 — Add working-doc reconciliation checks for state drift
- **Status:** draft
- **Description:** Add a three-layer reconciliation approach for working-doc state so task/phase readiness, deferral notes, and current-focus guidance do not drift after task closeout or planning updates. The intended layers are: (1) manual close/review checklist expectations, (2) an explicit `forge workflow reconcile` command for detection and repair, and (3) runner-level validation that blocks or warns on inconsistent state before drift spreads.
- **Files:** `docs/working/backlog.md`, `docs/working/current_focus.md`, `docs/working/v2_plan.md`, `docs/working/open_questions.md`, `docs/working/workflow_metrics.md`
- **Model:** open_model
- **Dependencies:** P8-T01
- **Ready:** after P8-T01

---

## 11. Future — Adapter Context Selection (Post-Phase 8)

> **Status:** draft — not yet scoped into a phase. Record only; do not execute until adapter context selection is confirmed as the token bottleneck.

### FA-T01 — Tree-sitter dependency graph for adapter context selection

- **Status:** draft
- **Description:** Replace static glob-pattern context selection in adapters with a tree-sitter import/call graph pass. Parse the dependency graph of task-touched files locally (zero LLM tokens), then pass only structurally connected files into context assembly. Expected outcome: smaller context bundles, fewer tokens per execute stage, more precise file selection. Applicable to: `code_adapter` (Python, Rust, Go, Java), `frontend_adapter` (TypeScript, JavaScript, TSX, CSS), `docs_adapter` (Markdown link/reference graphs), `devops_adapter` (Bash, Dockerfile, HCL, YAML). Not applicable to `spreadsheet_adapter`.
- **Files:** `src/forge/adapters/adapter_config.py`, `src/forge/services/context_service.py`, `docs/runtime/adapter_profiles.md`
- **Model:** frontier_model
- **Dependencies:** stable Phase 8 context service, tree-sitter Python binding
- **Ready:** after Phase 8 context/workflow primitives are stable and adapter context selection is confirmed as the bottleneck
- **Reference:** Graphify (MIT) — tree-sitter + parallel subagent pattern; FR-011 (Token Efficiency)

---

## 7. Backlog Maintenance Rules

1. backlog items must remain concrete and implementable
2. backlog items should map to one or more future task packets
3. large backlog items may later be split before execution
4. backlog items must not redefine canonical rules
5. items that require canonical change should link to a proposal, not silently change scope
