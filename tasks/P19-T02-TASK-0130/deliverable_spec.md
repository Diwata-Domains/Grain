# Deliverable Spec: TASK-0130

## Required Output

### New Files
- `src/grain/services/adapter_package_service.py` — validation service and result model for community adapter packages
- `tests/test_adapter_package_service.py` — focused validation coverage

### Modified Files
- `tasks/P19-T02-TASK-0130/task.md` — populated packet metadata and scope
- `tasks/P19-T02-TASK-0130/context.md` — recorded required docs and exclusions
- `tasks/P19-T02-TASK-0130/plan.md` — implementation plan
- `tasks/P19-T02-TASK-0130/deliverable_spec.md` — acceptance criteria and non-goals

## Acceptance Checklist
- [ ] minimum registry-entry package shape is explicit in service/tests
- [ ] validation checks metadata presence plus adapter-profile parse/shape compliance
- [ ] validation errors are deterministic and install-friendly
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions, or any unrun coverage explicitly noted in `results.md`
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- fetch/install behavior
- registry scaffold or CI wiring
- networked registry queries
