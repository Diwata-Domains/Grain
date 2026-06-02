# Deliverable Spec: TASK-0175

## Required Output

### New Files
- `src/grain/services/task_observability_service.py` — packet-local observability read/update service
- `tests/test_task_observe_cmd.py` — focused command and close-hook coverage

### Modified Files
- `src/grain/cli/task.py` — add `task observe` and close-hook updates
- `src/grain/cli/workflow.py` — surface active-task observability in text and JSON
- `src/grain/services/workflow_run_service.py` — record activation events
- `tests/test_workflow_next_cmd.py` — active-task observability coverage
- `tests/test_workflow_run_cmd.py` — activation observability coverage

## Acceptance Checklist
- [x] Packet-local observability service exists and writes deterministic JSON
- [x] `grain task observe` can show and update the active task record
- [x] `grain workflow next` surfaces active-task observability metadata
- [x] Runner activation and task close record last workflow action updates
- [x] All new tests passing
- [ ] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Live agent lifecycle management
- TUI panels
- Token-budget calculations
