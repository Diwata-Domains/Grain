# Deliverable Spec: TASK-0117

## Required Output

### New Files
- `src/grain/domain/ranking.py` — deterministic ranking contracts and helper functions
- `tests/test_ranking_domain.py` — focused coverage for the ranking data model

### Modified Files
- `src/grain/domain/__init__.py` — export ranking contracts through the public domain surface
- packet files under `tasks/P17-T01-TASK-0117/` — task execution records

## Acceptance Checklist
- [ ] ranking contracts expose signal IDs, default weights, and inspectable score-component structures
- [ ] authority scoring helper provides a stable normalized ordering for ranking use
- [ ] ranking contracts are exported from `grain.domain`
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions, or any unrun coverage explicitly noted in `results.md`
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- production ranking-service implementation
- context-selection integration
