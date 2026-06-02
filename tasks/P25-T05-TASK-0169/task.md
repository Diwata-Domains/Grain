# Task: Database smoke tests, docs, and closeout

## Metadata
- **ID:** TASK-0169
- **Status:** done
- **Phase:** Phase 25 — Database Adapter
- **Backlog:** P25-T05 — Database smoke tests, docs, and closeout
- **Packet Path:** tasks/P25-T05-TASK-0169/
- **Dependencies:** TASK-0166, TASK-0167, TASK-0168
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add the final smoke coverage and closeout artifacts for the first database adapter slice so Phase 25 ends with an integrated proof that schema, migration, query, repository, and review-guidance surfaces work together inside the packet-first Grain model.

## Why This Task Exists
Phase 25 now has the contract, context behavior, and review guidance for `database_adapter`, but the phase is not complete until those surfaces are validated together through a small smoke slice and recorded in the phase closeout artifacts.

## Scope
- add one integrated database adapter smoke test covering export behavior across schema, migration, query, and repository surfaces
- complete the packet and phase-closeout artifacts for the database adapter phase

## Constraints
- keep this task as closeout and validation work; do not introduce new database features
- preserve the CLI-first, packet-first, file-backed workflow boundary throughout the smoke slice and closeout docs

## Escalation Conditions
- if the closeout requires broader database runtime tooling or feature expansion rather than validation and documentation, stop and keep the slice narrow
