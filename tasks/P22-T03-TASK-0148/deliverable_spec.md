# Deliverable Spec: TASK-0148

## Required Output

### New Files
- none

### Modified Files
- `src/grain/tui/app.py` — extend snapshot and add backlog/task/packet inspector panels
- `src/grain/tui/__init__.py` — export any new inspector snapshot types
- `tests/test_tui_cmd.py` — add coverage for inspector snapshot fields and rendered inspector panels
- `tasks/P22-T03-TASK-0148/task.md` — record execution metadata and scope
- `tasks/P22-T03-TASK-0148/context.md` — record implementation context
- `tasks/P22-T03-TASK-0148/plan.md` — record execution plan

## Acceptance Checklist
- [ ] the TUI surfaces current-phase backlog tasks in a dedicated inspector
- [ ] the TUI surfaces active packet path and packet artifact presence in a dedicated inspector
- [ ] inspector data is read-only and derived from backlog/current-task/packet files already used by Grain
- [ ] the dashboard remains usable without deeper packet editing controls
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- packet content previews
- prompt body previews or context bundle inspectors
- execute/review/close action controls
