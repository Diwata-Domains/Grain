# Deliverable Spec: TASK-0150

## Required Output

### New Files
- none

### Modified Files
- `src/grain/tui/app.py` — add prompt preview, context summary, and blocker-detail snapshot/panel support
- `tests/test_tui_cmd.py` — add coverage for preview/detail snapshot and panel behavior
- `tasks/P22-T05-TASK-0150/task.md` — record execution metadata and scope
- `tasks/P22-T05-TASK-0150/context.md` — record implementation context
- `tasks/P22-T05-TASK-0150/plan.md` — record execution plan

## Acceptance Checklist
- [ ] the TUI shows a compact preview of the recommended prompt
- [ ] the TUI shows a compact summary of active-task context composition
- [ ] the TUI shows explicit blocker and affected-artifact detail
- [ ] preview/detail panels remain summary-level and derive from existing Grain services
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- full prompt-body rendering
- full context export rendering
- background context refresh loops
