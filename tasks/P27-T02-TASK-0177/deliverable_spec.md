# Deliverable Spec: TASK-0177

## Required Output

### Modified Files
- `src/grain/services/context_service.py` — add context-budget heuristics and trim hints
- `src/grain/cli/context.py` — surface context-budget metadata
- `tests/test_context_build_cmd.py` — add build-side budget coverage
- `tests/test_context_export_cmd.py` — add export-side budget coverage

## Acceptance Checklist
- [x] Context bundle exports include source-count and token-budget proxies
- [x] Context build text output shows budget warnings and trim hints
- [x] Context export JSON includes budget data
- [x] All new tests passing
- [ ] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Provider-specific token accounting
- TUI integration
- Automatic context trimming
