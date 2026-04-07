# Context: TASK-0060

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/adapter_profiles.md` — adapter contract source used by loader and context assembly tests

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — task lifecycle, review handoff, and test-completion expectations
- `docs/canonical/data_contracts.md` — packet metadata and adapter-field compatibility boundaries
- `docs/canonical/architecture.md` — adapter subsystem boundaries and runtime/core separation

### Working (load if needed)
- `docs/working/backlog.md` — confirms P6-T07 scope and dependencies
- `docs/working/current_focus.md` — confirms phase focus and immediate sequencing

### Packet Files
- `tasks/P6-T07-TASK-0060/task.md`
- `tasks/P6-T07-TASK-0060/plan.md`
- `tasks/P6-T07-TASK-0060/deliverable_spec.md`

## Excluded Context
- Phase 7 onboarding/adoption planning docs are excluded because this packet only validates Phase 6 adapter contract behavior.

## Context Sufficiency Note
This context is sufficient because the packet only adds adapter-system tests against established runtime and packet contracts without changing canonical behavior.
