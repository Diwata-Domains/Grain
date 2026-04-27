# Deliverable Spec: TASK-0112

## Required Output

### New Files
- `src/grain/services/local_provider.py` — optional local-model semantic provider
- `tests/test_local_provider.py` — provider and resolver integration coverage

### Modified Files
- `src/grain/services/embedding_resolver.py` — built-in local provider support
- packet files under `tasks/P16-T04-TASK-0112/` — task execution records

## Acceptance Checklist
- [ ] `LocalProvider` scores candidates by vector similarity
- [ ] Resolver uses LocalProvider when configured and falls back when dependency is unavailable
- [ ] Provider status reports missing optional dependency conditions cleanly
- [ ] Focused provider and resolver tests pass
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions, or any unrun coverage explicitly noted in `results.md`
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- OpenAI provider implementation
- context-service integration
