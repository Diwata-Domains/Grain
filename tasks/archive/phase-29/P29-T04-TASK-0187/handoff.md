# Handoff: TASK-0187

## What Changed
- added a new read-only `grain workflow explain` surface
- mapped common workflow stop reasons and actionable states to operator guidance
- added focused command coverage for text and JSON diagnostic output

## Verification
- `68 passed in 4.33s` via `tests/test_workflow_explain_cmd.py tests/test_command_groups.py tests/test_workflow_next_cmd.py tests/test_workflow_state_service.py`

## Review Focus
- Confirm the new diagnostic guidance is concrete enough to reduce manual redirection without inventing a second workflow engine
- Confirm the suggested commands stay aligned with the existing CLI contract

## Follow-Ups
- `P29-T05` should add smoke coverage and docs for the hardened operator loop
