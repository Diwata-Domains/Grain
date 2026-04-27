# Deliverable Spec: TASK-0085

## Required Output

### New Files
- `tasks/P11-T01-TASK-0085/task.md` — packet metadata/scope
- `tasks/P11-T01-TASK-0085/context.md` — packet context contract
- `tasks/P11-T01-TASK-0085/plan.md` — implementation plan
- `tasks/P11-T01-TASK-0085/deliverable_spec.md` — deliverable contract
- `tasks/P11-T01-TASK-0085/results.md` — execution results
- `tasks/P11-T01-TASK-0085/handoff.md` — review handoff

### Modified Files
- `pyproject.toml` — finalized package metadata/build configuration fields
- `docs/working/backlog.md` — update `P11-T01` status and sequence `P11-T02`
- `docs/working/current_focus.md` — update immediate Phase 11 goals
- `docs/working/current_task.md` — active packet pointer

## Acceptance Checklist
- [ ] `pyproject.toml` includes finalized metadata fields (classifiers/license/description/homepage/keywords/python constraints)
- [ ] `grain` entry point remains correctly defined
- [ ] Wheel builds successfully from `src/` layout
- [ ] Wheel contents exclude dev/test artifact directories
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Publish automation (`P11-T02`)
- Install docs (`P11-T03`/`P11-T04`)
