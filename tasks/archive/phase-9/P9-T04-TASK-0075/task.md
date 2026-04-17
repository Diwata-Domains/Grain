# Task: Implement orchestration service phase-level

## Metadata
- **ID:** TASK-0075
- **Status:** done
- **Phase:** Phase 9 — Orchestration Service Foundation
- **Backlog:** P9-T04
- **Packet Path:** tasks/P9-T04-TASK-0075/
- **Dependencies:** TASK-0074
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Extend orchestration service capabilities to phase-level planning by producing `OrchestratorPlan` proposals for phase shape drafts, dependency chains across packet candidates, and replan-oriented split recommendations.

## Why This Task Exists
After task-level orchestration (`P9-T03`), Phase 9 requires phase-level proposal generation so multi-packet phase shaping can be analyzed before CLI exposure and review-gate workflows.

## Scope
- Add a phase-level orchestration builder function in `src/grain/services/orchestration_service.py`.
- Generate packet-candidate chains, dependency links, and split recommendations from phase summary and optional explicit candidate titles.
- Add tests for phase-segment splitting, explicit candidate handling, and required-input validation.

## Constraints
- Outputs remain proposal-only (`OrchestratorPlan`) and must not mutate task packets/backlog directly.
- Keep behavior deterministic and local; no hidden state or remote lookups.

## Escalation Conditions
- If phase-level outputs require schema fields outside current `OrchestratorPlan` contract, stop and surface a proposal candidate.
- If adapter profile config is unavailable, return explicit error state rather than inferring adapters.
