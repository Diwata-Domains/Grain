# Deliverable Spec: TASK-0185

## Required Output

### New Files
- None

### Modified Files
- `src/grain/services/workflow_service.py` — add read-only misuse blockers for drift states
- `tests/test_workflow_state_service.py` — add focused coverage for the new drift blockers

## Acceptance Checklist
- [x] `workflow next` stops when backlog shows active work but `current_task.md` is unset
- [x] `workflow next` stops for clearly invalid active packet/backlog mismatches
- [x] legitimate blocked/review/done behaviors still pass
- [x] focused workflow-state tests pass
- [ ] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- New CLI command groups
- Runner activation fixes
- Broader operator diagnostics
