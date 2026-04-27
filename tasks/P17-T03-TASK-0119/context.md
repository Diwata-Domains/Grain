# Context: TASK-0119

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — context selection must stay minimal, traceable, and deterministic
- `docs/canonical/product_scope.md` — advisory scoring cannot override authoritative workflow behavior

### Working (load if needed)
- `docs/working/backlog.md` — P17-T03 scope and downstream dependencies
- `docs/working/implementation_plan.md` — Phase 17 goal for ranked context selection

### Packet Files
- `tasks/P17-T03-TASK-0119/task.md`
- `tasks/P17-T03-TASK-0119/plan.md`
- `tasks/P17-T03-TASK-0119/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a — shared context-selection logic lives in workflow-core services

## Excluded Context
- next-task advisory ranking — deferred to P17-T04
- impacted-file ranking — deferred to P17-T05

## Context Sufficiency Note
This context is sufficient because the task is limited to swapping context selection over to the new ranking engine while preserving existing source-trace behavior.
