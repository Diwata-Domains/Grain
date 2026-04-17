# Deliverable Spec: TASK-0062

## Required Output

### New Files
- `src/forge/domain/workflow.py` — workflow evaluation domain models
- `src/forge/services/workflow_service.py` — read-only workflow evaluator service
- `tests/test_workflow_state_service.py` — workflow evaluator behavior coverage
- `tasks/P8-T02-TASK-0062/results.md` — execution results and review notes
- `tasks/P8-T02-TASK-0062/handoff.md` — review handoff bundle

### Modified Files
- `docs/working/backlog.md` — mark `P8-T02` as review
- `docs/working/current_focus.md` — shift immediate goals to `P8-T02` review and next CLI surface task
- `docs/working/current_task.md` — active task pointer for `TASK-0062`
- `tasks/P8-T02-TASK-0062/task.md` — finalized metadata and scope
- `tasks/P8-T02-TASK-0062/context.md` — finalized context selection
- `tasks/P8-T02-TASK-0062/plan.md` — finalized implementation plan
- `tasks/P8-T02-TASK-0062/deliverable_spec.md` — finalized deliverable contract

## Acceptance Checklist
- [ ] Workflow evaluator service is read-only and does not mutate repo state
- [ ] Evaluator returns exactly one next action or explicit stop reason
- [ ] Evaluator enforces blocked and review-artifact stop gates
- [ ] Evaluator resolves no-active-task paths for execute/planning/phase-boundary stop
- [ ] Service outputs include machine-readable fields needed by future CLI surfaces
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- CLI command wiring (`forge workflow next`, `forge workflow run`)
- Canonical documentation edits
- Multi-step autonomous runner execution
