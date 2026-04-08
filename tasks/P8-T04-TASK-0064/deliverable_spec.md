# Deliverable Spec: TASK-0064

## Required Output

### New Files
- `tests/test_task_next_cmd.py` — command coverage for `forge task next`
- `tasks/P8-T04-TASK-0064/results.md` — execution results
- `tasks/P8-T04-TASK-0064/handoff.md` — review handoff

### Modified Files
- `src/forge/cli/task.py` — add `task next` command
- `docs/working/backlog.md` — mark `P8-T04` review and move `P8-T05` to ready
- `docs/working/current_focus.md` — immediate-goal update
- `docs/working/current_task.md` — active packet pointer/status
- `tasks/P8-T04-TASK-0064/task.md` — packet metadata/scope
- `tasks/P8-T04-TASK-0064/context.md` — packet context
- `tasks/P8-T04-TASK-0064/plan.md` — packet plan
- `tasks/P8-T04-TASK-0064/deliverable_spec.md` — deliverable contract

## Acceptance Checklist
- [ ] `forge task next` command exists and returns a next task when one ready candidate exists
- [ ] Command reports planning-required when no ready task is available
- [ ] JSON output includes stable machine-readable selection fields
- [ ] Command remains read-only and does not mutate workflow/task files
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- `forge phase next` implementation
- `forge task prepare` implementation
- `workflow run` execution behavior
