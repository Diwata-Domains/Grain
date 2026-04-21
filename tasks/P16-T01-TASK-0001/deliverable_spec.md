# Deliverable Spec: TASK-0001

## Required Output

### New Files
- `src/grain/domain/embedding.py` — semantic-scoring domain types and provider protocol
- `src/grain/services/embedding_resolver.py` — provider resolution and BM25 fallback service
- `tests/test_embedding_domain.py` — domain contract coverage
- `tests/test_embedding_resolver.py` — resolver fallback coverage

### Modified Files
- `src/grain/adapters/manifest.py` — extend `GrainConfig` and manifest parsing for semantic provider settings
- `src/grain/domain/__init__.py` — export embedding domain types
- `src/grain/data/runtime/docs_manifest.yaml` — expose semantic provider config in the bundled runtime template
- `docs/runtime/docs_manifest.yaml` — expose semantic provider config in this repo's runtime manifest
- `tests/test_grain_config.py` — validate new config defaults and model fields

## Acceptance Checklist
- [ ] Embedding domain types exist and are importable from `grain.domain`
- [ ] `GrainConfig` accepts `none`, `ollama`, `local`, and `openai`
- [ ] Resolver returns deterministic BM25 fallback behavior when a configured provider is unavailable
- [ ] Focused config and resolver tests pass
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions, or any unrun coverage explicitly noted in `results.md`
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- provider-specific network/API integrations
- semantic reranking inside `context_service.py`
- CLI surface for `grain embedding show`
