# Deliverable Spec: TASK-0126

## Required Output

### New Files
- none

### Modified Files
- `src/grain/adapters/export.py` — route Phase 18 data artifact suffixes through `DataArtifactExtractor`
- `tests/test_context_export.py` — add metadata-only export coverage for data artifacts
- `tests/test_orchestration_service.py` — prove `data_adapter` scope activation in representative data workflows
- `tasks/P18-T04-TASK-0126/task.md` — populated scope and constraints
- `tasks/P18-T04-TASK-0126/context.md` — recorded required docs and exclusions
- `tasks/P18-T04-TASK-0126/plan.md` — implementation plan
- `tasks/P18-T04-TASK-0126/deliverable_spec.md` — acceptance criteria and non-goals

## Acceptance Checklist
- [ ] context export renders metadata-only summaries for Phase 18 data artifact suffixes
- [ ] orchestration scope analysis can activate `data_adapter` in representative data workflows
- [ ] proposal-only orchestration payload shape remains backward-compatible
- [ ] focused tests cover export and scope integration paths
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions, or any unrun coverage explicitly noted in `results.md`
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- scanner/onboarding recommendation changes
- full Phase 18 end-to-end suite
- any change to authoritative workflow/task ranking behavior
