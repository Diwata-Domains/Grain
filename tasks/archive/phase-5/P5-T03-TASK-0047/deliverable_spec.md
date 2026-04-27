# Deliverable Spec: TASK-0047

## Required Output

### New Files
- `src/forge/services/handoff_service.py` — handoff artifact generation and validation service
- `tests/test_handoff_service.py` — focused handoff-service coverage

### Modified Files
- `tasks/P5-T03-TASK-0047/task.md` — active task metadata
- `tasks/P5-T03-TASK-0047/context.md` — execution context
- `tasks/P5-T03-TASK-0047/plan.md` — implementation plan
- `tasks/P5-T03-TASK-0047/deliverable_spec.md` — deliverable contract
- `tasks/P5-T03-TASK-0047/results.md` — execution results
- `tasks/P5-T03-TASK-0047/handoff.md` — reviewer handoff
- `docs/working/current_task.md` — active task state

## Acceptance Checklist
- [x] Review-ready packets can produce a handoff artifact
- [x] Completed packets can produce a handoff artifact
- [x] Missing packets fail cleanly
- [x] Incomplete packets are reported as not ready for handoff
- [x] All new tests passing
- [x] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- `forge review handoff`
- `forge review summary`
