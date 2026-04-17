# Deliverable Spec: TASK-0065

## Required Output

### New Files
- `src/forge/cli/phase.py` — phase command group and `phase next` command
- `tests/test_phase_next_cmd.py` — command tests for phase-action outputs
- `tasks/P8-T05-TASK-0065/results.md` — execution results
- `tasks/P8-T05-TASK-0065/handoff.md` — review handoff

### Modified Files
- `src/forge/cli/__init__.py` — register phase command group
- `docs/working/backlog.md` — mark `P8-T05` review and move `P8-T06` to ready
- `docs/working/current_focus.md` — update immediate goals
- `docs/working/current_task.md` — active task pointer for review
- `tasks/P8-T05-TASK-0065/task.md` — packet metadata/scope
- `tasks/P8-T05-TASK-0065/context.md` — packet context
- `tasks/P8-T05-TASK-0065/plan.md` — packet plan
- `tasks/P8-T05-TASK-0065/deliverable_spec.md` — deliverable contract

## Acceptance Checklist
- [ ] `forge phase next` command exists and is callable via `forge phase next`
- [ ] Command reports `phase_planning`, `phase_review_close`, or `no_phase_action` deterministically
- [ ] JSON output includes stable machine-readable phase-action payload
- [ ] Command remains read-only and does not mutate workflow/task state
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- `forge task prepare` implementation
- `forge prompt show` implementation
- `forge workflow run` one-step executor
