# Deliverable Spec: TASK-0084

## Required Output

### New Files
- `tasks/P10-T06-TASK-0084/task.md` — packet metadata/scope
- `tasks/P10-T06-TASK-0084/context.md` — packet context contract
- `tasks/P10-T06-TASK-0084/plan.md` — implementation plan
- `tasks/P10-T06-TASK-0084/deliverable_spec.md` — deliverable contract
- `tasks/P10-T06-TASK-0084/results.md` — execution results
- `tasks/P10-T06-TASK-0084/handoff.md` — review handoff

### Modified Files
- `src/grain/services/structural_intelligence_service.py` — tree-sitter parser implementation
- `pyproject.toml` — parser dependency updates
- `tests/test_structural_intelligence_service.py` — parser-contract assertions
- `docs/working/backlog.md` — set `P10-T06` status for handoff
- `docs/working/current_focus.md` — immediate-goal update after remediation
- `docs/working/current_task.md` — active packet pointer

## Acceptance Checklist
- [ ] Supported-language extraction uses tree-sitter parser path
- [ ] `StructuralExtraction.parser` is `tree-sitter` for supported fixtures
- [ ] `parser = none` only for unsupported/unavailable parser paths
- [ ] No regex fallback path retained for supported languages
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- New graph/context/orchestration feature work
- Phase 11 execution
