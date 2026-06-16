# Deliverable Spec: TASK-0111

## Required Output

### New Files
- `src/grain/services/ollama_provider.py` — local-server embedding provider
- `tests/test_ollama_provider.py` — provider and resolver integration coverage

### Modified Files
- `src/grain/services/embedding_resolver.py` — built-in Ollama resolver integration
- packet files under `tasks/P16-T03-TASK-0111/` — task execution records

## Acceptance Checklist
- [ ] `OllamaProvider` scores candidates by vector similarity
- [ ] Resolver uses Ollama when configured and falls back when unavailable
- [ ] Provider status reports unavailable server conditions cleanly
- [ ] Focused provider and resolver tests pass
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions, or any unrun coverage explicitly noted in `results.md`
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- LocalProvider or OpenAIProvider implementations
- context-service integration
