# Context: TASK-0057

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/adapter_profiles.md` — adapter IDs and profile contract context

### Canonical (load for this task)
- `docs/canonical/data_contracts.md` — packet metadata contract and optional-field tolerance
- `docs/canonical/workflow_spec.md` — packet lifecycle constraints
- `docs/canonical/architecture.md` — domain/parser layering boundaries

### Working (load if needed)
- `docs/working/backlog.md` — Phase 6 dependency ordering
- `docs/working/current_focus.md` — current phase priorities
- `docs/working/open_questions.md` — blocker verification

### Packet Files
- `tasks/P6-T04-TASK-0057/task.md`
- `tasks/P6-T04-TASK-0057/plan.md`
- `tasks/P6-T04-TASK-0057/deliverable_spec.md`

## Excluded Context
- `src/forge/services/context_service.py` changes are excluded because adapter hint wiring is deferred to `P6-T05`.

## Context Sufficiency Note
This context is sufficient because the task is constrained to metadata template/parser behavior and compatibility validation.
