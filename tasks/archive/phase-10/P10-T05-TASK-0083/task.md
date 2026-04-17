# Task: Add Phase 10 integration and graph rebuild validation

## Metadata
- **ID:** TASK-0083
- **Status:** done
- **Phase:** Phase 10 — Structural Intelligence: Tree-sitter + Knowledge Graph
- **Backlog:** P10-T05
- **Packet Path:** tasks/P10-T05-TASK-0083/
- **Dependencies:** TASK-0082
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add integration coverage for the full structural-intelligence path (structural extraction, graph build, context selection, orchestration scope signals) and validate graph rebuild determinism from source artifacts with no hidden state.

## Why This Task Exists
Phase 10 requires end-to-end validation that Layer 1, Layer 3, and Layer 4 cooperate correctly and that graph artifacts are always re-derivable from repository sources.

## Scope
- Add integration tests spanning extraction → graph → context → orchestration scope.
- Add graph rebuild validation proving artifacts are derivable from source inputs, independent of previously persisted proposal files.
- Update workflow/task artifacts and working docs for `P10-T05` execution.

## Constraints
- Keep all tests deterministic and local-only.
- Avoid new runtime behavior changes unless tests reveal a concrete defect.
- Do not modify canonical docs.

## Escalation Conditions
- If integration flow requires changing canonical contracts, stop and log a proposal candidate.
- If deterministic rebuild cannot be validated with existing graph service behavior, stop and record blocker details.
