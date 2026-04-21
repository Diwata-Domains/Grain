# Handoff: TASK-0121

## Final State
`Add ranked next-task advisory signals` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0121
- **Phase:** Phase 17 — Ranking and Decision Layer
- **Status:** review

### Outcome
- **Review Readiness:** ready
- **User Review State:** approved
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Implemented the Q17 resolution for Phase 17. Ranked next-task suggestions now live on a proposal-only surface through `orchestrate scope`, where the active phase’s currently eligible task pool is ranked against a supplied scope summary using the shared ranking engine. Authoritative `workflow next` and `task next` behavior remains unchanged.

## What Was Built
- Packet handoff support is ready.

## What Review Should Check
- - Confirm ranking the eligible pool as `ready` first, otherwise `draft`, is the intended long-term advisory behavior.
- - Confirm `orchestrate scope` is the right durable home for ranked task advice before adding any dedicated task-advice command.
- 

## What Was Not Done
- None

## Known Issues or Follow-ups
- None

## Files Changed
- - `src/grain/services/task_advice_service.py` — added proposal-only ranked task-advice helper
- - `src/grain/services/orchestration_service.py` — attached task-advice payload to orchestration scope output
- - `tests/test_task_advice_service.py` — added eligible-pool and ranking coverage for task advice
- - `tests/test_orchestration_service.py` — asserted task-advice payload presence
- - `docs/working/open_questions.md` — recorded the Q17 resolution
- - `docs/working/backlog.md` — re-scoped P17-T04 and unblocked P17-T06
- 

## Reviewer Notes
- - Confirm ranking the eligible pool as `ready` first, otherwise `draft`, is the intended long-term advisory behavior.
- - Confirm `orchestrate scope` is the right durable home for ranked task advice before adding any dedicated task-advice command.
- 

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None
