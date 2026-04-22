# Deliverable Spec: TASK-0128

## Required Output

### New Files
- `tests/test_phase18_integration.py` — end-to-end Phase 18 coverage across context, orchestration, and onboarding/scanner flows

### Modified Files
- `tasks/P18-T06-TASK-0128/task.md` — populated packet metadata and scope
- `tasks/P18-T06-TASK-0128/context.md` — recorded required docs and exclusions
- `tasks/P18-T06-TASK-0128/plan.md` — implementation plan
- `tasks/P18-T06-TASK-0128/deliverable_spec.md` — acceptance criteria and non-goals

## Acceptance Checklist
- [ ] integration suite covers context/export behavior for notebooks and data artifacts under `data_adapter`
- [ ] integration suite covers orchestration scope activation and onboarding/scanner detection in the same Phase 18 repo shape
- [ ] integration suite remains deterministic and local-only
- [ ] focused Phase 18 suite passes
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions, or any unrun coverage explicitly noted in `results.md`
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- full-repo suite execution
- any new Phase 18 feature work beyond test coverage
