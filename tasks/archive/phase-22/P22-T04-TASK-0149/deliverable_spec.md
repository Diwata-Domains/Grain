# Deliverable Spec: TASK-0149

## Required Output

### New Files
- none

### Modified Files
- `src/grain/tui/app.py` — add structured execute/review/close launchers, action panel, and bound actions
- `src/grain/tui/__init__.py` — export any new launcher result types
- `tests/test_tui_cmd.py` — add coverage for launcher helpers and rendered action feedback
- `tasks/P22-T04-TASK-0149/task.md` — record execution metadata and scope
- `tasks/P22-T04-TASK-0149/context.md` — record implementation context
- `tasks/P22-T04-TASK-0149/plan.md` — record execution plan

## Acceptance Checklist
- [ ] execute, review, and close launchers delegate to existing Grain services
- [ ] the TUI exposes visible action controls and operator feedback for launcher outcomes
- [ ] launcher attempts refresh the shell snapshot after mutation or gate results
- [ ] launcher failures/gates remain visible and do not bypass normal workflow rules
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- mouse-first controls
- prompt body rendering or context bundle launchers
- background workflow loops or autonomous action chaining
