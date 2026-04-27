# Deliverable Spec: TASK-0041

## Required Output

### New Files
- `tests/test_model_show_cmd.py` — command tests for `forge model show` text/json outputs and missing-config path

### Modified Files
- `src/forge/cli/model.py` — implemented `forge model show` command behavior
- `tasks/P4-T10-TASK-0041/task.md` — finalized packet metadata/scope
- `tasks/P4-T10-TASK-0041/context.md` — recorded execution context
- `tasks/P4-T10-TASK-0041/plan.md` — recorded implementation plan
- `tasks/P4-T10-TASK-0041/deliverable_spec.md` — recorded deliverable contract
- `tasks/P4-T10-TASK-0041/results.md` — recorded implementation outcomes
- `tasks/P4-T10-TASK-0041/handoff.md` — reviewer handoff bundle
- `docs/working/current_task.md` — active task status updated during execution

## Acceptance Checklist
- [x] `forge model show` renders model classes and profile details in text output
- [x] `forge model show --format json` returns structured profile data
- [x] Missing `agent_profiles.md` fails clearly
- [x] All new tests passing
- [x] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Implementing `forge model select` command behavior
- Implementing `forge model escalate` command behavior
