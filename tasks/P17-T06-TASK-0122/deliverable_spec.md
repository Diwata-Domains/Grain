# Deliverable Spec: TASK-0122

## Required Output

### New Files
- `tests/test_phase17_integration.py` — end-to-end Phase 17 coverage across ranking consumers

### Modified Files
- packet files under `tasks/P17-T06-TASK-0122/` — task execution records

## Acceptance Checklist
- [ ] integration coverage validates ranked context selection, task advice, and impacted-file advice together
- [ ] integration coverage preserves the advisory-only contract for non-workflow ranking outputs
- [ ] integration coverage remains deterministic without live providers
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions, or any unrun coverage explicitly noted in `results.md`
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- new production ranking behavior beyond integration coverage
