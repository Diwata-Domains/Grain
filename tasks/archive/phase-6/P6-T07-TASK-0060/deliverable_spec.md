# Deliverable Spec: TASK-0060

## Required Output

### New Files
- `tasks/P6-T07-TASK-0060/task.md` — packet definition
- `tasks/P6-T07-TASK-0060/context.md` — selected context
- `tasks/P6-T07-TASK-0060/plan.md` — implementation plan
- `tasks/P6-T07-TASK-0060/deliverable_spec.md` — acceptance criteria
- `tasks/P6-T07-TASK-0060/results.md` — execution results
- `tasks/P6-T07-TASK-0060/handoff.md` — review handoff
- `tests/test_adapter_loading.py` — adapter loading and packet metadata compatibility tests
- `tests/test_adapter_context.py` — adapter context assembly safety tests

### Modified Files
- `docs/working/current_task.md` — active task state
- `docs/working/backlog.md` — P6-T07 status update
- `docs/working/current_focus.md` — immediate-goal progression

## Acceptance Checklist
- [x] Adapter loader behavior covered with adapter profiles that include optional hint fields
- [x] Packet metadata parsing covered for packets with and without adapter metadata fields
- [x] Context assembly coverage includes adapter-neutral (`primary_adapter: none`) behavior
- [x] Context assembly coverage includes unknown-adapter safe degradation behavior
- [x] Focused adapter/context tests passing
- [x] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Runtime behavior changes to adapter selection or context assembly
- Canonical contract changes
