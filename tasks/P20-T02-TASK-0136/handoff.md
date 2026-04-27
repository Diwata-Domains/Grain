# Handoff: TASK-0136

## Final State
`Make task IDs globally monotonic across archived packets` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0136
- **Phase:** Phase 20 — Workflow Drift Remediation from Field Usage
- **Status:** review

### Outcome
- **Review Readiness:** blocked
- **User Review State:** pending
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Implemented the Phase 20 task-ID allocation fix. `next_task_id()` no longer looks only at top-level packet directories under `tasks/`; it now includes archived packet directories as well, so bare `TASK-####` identifiers remain globally monotonic after phase archiving. Added focused tests to confirm archived packets contribute to the next ID while archive container directories without task IDs are ignored.

## What Was Built
- Packet handoff support is ready.

## What Review Should Check
- - Confirm that using `rglob("*")` over `tasks/` is acceptable for current repository sizes and archive layout.
- - Confirm no command assumes task IDs can be reused after archive.
- 

## What Was Not Done
- [follow-up note, or "None"]

## Known Issues or Follow-ups
- [risk, or "None"]

## Files Changed
- - `src/grain/domain/packets.py` — changed `next_task_id()` to scan the full `tasks/` tree, including archived packet directories
- - `tests/test_task_id.py` — added archive-aware regression coverage
- 

## Reviewer Notes
- - Confirm that using `rglob("*")` over `tasks/` is acceptable for current repository sizes and archive layout.
- - Confirm no command assumes task IDs can be reused after archive.
- 

## Closeout Intake

### Open Questions To Log
- [question summary, or "None"]

### Proposal Candidates To Log
- [proposal summary, or "None"]

### Follow-Ups To Log
- [follow-up note, or "None"]
