# Deliverable Spec: TASK-0058

## Required Output

### New Files
- `tasks/P6-T05-TASK-0058/task.md` — packet definition
- `tasks/P6-T05-TASK-0058/context.md` — packet context selection
- `tasks/P6-T05-TASK-0058/plan.md` — execution plan
- `tasks/P6-T05-TASK-0058/deliverable_spec.md` — acceptance criteria
- `tasks/P6-T05-TASK-0058/results.md` — execution results
- `tasks/P6-T05-TASK-0058/handoff.md` — reviewer handoff

### Modified Files
- `src/forge/services/context_service.py` — adapter-aware source bias logic in context bundle assembly
- `tests/test_context_build.py` — adapter bias behavior coverage and ordering assertions
- `docs/working/current_task.md` — active task state
- `docs/working/backlog.md` — P6-T05 status update
- `docs/working/current_focus.md` — immediate goal progression

## Acceptance Checklist
- [x] Context assembly reads packet `primary_adapter` metadata
- [x] Adapter `relevant_file_patterns` and `ignore_file_patterns` influence selected context sources
- [x] `context_priority_rules` are applied to adapter-biased source ordering
- [x] No-adapter packets remain adapter-neutral with unchanged baseline behavior
- [x] Focused context tests passing
- [x] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Surfacing adapter review/test hints in context output (`P6-T06`)
- Adapter system-wide test matrix (`P6-T07`)
- Canonical doc edits
