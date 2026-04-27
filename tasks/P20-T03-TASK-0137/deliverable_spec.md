# Deliverable Spec: TASK-0137

## Required Output

### New Files
- `tests/test_workflow_state_service.py` additions — regression coverage for stale done pointers

### Modified Files
- `src/grain/services/workflow_service.py` — treat done packets referenced by `current_task.md` as non-active during evaluation

## Acceptance Checklist
- [x] Evaluator ignores stale `current_task.md` pointers to done packets
- [x] Blocked / review / in-progress behaviors still pass focused regression coverage
- [x] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Mutating `current_task.md` during evaluation
- Phase-level terminal-state changes handled by P20-T04
