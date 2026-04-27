# Deliverable Spec: TASK-0120

## Required Output

### New Files
- `src/grain/services/impact_ranking_service.py` — proposal-only impacted-file ranking helper
- `tests/test_impact_ranking_service.py` — focused impacted-file ranking coverage

### Modified Files
- `src/grain/services/orchestration_service.py` — attaches ranked impact metadata to scope-signal payloads
- `tests/test_orchestration_service.py` — asserts ranked impact payload presence
- packet files under `tasks/P17-T05-TASK-0120/` — task execution records

## Acceptance Checklist
- [ ] impacted-file ranking helper returns semantic and weighted ranking metadata for affected files
- [ ] orchestration scope signals expose ranked impact payload without changing existing `affected_files`
- [ ] ranked impacted-file output remains proposal-only and inspectable
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions, or any unrun coverage explicitly noted in `results.md`
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- changes to the authoritative impact signal contract
- next-task advisory ranking
