# Deliverable Spec: TASK-0110

## Required Output

### New Files
- `src/grain/services/bm25_provider.py` — deterministic lexical baseline provider
- `tests/test_bm25_provider.py` — provider scoring and status coverage

### Modified Files
- `src/grain/services/embedding_resolver.py` — use `BM25Provider` for default and fallback resolution
- `tests/test_embedding_resolver.py` — assert resolver returns the formal BM25 provider
- packet files under `tasks/P16-T02-TASK-0110/` — task documentation and results

## Acceptance Checklist
- [ ] `BM25Provider` exists as a dedicated provider module
- [ ] Resolver uses `BM25Provider` for configured `none` and fallback cases
- [ ] Deterministic scoring order matches the previous lexical fallback behavior
- [ ] Focused provider and resolver tests pass
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions, or any unrun coverage explicitly noted in `results.md`
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Ollama, Local, or OpenAI provider implementations
- context-service integration
