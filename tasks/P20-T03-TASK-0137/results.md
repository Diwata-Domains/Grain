# Results: TASK-0137

## Packet State
- **Current Task Status:** in_progress
- **Review Readiness:** pending
- **Recommended Next Status:** review

## Files Changed
- `src/grain/services/workflow_service.py` — normalized active task status from packet metadata and ignored stale done pointers during evaluation
- `tests/test_workflow_state_service.py` — added stale done-pointer regression coverage

## Summary
Implemented the Phase 20 stale-current-task fix. `workflow next` no longer requires a separate reconcile pass before it can move past a completed task referenced in `current_task.md`; if the referenced packet is already `done`, the evaluator treats it as non-active for routing purposes. The change preserves existing blocked, review, and execution-in-flight behavior for real active tasks and keeps evaluation read-only.

## Test Results
2/2 targeted workflow test files passing. 29 targeted tests passed.

## Efficiency
<!-- Fill in at close. Use "n/a" for any field not applicable to your project or agent model. -->
<!-- Tokens: use exact count if your runtime exposes it; otherwise record "n/a". -->

### Execute
- **Prompt Runs:** n/a
- **Conversation Restarts:** n/a
- **Files Read (est.):** n/a
- **Tokens:** n/a
- **Notes:** Focused on the evaluator and focused workflow-state tests only.

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
- Confirm that leaving `current_task.md` stale but non-blocking in evaluator output is acceptable until reconcile/close cleanup runs.
- Confirm no downstream command relies on `active_task_id` being preserved when the pointed packet is already `done`.

## User Review
<!-- reviewer fills this section — executor must leave all fields below as-is -->
- **State:** approved
- **Summary:** Approved to continue.
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
- **State:** [not_run / pending / passed / failed / inconclusive / waived]
- **Summary:** [verifier fills, or "No verifier configured"]

### Findings
- [finding, or "None"]

## Closure Decision
<!-- closer fills this section during final closeout -->
- **Decision:** closed
- **Reason:** Closed via grain task close.

### Closure Blockers
- None

## Deliverable Checklist
- [x] Evaluator ignores stale `current_task.md` pointers to done packets
- [x] Blocked / review / in-progress behavior still passes focused regression coverage
- [x] Focused workflow tests passing
- [ ] Full test suite passing

## Blockers
Full-suite validation was not run in this turn; only the focused workflow-state and workflow-run tests were executed.
