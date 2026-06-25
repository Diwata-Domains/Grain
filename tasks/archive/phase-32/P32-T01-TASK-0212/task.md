# Task: Confirm grain suggest spec is locked (canonical)

## Metadata
- **ID:** TASK-0212
- **Status:** done
- **Phase:** Phase 32 — v0.4.0 Proactive Assistance
- **Backlog:** P32-T01
- **Packet Path:** tasks/P32-T01-TASK-0212/
- **Dependencies:** none
- **Primary Adapter:** docs
- **Secondary Adapters:** none

## Objective
Confirm the `grain suggest` contract is fully specified and locked before implementation begins. The spec already exists at `docs/canonical/suggest_spec.md` (authored in Phase 30, TASK-0196). This task is a verification gate, not new authorship.

## Why This Task Exists
P32-T02 (implement) and P32-T05 (workflow-next integration) both depend on a locked spec. The canonical spec defines the proposal model (`SUG-YYYYMMDD-NNN` in `docs/working/proposals/`), the two suggestion kinds (`pick-up`, `new-task`), the signal inputs, the approval gate, and `--format json` output.

## Scope / Implementation Steps
1. Read `docs/canonical/suggest_spec.md` end-to-end and confirm it covers: proposal storage location, ID format, suggestion kinds, signal inputs, accept/dismiss/prune lifecycle, and workflow-next integration.
2. Confirm no contradictions with `docs/working/archive_spec.md` (suggest-driven archive surfaces) or `docs/canonical/feedback_spec.md`.
3. Record confirmation in `results.md`; mark this packet done.

## Acceptance Criteria
- `docs/canonical/suggest_spec.md` exists, is marked canonical/locked, and covers all contract points above.
- No open questions block T02/T05 implementation.

## Tests
- No code; verification only. `results.md` cites the spec sections that satisfy each contract point.

## Constraints
- Do not edit canonical docs in this task — confirmation only.
- If the spec is found incomplete, raise an open question instead of silently amending canonical.

## Escalation Conditions
- Spec contradicts archive_spec.md or feedback_spec.md — stop and reconcile before T02.
