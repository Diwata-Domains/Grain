# Handoff: TASK-0185

## What Changed
- Added read-only drift blockers for missing active-task pointers and invalid packet/backlog mismatches
- Kept the drift rule narrow enough to tolerate legitimate backlog lag during normal status progression
- Added focused workflow-state coverage for the new blocker paths

## Verification
- `16 passed in 0.75s` via `tests/test_workflow_state_service.py`

## Review Focus
- Confirm the new blocker paths are narrow enough not to create false positives during normal task progression
- Confirm the error messages are actionable for operators who need to reconcile state mid-session

## Follow-Ups
- `P29-T03` should target the runner/template drift that still causes these blockers in the first place
