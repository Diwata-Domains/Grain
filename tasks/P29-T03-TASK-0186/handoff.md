# Handoff: TASK-0186

## What Changed
- `workflow run` now hydrates auto-created packet templates instead of leaving raw placeholders behind
- activation now syncs packet and backlog status to `in_progress`
- added focused regression coverage for the bootstrap path

## Verification
- `55 passed in 1.27s` via `tests/test_workflow_run_cmd.py tests/test_runner_integration.py tests/test_workflow_state_service.py`

## Review Focus
- Confirm the bootstrap packet content is sufficiently usable without pretending to be task-specific implementation detail
- Confirm the activation sync does not create false positives for downstream workflow checks

## Follow-Ups
- `P29-T04` should explain the remaining blocked states more clearly when the workflow still stops
