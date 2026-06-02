# Deliverable Spec: TASK-0178

## Required Output

### Modified Files
- `src/grain/tui/app.py` — add observability panel, budget-rich context preview, and results summary support
- `tests/test_tui_cmd.py` — add TUI observability and context-cost panel coverage

## Acceptance Checklist
- [x] TUI snapshot includes observability metadata when present
- [x] Context panel shows estimated token proxies and trim hints
- [x] Packet panel shows recent results summary text
- [x] All new tests passing
- [ ] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Live process control
- Multi-project dashboards
- Provider-native token accounting
