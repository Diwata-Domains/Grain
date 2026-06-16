# Context: TASK-0111

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — provider output remains advisory and deterministic
- `docs/canonical/product_scope.md` — local-first semantic enrichment is in scope without changing workflow authority

### Working (load if needed)
- `docs/working/backlog.md` — task sequence and dependency on P16-T02
- `docs/working/implementation_plan.md` — Ollama role in the Phase 16 provider sequence

### Packet Files
- `tasks/P16-T03-TASK-0111/task.md`
- `tasks/P16-T03-TASK-0111/plan.md`
- `tasks/P16-T03-TASK-0111/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a — semantic-provider plumbing in the workflow core

## Excluded Context
- Local and OpenAI provider implementations — separate tasks
- context-service integration — deferred to P16-T06

## Context Sufficiency Note
This context is sufficient because the task is limited to one provider implementation plus resolver integration and does not require broader context-selection changes yet.
