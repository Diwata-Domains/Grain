# Deliverable Spec: TASK-0127

## Required Output

### New Files
- none

### Modified Files
- `src/grain/services/codebase_scanner.py` — promote notebook/data-file signals into official `data_adapter` applicability
- `tests/test_codebase_scanner.py` — validate data workflows map to `applicable_adapters` instead of a custom hint
- `tests/test_onboard_doc_generator.py` — ensure generated draft docs surface `data_adapter`
- `tasks/P18-T05-TASK-0127/task.md` — populated scope and constraints
- `tasks/P18-T05-TASK-0127/context.md` — recorded required docs and exclusions
- `tasks/P18-T05-TASK-0127/plan.md` — implementation plan
- `tasks/P18-T05-TASK-0127/deliverable_spec.md` — acceptance criteria and non-goals

## Acceptance Checklist
- [ ] scanner surfaces `data_adapter` in `applicable_adapters` for notebooks/data files
- [ ] obsolete custom-hint text for data workflows is removed
- [ ] onboarding draft docs surface `data_adapter` through the normal adapter list
- [ ] focused tests cover scanner and onboarding behavior
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions, or any unrun coverage explicitly noted in `results.md`
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- registry/install flows
- changes to devops/mobile custom-adapter hint behavior
- end-to-end Phase 18 integration coverage
