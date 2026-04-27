# Deliverable Spec: TASK-0118

## Required Output

### New Files
- `src/grain/services/ranking_service.py` — deterministic weighted ranking engine
- `tests/test_ranking_service.py` — focused ranking-service coverage

### Modified Files
- packet files under `tasks/P17-T02-TASK-0118/` — task execution records

## Acceptance Checklist
- [ ] ranking service combines graph distance, semantic similarity, authority, and packet priority into weighted totals
- [ ] ranking output exposes per-signal score breakdowns through `RankedCandidate`
- [ ] ranking order is deterministic with stable tie-breaking
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions, or any unrun coverage explicitly noted in `results.md`
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- consumer integration into context or advisory workflows
