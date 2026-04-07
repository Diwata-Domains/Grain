# Deliverable Spec: TASK-0046

## Required Output

### New Files
- `tests/test_review_check_cmd.py` — CLI coverage for `forge review check`

### Modified Files
- `src/forge/cli/review.py` — implement `review check`
- `tasks/P5-T02-TASK-0046/task.md` — active task metadata
- `tasks/P5-T02-TASK-0046/context.md` — execution context
- `tasks/P5-T02-TASK-0046/plan.md` — implementation plan
- `tasks/P5-T02-TASK-0046/deliverable_spec.md` — deliverable contract
- `tasks/P5-T02-TASK-0046/results.md` — execution results
- `tasks/P5-T02-TASK-0046/handoff.md` — reviewer handoff
- `docs/working/current_task.md` — active task state

## Acceptance Checklist
- [x] `forge review check` reports review readiness for a valid packet
- [x] `forge review check` reports blockers for incomplete packets
- [x] JSON output is structured and stable
- [x] Missing packets fail cleanly
- [x] All new tests passing
- [x] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- `forge review handoff`
- `forge review summary`
