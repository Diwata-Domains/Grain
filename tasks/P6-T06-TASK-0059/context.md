# Context: TASK-0059

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/adapter_profiles.md` — source of `review_focus_hints` and `test_or_validation_hints` to surface in context outputs

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — context build/export command expectations
- `docs/canonical/architecture.md` — service/adapter boundaries for context and export paths
- `docs/canonical/data_contracts.md` — compatibility guardrails for output metadata shapes

### Working (load if needed)
- `docs/working/backlog.md` — confirms P6 sequencing and active dependencies
- `docs/working/current_focus.md` — confirms P6-T06 priority and next-step target

### Packet Files
- `tasks/P6-T06-TASK-0059/task.md`
- `tasks/P6-T06-TASK-0059/plan.md`
- `tasks/P6-T06-TASK-0059/deliverable_spec.md`

## Excluded Context
- Phase 7 onboarding/adoption flows are excluded because they depend on Phase 6 adapter contract completion.

## Context Sufficiency Note
This context is sufficient because the task only extends existing adapter metadata and context-output rendering behavior without requiring canonical architecture or scope changes.
