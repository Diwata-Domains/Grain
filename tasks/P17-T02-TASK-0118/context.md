# Context: TASK-0118

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — ranking must stay deterministic, inspectable, and advisory-only
- `docs/canonical/product_scope.md` — advisory outputs must not override authority

### Working (load if needed)
- `docs/working/backlog.md` — P17-T02 scope and downstream consumers
- `docs/working/implementation_plan.md` — ranking-layer objective and signal set

### Packet Files
- `tasks/P17-T02-TASK-0118/task.md`
- `tasks/P17-T02-TASK-0118/plan.md`
- `tasks/P17-T02-TASK-0118/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a — shared ranking logic belongs in workflow-core services

## Excluded Context
- context-selection integration details — deferred to P17-T03
- next-task and impacted-file advisory consumers — deferred to later tasks

## Context Sufficiency Note
This context is sufficient because the task is limited to implementing the shared ranking engine and validating its deterministic behavior.
