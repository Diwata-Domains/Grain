# Deliverable Spec: TASK-0125

## Required Output

### New Files
- none

### Modified Files
- `docs/runtime/adapter_profiles.md` — migrate notebook ownership from `code_adapter` to `data_adapter`
- `src/grain/services/context_service.py` — preserve deterministic notebook selection for `data_adapter`
- `tests/test_notebook_extractor.py` — prove notebooks still select and export under `data_adapter`
- `tests/test_adapter_config_loader.py` — validate runtime profile changes
- `tasks/P18-T03-TASK-0125/task.md` — populated scope and constraints
- `tasks/P18-T03-TASK-0125/context.md` — recorded required docs and exclusions
- `tasks/P18-T03-TASK-0125/plan.md` — implementation plan
- `tasks/P18-T03-TASK-0125/deliverable_spec.md` — acceptance criteria and non-goals

## Acceptance Checklist
- [ ] `.ipynb` ownership moves from `code_adapter` to `data_adapter` in runtime profiles
- [ ] notebook selection remains deterministic and functional under `data_adapter`
- [ ] notebook extraction output remains unchanged after the ownership migration
- [ ] focused tests prove the migration without depending on broader Phase 18 integration work
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions, or any unrun coverage explicitly noted in `results.md`
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- full data-artifact context integration
- scanner/onboarding recommendation changes
- notebook extractor content-format changes
