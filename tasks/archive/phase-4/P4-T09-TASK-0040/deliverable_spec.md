# Deliverable Spec: TASK-0040

## Required Output

### New Files
- `src/forge/services/model_service.py` — service wrapper that loads config and resolves model class for stage/role queries
- `tests/test_model_service.py` — routing + service tests for P4-T09 behavior

### Modified Files
- `src/forge/domain/routing.py` — added stage/role selection logic and decision model
- `tasks/P4-T09-TASK-0040/task.md` — finalized task scope and metadata
- `tasks/P4-T09-TASK-0040/context.md` — recorded required context
- `tasks/P4-T09-TASK-0040/plan.md` — recorded implementation plan
- `tasks/P4-T09-TASK-0040/deliverable_spec.md` — recorded deliverable contract
- `tasks/P4-T09-TASK-0040/results.md` — recorded implementation results
- `tasks/P4-T09-TASK-0040/handoff.md` — prepared reviewer handoff
- `docs/working/current_task.md` — updated active task state

## Acceptance Checklist
- [x] Workflow stage and task-role inputs resolve to model classes deterministically
- [x] Selection logic remains provider-agnostic and role/capability based
- [x] Service loads runtime profile config and reports missing-config errors cleanly
- [x] All new tests passing
- [x] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- CLI command wiring in `src/forge/cli/model.py`
- Escalation command behavior (`forge model escalate`) beyond selection foundations
