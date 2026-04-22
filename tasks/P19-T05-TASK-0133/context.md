# Context: TASK-0133

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — community adapter trust boundaries
- `docs/canonical/data_contracts.md` — community adapter packaging expectations and promotion boundary

### Working (load if needed)
- `docs/working/backlog.md` — Phase 19 scope for CI and author guidance
- `tasks/P19-T02-TASK-0130/results.md` — validator contract
- `tasks/P19-T03-TASK-0131/results.md` — local install contract
- `tasks/P19-T04-TASK-0132/results.md` — registry scaffold contract

### Packet Files
- `tasks/P19-T05-TASK-0133/task.md`
- `tasks/P19-T05-TASK-0133/plan.md`
- `tasks/P19-T05-TASK-0133/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** docs_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** This task is documentation and workflow guidance for community adapter authors and maintainers.

## Excluded Context
- Phase 19 end-to-end integration behavior — deferred to `P19-T06`
- remote registry download/auth semantics — still out of scope for this phase slice

## Context Sufficiency Note
These docs are sufficient because the workflow and guide only need to codify the Phase 19 contracts that are already implemented.
