# Deliverable Spec: TASK-0115

## Required Output

### New Files
- `src/grain/cli/embedding.py` — embedding inspection CLI group and show command
- `src/grain/services/embedding_service.py` — resolver-backed inspection service
- `tests/test_embedding_show_cmd.py` — text and JSON command coverage

### Modified Files
- `src/grain/cli/__init__.py` — registers the new embedding CLI group
- packet files under `tasks/P16-T07-TASK-0115/` — task execution records

## Acceptance Checklist
- [ ] `grain embedding show` reports configured and active provider/model information
- [ ] command output surfaces provider availability and fallback state
- [ ] text and JSON output are both covered by tests
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions, or any unrun coverage explicitly noted in `results.md`
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- new provider behavior
- context-selection changes
