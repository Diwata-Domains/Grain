# Handoff: TASK-0135

## Final State
`Route executed tasks to review instead of execute` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0135
- **Phase:** Phase 20 — Workflow Drift Remediation from Field Usage
- **Status:** review

### Outcome
- **Review Readiness:** blocked
- **User Review State:** pending
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Implemented the Phase 20 review-routing fix. Grain no longer reports `task_execute` for an active in-progress task once `results.md` exists. Instead, workflow evaluation now surfaces an explicit `task_review` action with `prompts/task.review.md`, and the runner treats that state as a human/reviewer gate. Regression tests were updated to reflect the intended Execute -> Review -> Close lifecycle.

## What Was Built
- Packet handoff support is ready.

## What Review Should Check
- - Verify that introducing `task_review` does not break any downstream command assumptions that only knew `task_execute`, `task_planning`, or `task_close`.
- - Decide whether `task_review` should become a first-class documented workflow action in canonical docs during a follow-up task.
- 

## What Was Not Done
- [follow-up note, or "None"]

## Known Issues or Follow-ups
- [risk, or "None"]

## Files Changed
- - `src/grain/services/workflow_service.py` — route active tasks with `results.md` to `task_review`
- - `src/grain/services/workflow_run_service.py` — gate `task_review` as a human/reviewer step
- - `tests/test_workflow_state_service.py` — added evaluator coverage for review routing
- - `tests/test_workflow_run_cmd.py` — updated old execute assertion and added review-gate coverage
- - `tests/test_prompt_show_cmd.py` — added review-prompt selection coverage
- - `tests/test_runner_integration.py` — added cross-command regression coverage
- 

## Reviewer Notes
- - Verify that introducing `task_review` does not break any downstream command assumptions that only knew `task_execute`, `task_planning`, or `task_close`.
- - Decide whether `task_review` should become a first-class documented workflow action in canonical docs during a follow-up task.
- 

## Closeout Intake

### Open Questions To Log
- [question summary, or "None"]

### Proposal Candidates To Log
- [proposal summary, or "None"]

### Follow-Ups To Log
- [follow-up note, or "None"]
