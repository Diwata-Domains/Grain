# Deliverable Spec: TASK-0146

## Required Output

### New Files
- `src/grain/cli/tui.py` — CLI command that launches the Grain terminal UI shell
- `src/grain/tui/__init__.py` — TUI package export surface
- `src/grain/tui/app.py` — lazy-loaded Textual shell and workflow snapshot helpers
- `tests/test_tui_cmd.py` — focused tests for TUI command wiring and snapshot behavior

### Modified Files
- `pyproject.toml` — add the Textual dependency for the in-process TUI stack
- `src/grain/cli/__init__.py` — register the new `grain tui` command
- `tasks/P22-T01-TASK-0146/task.md` — mark execution status and retain scope
- `tasks/P22-T01-TASK-0146/context.md` — record the required implementation context
- `tasks/P22-T01-TASK-0146/plan.md` — record the execution plan

## Acceptance Checklist
- [ ] `grain tui` is available from the main CLI entrypoint
- [ ] the TUI shell lives under `src/grain/tui/` and remains thin over existing Grain workflow services
- [ ] the scaffold renders workflow-aware placeholders without adding hidden workflow state
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- full dashboard detail, packet inspector depth, prompt preview detail, and action-launch flows beyond the base shell
- embedded agent terminals, multi-project views, or non-terminal UI surfaces
