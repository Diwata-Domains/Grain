# Deliverable Spec: TASK-0186

## Required Output

### New Files
- None

### Modified Files
- `src/grain/services/workflow_run_service.py` — hydrate auto-created packets and sync activation state
- `tests/test_workflow_run_cmd.py` — add activation bootstrap coverage
- `tests/test_runner_integration.py` — preserve integration behavior after the runner change
- `tests/test_workflow_state_service.py` — preserve workflow-state compatibility after the runner change

## Acceptance Checklist
- [x] auto-created packets are hydrated instead of left as raw template stubs
- [x] workflow activation syncs packet and backlog status to `in_progress`
- [x] focused workflow-run, runner-integration, and workflow-state tests pass
- [ ] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- New diagnostic command surfaces
- Broader reconcile redesign
- Full phase-close smoke coverage
