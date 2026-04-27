# Task: Add adapter system tests

## Metadata
- **ID:** TASK-0060
- **Status:** done
- **Phase:** Phase 6 — Adapter System Foundation (V2)
- **Backlog:** P6-T07
- **Packet Path:** tasks/P6-T07-TASK-0060/
- **Dependencies:** TASK-0059
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
Add adapter-system test coverage for adapter profile loading, packet metadata parsing with and without adapter fields, and context assembly behavior for active, inactive, and unknown adapter states.

## Why This Task Exists
Phase 6 requires end-to-end adapter contract confidence before phase-level review and closeout.

## Scope
- Add dedicated adapter-system tests in new files aligned to P6-T07.
- Validate adapter loader output shape and packet metadata compatibility paths.
- Validate context assembly adapter-neutral and unknown-adapter-safe behavior.
- Run focused adapter/context tests and full regression suite.

## Constraints
- Tests must not change runtime behavior; this packet is coverage-only.
- No-adapter behavior must remain adapter-neutral and backward compatible.

## Escalation Conditions
- If tests expose a contract mismatch that requires canonical doc changes, stop and route through change proposal flow.
- If adapter coverage reveals ambiguous expected behavior, record the ambiguity rather than inferring a new contract.
