# Deliverable Spec: TASK-0182

## Required Output

### New Files
- None

### Modified Files
- `src/grain/validators/packet_validator.py` — block pending/failed verification states at closure
- `src/grain/services/workflow_service.py` — surface review-close verification blockers
- `src/grain/cli/task.py` — print closure blockers before exiting
- `tests/test_closure_validation.py` — pending/failed verification coverage
- `tests/test_workflow_state_service.py` — review-close gate coverage
- `tests/test_task_close_cmd.py` — close command blocker coverage

## Acceptance Checklist
- [x] pending verification blocks closure
- [x] failed verification blocks closure until the operator explicitly resolves or waives it
- [x] `workflow next` surfaces review-close blockers instead of routing straight to `task_close`
- [x] `task close` surfaces verification blocker details to the operator
- [x] focused workflow/verification tests pass
- [ ] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Provider polling
- Automatic waiver commands
- Cross-packet verification coordination
