# Task: Implement workflow state evaluator service

## Metadata
- **ID:** TASK-0062
- **Status:** done
- **Phase:** Phase 8 — Workflow Automation Runner Foundation
- **Backlog:** P8-T02
- **Packet Path:** tasks/P8-T02-TASK-0062/
- **Dependencies:** TASK-0061
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Implement a read-only workflow state evaluator that inspects current phase/task/backlog state and determines one next legal workflow action or an explicit stop reason, without mutating repository state.

## Why This Task Exists
`P8-T02` is the first implementation task after the Phase 8 boundary contract (`P8-T01`). It provides the service-layer decision engine required before CLI surfaces (`workflow next`, `workflow run`, `phase next`, `task next`) can be added safely.

## Scope
- Add workflow evaluation domain models for action/stop outputs.
- Implement a service that reads working docs + packet state and returns deterministic next-action decisions and stop conditions.
- Add focused service tests covering ready/blocked/review/planning/phase-boundary paths.

## Constraints
- Do not mutate task, backlog, or phase files during evaluation.
- Keep output aligned with the minimal Phase 8 contract (one-step, explicit stop reasons, machine-readable fields).

## Escalation Conditions
- If required workflow semantics conflict with canonical docs, stop and route through a change proposal.
- If phase/task state is ambiguous and cannot be resolved deterministically, return a stop reason instead of inferring hidden behavior.
