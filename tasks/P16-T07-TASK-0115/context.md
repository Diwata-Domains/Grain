# Context: TASK-0115

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — CLI surfaces must stay provider-agnostic and inspectable
- `docs/canonical/cli_spec.md` — command additions must remain command-facing and avoid rewriting workflow semantics

### Working (load if needed)
- `docs/working/backlog.md` — confirms the required operator-facing fields for P16-T07
- `docs/working/implementation_plan.md` — semantic-layer design notes for provider inspection

### Packet Files
- `tasks/P16-T07-TASK-0115/task.md`
- `tasks/P16-T07-TASK-0115/plan.md`
- `tasks/P16-T07-TASK-0115/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a — semantic-provider inspection stays in workflow-core CLI/service code

## Excluded Context
- context-selection reranking behavior — already handled in P16-T06
- cross-phase ranking logic beyond provider inspection — deferred to later work

## Context Sufficiency Note
This context is sufficient because the task is limited to surfacing already-existing resolver status through a CLI command without changing provider contracts.
