# Deliverable Spec: TASK-0076

## Required Output

### New Files
- `src/grain/cli/adapter.py` — adapter command group with list/show
- `tests/test_adapter_cmd.py` — adapter command tests
- `tasks/P9-T05-TASK-0076/results.md` — execution results
- `tasks/P9-T05-TASK-0076/handoff.md` — review handoff

### Modified Files
- `src/grain/cli/__init__.py` — register adapter group
- `tests/test_command_groups.py` — include adapter and other registered groups in help coverage
- `docs/working/backlog.md` — set `P9-T05` review and `P9-T06` ready
- `docs/working/current_focus.md` — update immediate goals
- `docs/working/current_task.md` — active packet pointer
- `tasks/P9-T05-TASK-0076/task.md` — packet metadata/scope
- `tasks/P9-T05-TASK-0076/context.md` — packet context
- `tasks/P9-T05-TASK-0076/plan.md` — packet plan
- `tasks/P9-T05-TASK-0076/deliverable_spec.md` — deliverable contract

## Acceptance Checklist
- [ ] `grain adapter list` command reports known adapter profiles
- [ ] `grain adapter show --id` reports one adapter contract
- [ ] Both commands support `--format text|json`
- [ ] Unknown adapter IDs return usage-style failure
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- `grain orchestrate scope/plan` commands
- Phase 9 orchestration validator/integration suite (`P9-T07`)
