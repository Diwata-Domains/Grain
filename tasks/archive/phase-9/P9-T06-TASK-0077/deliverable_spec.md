# Deliverable Spec: TASK-0077

## Required Output

### New Files
- `src/grain/cli/orchestrate.py` — orchestrate command group with scope/plan
- `tests/test_orchestrate_cmd.py` — command tests for scope/plan behavior
- `tasks/P9-T06-TASK-0077/results.md` — execution results
- `tasks/P9-T06-TASK-0077/handoff.md` — review handoff

### Modified Files
- `src/grain/cli/__init__.py` — register orchestrate group
- `src/grain/services/orchestration_service.py` — scope analysis API and adapter-filter support
- `tests/test_orchestration_service.py` — service coverage for scope signals and filter errors
- `tests/test_command_groups.py` — include orchestrate group/subcommands
- `docs/working/backlog.md` — set `P9-T06` review and `P9-T07` ready
- `docs/working/current_focus.md` — update immediate goals
- `docs/working/current_task.md` — active packet pointer
- `tasks/P9-T06-TASK-0077/task.md` — packet metadata/scope
- `tasks/P9-T06-TASK-0077/context.md` — packet context
- `tasks/P9-T06-TASK-0077/plan.md` — packet plan
- `tasks/P9-T06-TASK-0077/deliverable_spec.md` — deliverable contract

## Acceptance Checklist
- [ ] `grain orchestrate scope --scope` reports adapter/domain signals
- [ ] `grain orchestrate plan --scope` generates draft `OrchestratorPlan`
- [ ] Plan command writes inspectable artifact in `docs/working/proposals/`
- [ ] Both commands support `--format text|json`
- [ ] Optional `--adapter` filter is supported and invalid IDs fail clearly
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- OrchestratorPlan validator and cross-command integration suite (`P9-T07`)
- Automatic task packet creation from orchestration plans
