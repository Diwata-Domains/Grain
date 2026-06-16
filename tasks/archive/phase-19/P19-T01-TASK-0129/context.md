# Context: TASK-0129

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — existing official/custom adapter layer boundaries
- `docs/canonical/data_contracts.md` — adapter profile contract and discovery rules
- `docs/canonical/product_scope.md` — product-level adapter positioning

### Working (load if needed)
- `docs/working/backlog.md` — Phase 19 scope and downstream task ordering
- `docs/working/open_questions.md` — Q19 decision entrypoint
- `docs/working/current_focus.md` — active phase and immediate goals

### Packet Files
- `tasks/P19-T01-TASK-0129/task.md`
- `tasks/P19-T01-TASK-0129/plan.md`
- `tasks/P19-T01-TASK-0129/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** docs_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** This is a contract-definition and documentation slice. No runtime adapter behavior changes land here yet.

## Excluded Context
- install command implementation — deferred to P19-T03
- validation service internals — deferred to P19-T02
- registry scaffold/CI files — deferred to P19-T04 and P19-T05

## Context Sufficiency Note
The current canonical adapter contract plus the Phase 19 planning notes are sufficient to resolve the hosting/trust model without widening into implementation work.
