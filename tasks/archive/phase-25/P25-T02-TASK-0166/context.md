# Context: TASK-0166

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/adapter_profiles.md`

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — preserves the packet-first, file-backed constraints for adapter-driven context selection

### Working (load if needed)
- `docs/working/backlog.md` — P25-T02 scope and dependency on the database adapter scaffold
- `docs/working/current_focus.md` — active Phase 25 direction and immediate goals

### Packet Files
- `tasks/P25-T02-TASK-0166/task.md`
- `tasks/P25-T02-TASK-0166/plan.md`
- `tasks/P25-T02-TASK-0166/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** database_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** this task implements the first concrete context-selection behavior for the new database adapter surface

## Excluded Context
- broader query-file and ORM repository selection is excluded because it belongs to `P25-T03`
- runtime database tooling, migration execution, and mutation helpers are excluded because this task is only about context assembly

## Context Sufficiency Note
The runtime adapter profile contract, current Phase 25 plan, and existing context-service code are sufficient because this task is a bounded context-selection change inside the current adapter pipeline.
