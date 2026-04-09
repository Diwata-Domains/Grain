# Task: Define OrchestratorPlan Domain Model

## Metadata
- **ID:** TASK-0072
- **Status:** in_progress
- **Phase:** Phase 9 — Orchestration Service Foundation
- **Backlog:** P9-T01
- **Packet Path:** tasks/P9-T01-TASK-0072/
- **Dependencies:** none
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective

Add the `OrchestratorPlan` dataclass and its supporting types (`PacketCandidate`, `CrossDomainDependency`) to `src/forge/domain/orchestrator.py`. All fields must conform to `data_contracts.md §18`. This is a pure domain model task — no service logic, no CLI changes.

## Why This Task Exists

Phase 9 builds the orchestration service. That service requires a stable domain model to produce and pass typed planning proposals through the Review/Gate Layer. Without this model, P9-T02 (adapter capability surface) and P9-T03 (orchestration service — task-level) have no types to work with.

## Scope
- Add `src/forge/domain/orchestrator.py` with `PacketCandidate`, `CrossDomainDependency`, `OrchestratorPlan`
- Export new types from `src/forge/domain/__init__.py`
- Add `tests/test_orchestrator_domain.py` with constructor and default-field tests

## Constraints
- Fields must match `data_contracts.md §18.2` exactly
- `OrchestratorPlan.status` must be validated against allowed values: `draft`, `under_review`, `accepted`, `rejected`, `deferred`
- All outputs are proposals — no state mutation logic belongs here
- Do not modify any canonical docs, CLI, or service files

## Escalation Conditions
- If `data_contracts.md §18` is ambiguous about a field type, stop and record the question rather than inferring

## Closure Requirements
- `results.md` and `handoff.md` filled
- Tests pass (no regressions)
- New domain types importable from `src/forge/domain`
