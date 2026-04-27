# Deliverable Spec: TASK-0048

## Required Output

### New Files
- `tests/test_review_handoff_cmd.py` — CLI coverage for `forge review handoff`

### Modified Files
- `src/forge/cli/review.py` — implement `review handoff`
- `src/forge/services/handoff_service.py` — add a helper for materializing handoff artifacts if needed
- `tasks/P5-T04-TASK-0048/task.md` — active task metadata
- `tasks/P5-T04-TASK-0048/context.md` — execution context
- `tasks/P5-T04-TASK-0048/plan.md` — implementation plan
- `tasks/P5-T04-TASK-0048/deliverable_spec.md` — deliverable contract
- `tasks/P5-T04-TASK-0048/results.md` — execution results
- `tasks/P5-T04-TASK-0048/handoff.md` — reviewer handoff
- `docs/working/current_task.md` — active task state

## Acceptance Checklist
- [x] Review-ready packets can generate a handoff artifact through CLI
- [x] Completed packets can generate a handoff artifact through CLI
- [x] Custom output paths are supported
- [x] Missing packets fail cleanly
- [x] Incomplete packets are rejected
- [x] All new tests passing
- [x] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- `forge review summary`
