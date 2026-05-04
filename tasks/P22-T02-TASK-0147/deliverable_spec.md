# Deliverable Spec: TASK-0147

## Required Output

### New Files
- none

### Modified Files
- `src/grain/tui/app.py` — extend the shell snapshot and render a real workflow dashboard
- `tests/test_tui_cmd.py` — cover dashboard snapshot data and rendered summary sections
- `tasks/P22-T02-TASK-0147/task.md` — record execution metadata and scope
- `tasks/P22-T02-TASK-0147/context.md` — record implementation context
- `tasks/P22-T02-TASK-0147/plan.md` — record execution plan

## Acceptance Checklist
- [ ] the TUI dashboard shows active phase, current task, next step, and prompt status
- [ ] the dashboard distinguishes ready workflow state from blocked workflow state
- [ ] candidate tasks or blockers are visible without opening deeper inspectors
- [ ] the dashboard remains read-only and derived from existing Grain services
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- packet artifact inspection depth
- execute/review/close mutation controls
- prompt-preview body rendering or context-bundle inspection
