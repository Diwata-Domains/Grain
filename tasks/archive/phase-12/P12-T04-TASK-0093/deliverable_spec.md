# Deliverable Spec: TASK-0093

## Required Output

### New Files
- `tasks/P12-T04-TASK-0093/task.md` — packet metadata/scope
- `tasks/P12-T04-TASK-0093/context.md` — packet context contract
- `tasks/P12-T04-TASK-0093/plan.md` — implementation plan
- `tasks/P12-T04-TASK-0093/deliverable_spec.md` — deliverable contract
- `tasks/P12-T04-TASK-0093/results.md` — execution results
- `tasks/P12-T04-TASK-0093/handoff.md` — review handoff

### Modified Files
- `src/grain/cli/orchestrate.py` — add `orchestrate accept` command
- `src/grain/services/workflow_loop_service.py` — accepted-plan task-order integration
- `tests/test_orchestrate_cmd.py` — acceptance command tests
- `tests/test_workflow_loop_cmd.py` — accepted-plan loop-order integration test
- `docs/working/backlog.md` — move `P12-T04` to review
- `docs/working/current_focus.md` — immediate goals update for phase close path
- `docs/working/current_task.md` — active packet pointer/state

## Acceptance Checklist
- [ ] `orchestrate accept` updates proposal status to `accepted`
- [ ] Loop consults accepted plan order when resolving conflicting ready tasks
- [ ] Loop falls back cleanly when no accepted plan is usable
- [ ] Integration tests cover acceptance and plan-driven ordering behavior
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- New OrchestratorPlan schema fields beyond optional task-ref extraction
- Phase close execution itself
