# Deliverable Spec: TASK-0059

## Required Output

### New Files
- `tasks/P6-T06-TASK-0059/task.md` — packet definition
- `tasks/P6-T06-TASK-0059/context.md` — selected execution context
- `tasks/P6-T06-TASK-0059/plan.md` — implementation plan
- `tasks/P6-T06-TASK-0059/deliverable_spec.md` — acceptance criteria
- `tasks/P6-T06-TASK-0059/results.md` — execution results
- `tasks/P6-T06-TASK-0059/handoff.md` — review handoff

### Modified Files
- `src/forge/services/context_service.py` — adds adapter hint metadata fields in context bundle output
- `src/forge/cli/context.py` — surfaces adapter hint data in build/export CLI output and JSON export payload
- `src/forge/adapters/export.py` — renders adapter hint sections in markdown context export
- `tests/test_context_build.py` — verifies adapter hint metadata in bundle output
- `tests/test_context_build_cmd.py` — verifies build command hint summary output
- `tests/test_context_export.py` — verifies markdown export includes adapter hint section
- `tests/test_context_export_cmd.py` — verifies JSON export includes adapter hint metadata
- `docs/working/current_task.md` — active task state
- `docs/working/backlog.md` — P6-T06 status update
- `docs/working/current_focus.md` — immediate-goal progression

## Acceptance Checklist
- [x] Active adapter review hints are surfaced in context build output
- [x] Active adapter validation hints are surfaced in context build/output exports
- [x] JSON context export includes `adapter_context` metadata
- [x] Markdown context export includes adapter hint section when adapter is active
- [x] Adapter-neutral behavior remains safe when no adapter is declared
- [x] Focused context tests passing
- [x] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Additional adapter profiles or adapter execution logic (deferred to later phases)
- End-to-end adapter-system matrix expansion beyond this hint-surfacing behavior (covered in `P6-T07`)
