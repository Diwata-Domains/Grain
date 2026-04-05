# Context: TASK-0042

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/cli_spec.md` — §6.5 model group, recommended options, and output contract

### Working (load if needed)
- `docs/working/current_focus.md` — confirms P4-T09/T10 done and P4-T11 is next

### Packet Files
- `tasks/P4-T11-TASK-0042/task.md`
- `tasks/P4-T11-TASK-0042/plan.md`
- `tasks/P4-T11-TASK-0042/deliverable_spec.md`

### Reference Implementations
- `src/forge/services/model_service.py` — service function to call
- `src/forge/cli/model.py` — file to extend
- `tests/test_model_show_cmd.py` — test pattern to follow

## Excluded Context
- `docs/canonical/architecture.md` — no architectural changes; routing domain already implemented
- `docs/working/backlog.md` — not needed for this narrow implementation task

## Context Sufficiency Note
The existing service layer and CLI stubs are sufficient to implement and test `forge model select` without additional context.
