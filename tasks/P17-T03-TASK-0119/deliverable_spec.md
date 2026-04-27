# Deliverable Spec: TASK-0119

## Required Output

### New Files
- none

### Modified Files
- `src/grain/services/context_service.py` — integrate ranked scoring into adapter-source ordering
- `tests/test_context_build.py` — assert ranked score breakdown metadata
- packet files under `tasks/P17-T03-TASK-0119/` — task execution records

## Acceptance Checklist
- [ ] context selection uses the ranking service instead of semantic-only ordering for graph-derived adapter sources
- [ ] bundle metadata exposes ranked score breakdowns alongside semantic provider details
- [ ] graph traces and source inclusion behavior remain intact
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions, or any unrun coverage explicitly noted in `results.md`
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- advisory ranking for next-task or impacted-file outputs
