# Context: TASK-0066

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — task lifecycle and review/close gating
- `docs/canonical/architecture.md` — deterministic, service-first command behavior

### Working (load if needed)
- `docs/working/v2_plan.md` — machine-readable workflow command boundary
- `docs/working/backlog.md` — phase sequencing and task readiness constraints
- `docs/working/current_focus.md` — active priorities and constraints

### Packet Files
- `tasks/P8-T06-TASK-0066/task.md`
- `tasks/P8-T06-TASK-0066/plan.md`
- `tasks/P8-T06-TASK-0066/deliverable_spec.md`

## Excluded Context
- `workflow run` execution behavior is excluded.
- Prompt rendering/template engine changes are excluded.

## Context Sufficiency Note
These docs and existing command/service patterns are sufficient to implement readiness checks and output surfaces without expanding runner execution scope.
