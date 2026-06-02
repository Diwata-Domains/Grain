# Results: TASK-0175

## Summary
Added packet-local task observability with a new `grain task observe` command, active-task workflow-next reporting, and automatic runner/close action recording.

## Files Changed
- `src/grain/services/task_observability_service.py` — added packet-local observability read/update service
- `src/grain/cli/task.py` — added `task observe` and close-hook metadata updates
- `src/grain/cli/workflow.py` — surfaced active-task observability in text and JSON output
- `src/grain/services/workflow_run_service.py` — recorded activation workflow actions
- `tests/test_task_observe_cmd.py` — added task observability command coverage
- `tests/test_workflow_next_cmd.py` — added active-task observability reporting coverage
- `tests/test_workflow_run_cmd.py` — added activation observability coverage

## Verification
- `/Users/barbaricum/diwata-labs/.venv/bin/python -m pytest -q tests/test_task_observe_cmd.py tests/test_workflow_next_cmd.py tests/test_workflow_run_cmd.py`
- `25 passed in 0.93s`

## User Review
- **State:** approved
- **Summary:** Observability surface is acceptable for the first Phase 27 slice.
- **Resolution Mode:** close_task

### Required Fixes
- None

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- Consider surfacing `observability.json` inside the TUI packet inspector during `P27-T03`.

### Residual Risks
- The first slice records only Grain-known workflow actions plus explicit operator updates; external agent activity still depends on `grain task observe` calls.

## Verification Review
- **State:** passed
- **Summary:** Focused CLI and workflow tests passed for the new observability slice.

### Findings
- None

## Closure Decision
- **Decision:** closed
- **Reason:** Closed via grain task close.

### Closure Blockers
- None
