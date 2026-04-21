# Context: TASK-0122

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — ranking and advisory outputs must stay deterministic and non-authoritative
- `docs/canonical/product_scope.md` — proposal-only behavior must hold across the ranking layer

### Working (load if needed)
- `docs/working/backlog.md` — final Phase 17 deliverable boundary
- `docs/working/implementation_plan.md` — ranking-layer integration goals

### Packet Files
- `tasks/P17-T06-TASK-0122/task.md`
- `tasks/P17-T06-TASK-0122/plan.md`
- `tasks/P17-T06-TASK-0122/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a — this task validates workflow-core ranking behavior end-to-end

## Excluded Context
- Phase 18 data-adapter planning
- any canonical workflow changes beyond the already-resolved Phase 17 advisory contract

## Context Sufficiency Note
This context is sufficient because the task is limited to end-to-end verification of already-landed Phase 17 ranking behavior.
