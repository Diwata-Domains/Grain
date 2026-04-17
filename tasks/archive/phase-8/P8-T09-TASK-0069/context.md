# Context: TASK-0069

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/cli_spec.md` — §10 structured output expectations

### Working (load if needed)
- `docs/working/current_focus.md` — active constraints, to be updated

### Packet Files
- `tasks/P8-T09-TASK-0069/task.md`
- `tasks/P8-T09-TASK-0069/plan.md`
- `tasks/P8-T09-TASK-0069/deliverable_spec.md`

## Excluded Context
- Phase 1–7 archives
- `docs/working/v2_adapters.md`, `docs/working/v2_onboarding.md`
- Canonical docs not related to CLI output behavior

## Context Sufficiency Note
The existing runner CLI files (`workflow.py`, `task.py`, `phase.py`, `prompt.py`) and test patterns from `test_workflow_run_cmd.py` are sufficient to implement this task.
