# Context: TASK-0043

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/cli_spec.md` — §6.5 model group, escalation command responsibilities

### Working (load if needed)
- `docs/working/current_focus.md` — confirms P4-T12 is the active target

### Packet Files
- `tasks/P4-T12-TASK-0043/task.md`
- `tasks/P4-T12-TASK-0043/plan.md`
- `tasks/P4-T12-TASK-0043/deliverable_spec.md`

### Reference Implementations
- `src/forge/domain/routing.py` — `EscalationRule`, `ModelRoutingConfig` (escalation_rules)
- `src/forge/services/model_service.py` — service pattern to follow
- `src/forge/cli/model.py` — file to extend
- `tests/test_model_select_cmd.py` — test pattern to follow

## Excluded Context
- `docs/canonical/architecture.md` — no architectural changes
- `docs/working/backlog.md` — not needed for this narrow task

## Context Sufficiency Note
Existing domain and service layers have all required escalation data; this task adds the escalation logic function, service wrapper, and CLI surface.
