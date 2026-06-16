# Deliverable Spec: TASK-0114

## Required Output

### New Files
- none

### Modified Files
- `src/grain/services/context_service.py` — semantic reranking integrated into graph-assisted adapter source selection
- `tests/test_context_build.py` — coverage for semantic reranking behavior
- packet files under `tasks/P16-T06-TASK-0114/` — task execution records

## Acceptance Checklist
- [ ] context selection resolves the configured embedding provider with existing fallback behavior
- [ ] graph-derived adapter candidates are semantically reranked without adding new sources
- [ ] selection traces remain intact and inspectable after reranking
- [ ] bundle metadata exposes semantic provider and score details
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions, or any unrun coverage explicitly noted in `results.md`
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- new provider implementations
- CLI surface for provider inspection
