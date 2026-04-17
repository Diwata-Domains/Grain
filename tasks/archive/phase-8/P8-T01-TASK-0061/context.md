# Context: TASK-0061

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/product_scope.md` — CLI-first boundary, human-gated workflow change control
- `docs/canonical/architecture.md` — thin CLI/service boundaries and constrained autonomy model
- `docs/canonical/workflow_spec.md` — packet lifecycle and stop-condition expectations

### Working (load if needed)
- `docs/working/v2_plan.md` — Phase 8 planning surface and automation runner guidance
- `docs/working/backlog.md` — P8 sequencing and dependencies
- `docs/working/current_focus.md` — immediate goals and active constraints
- `docs/working/open_questions.md` — prior resolved workflow-boundary questions

### Packet Files
- `tasks/P8-T01-TASK-0061/task.md`
- `tasks/P8-T01-TASK-0061/plan.md`
- `tasks/P8-T01-TASK-0061/deliverable_spec.md`

## Excluded Context
- Runner implementation code (`src/forge/*`) is excluded; this packet is planning-only.
- Sentinel bridge implementation (`P8-T10`) remains excluded.

## Context Sufficiency Note
These documents are sufficient to lock the minimal runner slice and ready dependent Phase 8 tasks without implementation changes.
