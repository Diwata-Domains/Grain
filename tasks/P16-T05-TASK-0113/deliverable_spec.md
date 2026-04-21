# Deliverable Spec: TASK-0113

## Required Output

### New Files
- `src/grain/services/openai_provider.py` — optional OpenAI semantic provider
- `tests/test_openai_provider.py` — provider and resolver integration coverage

### Modified Files
- `src/grain/services/embedding_resolver.py` — built-in OpenAI provider support
- packet files under `tasks/P16-T05-TASK-0113/` — task execution records

## Acceptance Checklist
- [ ] `OpenAIProvider` scores candidates by vector similarity
- [ ] Resolver uses OpenAIProvider when configured and falls back when configuration is incomplete
- [ ] Provider status reports missing API-key conditions cleanly
- [ ] Focused provider and resolver tests pass
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions, or any unrun coverage explicitly noted in `results.md`
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- context-service integration
- provider selection UI
