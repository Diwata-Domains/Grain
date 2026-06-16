# Results: TASK-0187

## Summary
Added a lightweight `grain workflow explain` surface that turns the existing workflow evaluation into clearer operator guidance. The new command stays read-only and file-backed: it does not make workflow decisions itself, but it explains why Grain is blocked or what the next legal move should be and suggests the relevant follow-up commands.

## Files Changed
- `src/grain/services/workflow_diagnostics_service.py` — maps workflow stop reasons and next-action states into operator-facing diagnostics
- `src/grain/cli/workflow.py` — adds `grain workflow explain` in text and JSON forms
- `tests/test_workflow_explain_cmd.py` — covers actionable, blocked, and JSON diagnostic output
- `tests/test_command_groups.py` — registers the new workflow subcommand

## Verification
- `/Users/barbaricum/diwata-labs/.venv/bin/python -m pytest -q tests/test_workflow_explain_cmd.py tests/test_command_groups.py tests/test_workflow_next_cmd.py tests/test_workflow_state_service.py`
- `68 passed in 4.33s`

## User Review
- **State:** approved
- **Summary:** Approved to close and continue into the hardening smoke/closeout slice.
- **Resolution Mode:** close_task

### Required Fixes
- None

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- `P29-T05` should add smoke coverage and docs for the hardened operator loop.

### Residual Risks
- The diagnostic mapping is intentionally heuristic and only covers the current workflow gate vocabulary; new stop reasons will need explicit guidance as they are added.

## Verification Review
- **State:** not_run
- **Summary:** No external verifier configured for this workflow-hardening slice.

### Findings
- None

## Closure Decision
- **Decision:** closed
- **Reason:** Closed via grain task close.

### Closure Blockers
- None
