# Deliverable Spec: TASK-0056

## Required Output

### New Files
- `src/forge/adapters/adapter_config.py` — adapter profile loader and parser
- `tests/test_adapter_config_loader.py` — focused tests for load/parse behavior

### Modified Files
- `docs/working/current_task.md` — active task pointer/status
- `docs/working/backlog.md` — P6-T03 status update
- `docs/working/current_focus.md` — immediate-goal progression
- `tasks/P6-T03-TASK-0056/task.md` — task definition
- `tasks/P6-T03-TASK-0056/context.md` — task context
- `tasks/P6-T03-TASK-0056/plan.md` — execution plan
- `tasks/P6-T03-TASK-0056/deliverable_spec.md` — acceptance criteria
- `tasks/P6-T03-TASK-0056/results.md` — implementation outcomes
- `tasks/P6-T03-TASK-0056/handoff.md` — reviewer handoff

## Acceptance Checklist
- [x] `load_adapter_profiles()` loads `docs/runtime/adapter_profiles.md` from repo root
- [x] `parse_adapter_profiles_markdown()` returns structured `AdapterProfile` objects
- [x] Parser validates required fields and required hint presence
- [x] Focused loader tests passing
- [x] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Wiring adapter loader into context service (`P6-T05`, `P6-T06`)
- Packet metadata adapter fields (`P6-T04`)
- CLI command changes
