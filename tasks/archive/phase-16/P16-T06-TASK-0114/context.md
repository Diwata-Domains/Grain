# Context: TASK-0114

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — context selection must remain minimal, traceable, and provider-agnostic
- `docs/canonical/product_scope.md` — semantic outputs are advisory, not authority overrides

### Working (load if needed)
- `docs/working/backlog.md` — task contract for P16-T06 and downstream Phase 16 dependencies
- `docs/working/implementation_plan.md` — semantic-layer design notes for reranking existing context candidates

### Packet Files
- `tasks/P16-T06-TASK-0114/task.md`
- `tasks/P16-T06-TASK-0114/plan.md`
- `tasks/P16-T06-TASK-0114/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a — workflow-core context assembly and semantic-provider plumbing

## Excluded Context
- provider recommendation UI — deferred to P16-T07
- broader ranking-service design beyond context selection — deferred to later phases

## Context Sufficiency Note
This context is sufficient because the task is limited to reranking existing adapter candidates inside the current context assembly pipeline without changing workflow law.
