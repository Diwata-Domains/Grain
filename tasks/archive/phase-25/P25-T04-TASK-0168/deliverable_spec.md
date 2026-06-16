# Deliverable Spec: TASK-0168

## Required Output

### New Files
- no new product areas required; this slice should stay inside shipped docs and release-surface tests

### Modified Files
- `README.md` — explain the database workflow and review boundary
- `docs/runtime/AGENTS.md` and `docs/runtime/CLAUDE.md` — add database review and validation guidance
- `tests/test_release_surface.py` — add regression assertions for the shipped database guidance
- `tasks/P25-T04-TASK-0168/*` — complete the packet review artifacts for the database review-guidance slice

## Acceptance Checklist
- [ ] shipped docs clearly mention `database_adapter` and its review/validation boundary
- [ ] destructive migration risk, rollback expectations, and schema/query drift are explicit in the runtime guidance
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- new database execution commands
- database recipe work
- phase-close smoke/docs work
