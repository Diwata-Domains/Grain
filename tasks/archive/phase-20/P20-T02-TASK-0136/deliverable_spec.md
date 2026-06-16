# Deliverable Spec: TASK-0136

## Required Output

### New Files
- `tests/test_task_id.py` additions — archive-aware regression coverage for task ID allocation

### Modified Files
- `src/grain/domain/packets.py` — include archived packet directories when computing the next task ID

## Acceptance Checklist
- [x] Archived packet directories contribute to the next allocated `TASK-####`
- [x] Archive container directories without task IDs are ignored
- [x] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Changing archive directory structure or packet naming conventions
- Fixing other workflow-state issues outside task ID allocation
