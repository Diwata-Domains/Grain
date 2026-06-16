# Task: Add ranked impacted-file advisory signals

## Metadata
- **ID:** TASK-0120
- **Status:** done
- **Phase:** Phase 17 — Ranking and Decision Layer
- **Backlog:** P17-T05 — Add ranked impacted-file advisory signals
- **Packet Path:** tasks/P17-T05-TASK-0120/
- **Dependencies:** TASK-0118
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Apply the ranking layer to impacted-file advisory output so graph-derived impact candidates can also be semantically scored and returned with inspectable weighted breakdowns without changing the existing authoritative impact list.

## Why This Task Exists
Phase 17 needs one more real consumer of the ranking engine beyond context selection. The orchestration impact path already exposes proposal-only `affected_files`, so it is the right place to add ranked, inspectable file advice.

## Scope
- add a proposal-only impacted-file ranking helper
- attach ranked impact metadata to orchestration scope-signal payloads
- add focused tests for the ranking helper and orchestration payload

## Constraints
- preserve the existing `affected_files` contract as-is
- keep ranked impacted-file output advisory and inspectable

## Escalation Conditions
- impacted-file ranking requires changing the authoritative impact signal contract
- orchestration payload needs canonical CLI/contract changes before this advisory extension can land
