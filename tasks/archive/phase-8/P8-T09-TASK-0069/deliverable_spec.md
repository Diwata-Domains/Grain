# Deliverable Spec: TASK-0069

## Required Output

### New Files
- `tests/test_runner_integration.py` — integration tests across runner commands
- `tasks/P8-T09-TASK-0069/` — full task packet

### Modified Files
- `docs/working/current_focus.md` — updated to reflect P8-T08 done and P8-T09 active
- `docs/working/backlog.md` — P8-T09 status updated to `review`
- `docs/working/current_task.md` — updated to TASK-0069 in_progress

## Acceptance Checklist
- [ ] Integration tests cover activation chain (state mutation visible cross-command)
- [ ] Integration tests cover cross-command agreement on ready task state
- [ ] Integration tests cover cross-command agreement on planning state
- [ ] Integration tests cover phase boundary surfaced by all runner commands
- [ ] Integration tests cover JSON output invariants for all 5+ automation commands
- [ ] All new tests passing (at least 12)
- [ ] Full test suite passing with no regressions
- [ ] No source code files modified
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Changes to existing JSON output shapes
- Source code modifications to CLI or service files
- New CLI commands
