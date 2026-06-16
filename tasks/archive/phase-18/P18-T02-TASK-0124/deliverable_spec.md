# Deliverable Spec: TASK-0124

## Required Output

### New Files
- `src/grain/services/data_artifact_extractor.py` — metadata-only extractor for dataset and model artifact files
- `tests/test_data_artifact_extractor.py` — focused coverage for supported suffixes and graceful degradation

### Modified Files
- `pyproject.toml` — document optional Phase 18 reader dependencies
- `tasks/P18-T02-TASK-0124/task.md` — populated packet scope and constraints
- `tasks/P18-T02-TASK-0124/context.md` — recorded required docs and exclusions
- `tasks/P18-T02-TASK-0124/plan.md` — implementation plan
- `tasks/P18-T02-TASK-0124/deliverable_spec.md` — acceptance criteria and non-goals

## Acceptance Checklist
- [ ] extractor supports the planned Phase 18 dataset/model suffixes
- [ ] output remains metadata-only for all supported artifact types
- [ ] optional readers add lightweight schema hints without becoming mandatory dependencies
- [ ] focused tests cover graceful degradation and deterministic metadata rendering
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions, or any unrun coverage explicitly noted in `results.md`
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- context export wiring
- adapter-profile notebook ownership migration
- orchestration or scanner integration
