# Deliverable Spec: TASK-0090

## Required Output

### New Files
- `src/grain/domain/workflow_loop.py` — workflow loop config domain models
- `src/grain/services/workflow_loop_config_service.py` — runtime YAML loader/validator
- `docs/runtime/workflow_loop.yaml` — default workflow loop runtime config
- `tests/test_workflow_loop_config_service.py` — loader/validation tests
- `tasks/P12-T01-TASK-0090/task.md` — packet metadata/scope
- `tasks/P12-T01-TASK-0090/context.md` — packet context contract
- `tasks/P12-T01-TASK-0090/plan.md` — implementation plan
- `tasks/P12-T01-TASK-0090/deliverable_spec.md` — deliverable contract
- `tasks/P12-T01-TASK-0090/results.md` — execution results
- `tasks/P12-T01-TASK-0090/handoff.md` — review handoff

### Modified Files
- `docs/working/backlog.md` — status update for `P12-T01`
- `docs/working/current_focus.md` — immediate goals update
- `docs/working/current_task.md` — active task pointer/status

## Acceptance Checklist
- [ ] Workflow loop config domain model added for supervision and stage agents
- [ ] YAML config loader validates required stages and invocation modes
- [ ] Runtime config file exists with valid default values
- [ ] Tests cover valid parse, invalid schema, and override behavior
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- `grain workflow loop` command implementation
- Stage prompt dispatch or agent invocation runtime
