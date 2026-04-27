# Handoff: TASK-0137

## Final State
`Treat completed current task state as non-active workflow state` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0137
- **Phase:** Phase 20 — Workflow Drift Remediation from Field Usage
- **Status:** review

### Outcome
- **Review Readiness:** blocked
- **User Review State:** pending
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Implemented the Phase 20 stale-current-task fix. `workflow next` no longer requires a separate reconcile pass before it can move past a completed task referenced in `current_task.md`; if the referenced packet is already `done`, the evaluator treats it as non-active for routing purposes. The change preserves existing blocked, review, and execution-in-flight behavior for real active tasks and keeps evaluation read-only.

## What Was Built
- Packet handoff support is ready.

## What Review Should Check
- - Confirm that leaving `current_task.md` stale but non-blocking in evaluator output is acceptable until reconcile/close cleanup runs.
- - Confirm no downstream command relies on `active_task_id` being preserved when the pointed packet is already `done`.
- 

## What Was Not Done
- [follow-up note, or "None"]

## Known Issues or Follow-ups
- [risk, or "None"]

## Files Changed
- - `src/grain/services/workflow_service.py` — normalized active task status from packet metadata and ignored stale done pointers during evaluation
- - `tests/test_workflow_state_service.py` — added stale done-pointer regression coverage
- 

## Reviewer Notes
- - Confirm that leaving `current_task.md` stale but non-blocking in evaluator output is acceptable until reconcile/close cleanup runs.
- - Confirm no downstream command relies on `active_task_id` being preserved when the pointed packet is already `done`.
- 

## Closeout Intake

### Open Questions To Log
- [question summary, or "None"]

### Proposal Candidates To Log
- [proposal summary, or "None"]

### Follow-Ups To Log
- [follow-up note, or "None"]
