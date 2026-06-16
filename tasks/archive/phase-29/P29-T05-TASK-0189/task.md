# Task: Hardening smoke tests and closeout docs

## Metadata
- **ID:** TASK-0189
- **Status:** done
- **Phase:** Phase 29 — Workflow Compliance Hardening
- **Backlog:** P29-T05
- **Packet Path:** tasks/P29-T05-TASK-0189/
- **Dependencies:** TASK-0184, TASK-0185, TASK-0186, TASK-0187
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
Close out the workflow hardening phase with focused smoke coverage and operator docs, including the backlog-parser edge that kept the final ready task hidden behind the phase-boundary gate.

## Why This Task Exists
Phase 29 is only complete if the long-session hardening work is covered by tests and documented in the surfaces operators and agents actually read. During closeout, the backlog parser exposed one more drift path: phase tasks at the end of a section could be overwritten by later non-phase headings. This task locks that down and updates the hardened operator loop docs.

## Scope
- Fix the backlog parser so non-phase sections do not overwrite the last task in the active phase.
- Add focused smoke coverage for the hardened workflow loop and diagnostic surface.
- Update README and runtime guidance to route blocked sessions through `grain workflow explain` and `grain workflow reconcile --dry-run`.

## Constraints
- Keep the hardening slice file-backed and incremental; do not introduce new background supervision.
- Do not expand beyond smoke coverage and docs closeout for the existing workflow surfaces.

## Escalation Conditions
- Stop if phase closeout requires redesigning the backlog model rather than tightening the current parser and guidance loop.
