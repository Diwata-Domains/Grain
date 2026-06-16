# Deliverable Spec: TASK-0163

## Required Output

### New Files
- no new top-level product area required; this slice should land inside the existing context and adapter test surfaces

### Modified Files
- `src/grain/services/context_service.py` — add the first Obsidian-specific vault-aware source ordering behavior
- `docs/runtime/adapter_profiles.md` and bundled runtime copies if needed — keep the runtime guidance aligned with the implemented Obsidian behavior
- `tests/test_document_adapters_integration.py` — add or refine focused vault-ordering and export coverage
- `tests/test_adapter_config_loader.py` and release-surface tests as needed — keep shipped adapter/runtime expectations aligned
- `tasks/P24-T04-TASK-0163/*` — complete the packet review artifacts for the Obsidian context slice

## Acceptance Checklist
- [ ] `obsidian_adapter` can prioritize a target note and its wiki-linked neighbors ahead of unrelated markdown
- [ ] the ordering survives the normal adapter reranking flow without weakening the broader context-selection system
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Obsidian mutation commands
- full vault graph traversal or indexing
- desktop/MCP wrapper changes
