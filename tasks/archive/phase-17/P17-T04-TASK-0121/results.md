# Results: TASK-0121

## Packet State
- **Current Task Status:** review
- **Review Readiness:** approved
- **Recommended Next Status:** done

## Files Changed
- `src/grain/services/task_advice_service.py` — added proposal-only ranked task-advice helper
- `src/grain/services/orchestration_service.py` — attached task-advice payload to orchestration scope output
- `tests/test_task_advice_service.py` — added eligible-pool and ranking coverage for task advice
- `tests/test_orchestration_service.py` — asserted task-advice payload presence
- `docs/working/open_questions.md` — recorded the Q17 resolution
- `docs/working/backlog.md` — re-scoped P17-T04 and unblocked P17-T06

## Summary
Implemented the Q17 resolution for Phase 17. Ranked next-task suggestions now live on a proposal-only surface through `orchestrate scope`, where the active phase’s currently eligible task pool is ranked against a supplied scope summary using the shared ranking engine. Authoritative `workflow next` and `task next` behavior remains unchanged.

## Test Results
20/20 targeted tests passing:
- `tests/test_task_advice_service.py`
- `tests/test_orchestration_service.py`
- `tests/test_ranking_service.py`
- `tests/test_imports.py`

## Efficiency
<!-- Fill in at close. Use "n/a" for any field not applicable to your project or agent model. -->
<!-- Tokens: use exact count if your runtime exposes it; otherwise record "n/a". -->

### Execute
- **Prompt Runs:** n/a
- **Conversation Restarts:** n/a
- **Files Read (est.):** n/a
- **Tokens:** n/a
- **Notes:** Implemented the advisory contract as an orchestration payload extension so no authoritative workflow commands needed modification.

### Review
- **Prompt Runs:** n/a
- **Conversation Restarts:** n/a
- **Files Read (est.):** n/a
- **Tokens:** n/a
- **Notes:** None

### Close
- **Prompt Runs:** n/a
- **Conversation Restarts:** n/a
- **Files Read (est.):** n/a
- **Tokens:** n/a
- **Notes:** None

## Review Notes
- Confirm ranking the eligible pool as `ready` first, otherwise `draft`, is the intended long-term advisory behavior.
- Confirm `orchestrate scope` is the right durable home for ranked task advice before adding any dedicated task-advice command.

## User Review
<!-- reviewer fills this section — executor must leave all fields below as-is -->
- **State:** approved
- **Summary:** Ranked next-task suggestions now exist on an advisory surface without disturbing authoritative workflow selection.
- **Resolution Mode:** close_task

### Required Fixes
- None

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None

### Residual Risks
- None

## Verification Review
<!-- verifier fills this section when applicable; otherwise leave defaults -->
- **State:** not_run
- **Summary:** No verifier configured

### Findings
- None

## Closure Decision
<!-- closer fills this section during final closeout -->
- **Decision:** closed
- **Reason:** Closed via grain task close.

### Closure Blockers
- None

## Deliverable Checklist
- [x] ranked task advice scores only the currently eligible phase task pool
- [x] advisory task suggestions are exposed on a proposal-only surface
- [x] `workflow next` and `task next` remain unchanged
- [x] All new tests passing
- [ ] Full test suite passing with no regressions, or any unrun coverage explicitly noted in `results.md`
- [x] review bundle complete in `results.md` and `handoff.md`

## Blockers
None.
