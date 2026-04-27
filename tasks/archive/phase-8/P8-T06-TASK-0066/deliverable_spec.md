# Deliverable Spec: TASK-0066

## Required Output

### New Files
- `src/forge/services/task_prepare_service.py` — task prerequisite-check service
- `tests/test_task_prepare_cmd.py` — command tests for `task prepare`
- `tasks/P8-T06-TASK-0066/results.md` — execution results
- `tasks/P8-T06-TASK-0066/handoff.md` — review handoff

### Modified Files
- `src/forge/cli/task.py` — add `task prepare` subcommand
- `docs/working/backlog.md` — mark `P8-T06` review and move `P8-T07` to ready
- `docs/working/current_focus.md` — update immediate goals
- `docs/working/current_task.md` — active task pointer/status
- `tasks/P8-T06-TASK-0066/task.md` — packet metadata/scope
- `tasks/P8-T06-TASK-0066/context.md` — packet context
- `tasks/P8-T06-TASK-0066/plan.md` — packet plan
- `tasks/P8-T06-TASK-0066/deliverable_spec.md` — deliverable contract

## Acceptance Checklist
- [ ] `forge task prepare --id TASK-####` command exists and checks one task packet
- [ ] Command reports missing packet/prompt prerequisites explicitly
- [ ] JSON output includes stable readiness payload fields
- [ ] Command is read-only and does not mutate task/workflow state
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Prompt rendering engine changes
- `forge prompt show` command implementation
- `forge workflow run` command implementation
