# Deliverable Spec: TASK-0045

## Required Output

### New Files
- `src/forge/services/review_service.py` — review readiness validation service
- `tests/test_review_service.py` — focused review-service coverage

### Modified Files
- `tasks/P5-T01-TASK-0045/task.md` — active task metadata
- `tasks/P5-T01-TASK-0045/context.md` — execution context
- `tasks/P5-T01-TASK-0045/plan.md` — implementation plan
- `tasks/P5-T01-TASK-0045/deliverable_spec.md` — deliverable contract
- `tasks/P5-T01-TASK-0045/results.md` — execution results
- `tasks/P5-T01-TASK-0045/handoff.md` — reviewer handoff
- `docs/working/current_task.md` — active task state

## Acceptance Checklist
- [x] Review readiness can be evaluated for a valid packet
- [x] Missing packets fail cleanly
- [x] Incomplete packets report blockers clearly
- [x] All new tests passing
- [x] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- CLI wiring for `forge review check`, `forge review handoff`, or `forge review summary`
