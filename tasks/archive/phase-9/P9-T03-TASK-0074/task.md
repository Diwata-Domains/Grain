# Task: Implement orchestration service task-level

## Metadata
- **ID:** TASK-0074
- **Status:** done
- **Phase:** Phase 9 — Orchestration Service Foundation
- **Backlog:** P9-T03
- **Packet Path:** tasks/P9-T03-TASK-0074/
- **Dependencies:** TASK-0072, TASK-0073
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Implement a task-level orchestration service that analyzes a work scope, detects relevant adapters, proposes packet candidates and dependency links, and returns an `OrchestratorPlan` proposal without mutating packets/backlog.

## Why This Task Exists
Phase 9 requires orchestration planning before CLI surfaces can expose `forge orchestrate scope/plan`. This service is the core proposal generator those commands depend on.

## Scope
- Add `src/grain/services/orchestration_service.py` for task-level plan generation.
- Use adapter profiles and capability protocol (`detect_scope`) for adapter relevance signals with graceful degradation.
- Generate `OrchestratorPlan` proposals including `active_adapters`, `packet_candidates`, `dependency_links`, `cross_domain_flags`, and `split_recommendations`.
- Add focused tests for single-domain, multi-domain, no-signal fallback, missing-config, and empty-scope error paths.

## Constraints
- Orchestration outputs are proposals only; no task packet creation or workflow state mutation.
- Service must degrade gracefully when no adapter signals are found.

## Escalation Conditions
- If canonical orchestration contract fields are missing or contradictory, stop and raise a change-proposal candidate.
- If adapter profile runtime config is missing or invalid, return explicit service error state instead of implicit defaults.
