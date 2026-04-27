# Context: TASK-0117

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — ranking must remain deterministic, explainable, and advisory-only
- `docs/canonical/product_scope.md` — advisory outputs must not become hidden authority

### Working (load if needed)
- `docs/working/backlog.md` — P17-T01 scope and downstream Phase 17 dependencies
- `docs/working/implementation_plan.md` — ranking-layer objective and deliverable outline

### Packet Files
- `tasks/P17-T01-TASK-0117/task.md`
- `tasks/P17-T01-TASK-0117/plan.md`
- `tasks/P17-T01-TASK-0117/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a — ranking contracts live in workflow-core domain code

## Excluded Context
- production ranking service behavior — deferred to P17-T02
- context-selection integration — deferred to P17-T03

## Context Sufficiency Note
This context is sufficient because the task is limited to defining the ranking contract layer and validating it with focused domain tests.
