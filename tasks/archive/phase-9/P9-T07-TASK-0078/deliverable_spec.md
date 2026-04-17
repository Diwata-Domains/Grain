# Deliverable Spec: TASK-0078

## Required Output

### New Files
- `src/grain/validators/orchestrator_validator.py` — OrchestratorPlan validator helpers
- `tests/test_orchestrator_validator.py` — validator unit tests
- `tests/test_orchestration_integration.py` — adapter/orchestrate integration tests
- `tasks/P9-T07-TASK-0078/results.md` — execution results
- `tasks/P9-T07-TASK-0078/handoff.md` — review handoff

### Modified Files
- `src/grain/validators/__init__.py` — export validator entrypoint
- `docs/working/backlog.md` — set `P9-T07` review
- `docs/working/current_focus.md` — update immediate goals after P9 backlog completion
- `docs/working/current_task.md` — active packet pointer
- `tasks/P9-T07-TASK-0078/task.md` — packet metadata/scope
- `tasks/P9-T07-TASK-0078/context.md` — packet context
- `tasks/P9-T07-TASK-0078/plan.md` — packet plan
- `tasks/P9-T07-TASK-0078/deliverable_spec.md` — deliverable contract

## Acceptance Checklist
- [ ] OrchestratorPlan validator checks `plan_id` is present and non-empty
- [ ] Validator checks `status` is a valid OrchestratorPlan status
- [ ] Validator checks candidate entries contain `candidate_id` and `title`
- [ ] Validator checks `active_adapters` resolve to known adapter IDs when provided
- [ ] Integration coverage exercises `orchestrate scope`, `orchestrate plan`, and `adapter list/show`
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- New CLI command surface for validator execution
- Phase 10 implementation work
