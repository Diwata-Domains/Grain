# Context: TASK-0109

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — advisory/intelligence layer must remain proposal-only and deterministic
- `docs/canonical/product_scope.md` — semantic enrichment is in scope, but it cannot bypass workflow authority boundaries

### Working (load if needed)
- `docs/working/backlog.md` — active Phase 16 task definition and sequencing
- `docs/working/current_focus.md` — confirms Phase 16 is active and Phase 15 is closed
- `docs/working/implementation_plan.md` — provider model defaults and Phase 16 deliverables

### Packet Files
- `tasks/P16-T01-TASK-0109/task.md`
- `tasks/P16-T01-TASK-0109/plan.md`
- `tasks/P16-T01-TASK-0109/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a — this is workflow/core domain plumbing, not adapter-specific logic

## Excluded Context
- provider-specific integration tasks beyond the resolver contract (`P16-T02` through `P16-T05`) — out of scope for this packet
- context-service wiring (`P16-T06`) — this task must not change runtime context selection yet

## Context Sufficiency Note
These docs are sufficient because the task is limited to contract/config plumbing and does not require provider network integration or context-service mutation yet.
