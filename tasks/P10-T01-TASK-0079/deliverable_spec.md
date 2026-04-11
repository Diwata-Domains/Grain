# Deliverable Spec: TASK-0079

## Required Output

### New Files
- `src/grain/services/structural_intelligence_service.py` — deterministic Layer 1 extraction service
- `tests/test_structural_intelligence_service.py` — service tests for code/frontend/docs/devops extraction
- `tasks/P10-T01-TASK-0079/results.md` — execution results
- `tasks/P10-T01-TASK-0079/handoff.md` — review handoff

### Modified Files
- `pyproject.toml` — add tree-sitter dependency declaration
- `docs/working/backlog.md` — set `P10-T01` review and `P10-T02` ready
- `docs/working/current_focus.md` — update immediate goals
- `docs/working/current_task.md` — active packet pointer
- `tasks/P10-T01-TASK-0079/task.md` — packet metadata/scope
- `tasks/P10-T01-TASK-0079/context.md` — packet context
- `tasks/P10-T01-TASK-0079/plan.md` — packet plan
- `tasks/P10-T01-TASK-0079/deliverable_spec.md` — deliverable contract

## Acceptance Checklist
- [ ] Structural extraction service exists for Layer 1
- [ ] Code/frontend extraction surfaces functions/classes/imports/call sites
- [ ] Docs extraction surfaces link/cross-reference style signals
- [ ] Devops extraction surfaces dependency declaration signals
- [ ] Output records are normalized and deterministic
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Knowledge graph persistence (`P10-T02`)
- Graph-assisted context traversal (`P10-T03`)
