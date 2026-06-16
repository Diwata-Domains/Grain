# Context: TASK-0167

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/adapter_profiles.md`

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — preserves the packet-first, file-backed constraints for adapter-driven context selection

### Working (load if needed)
- `docs/working/backlog.md` — P25-T03 scope and dependency on the database context foundation
- `docs/working/current_focus.md` — active Phase 25 direction and immediate goals

### Packet Files
- `tasks/P25-T03-TASK-0167/task.md`
- `tasks/P25-T03-TASK-0167/plan.md`
- `tasks/P25-T03-TASK-0167/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** database_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** this task extends the database adapter with objective-sensitive query and repository selection rules

## Excluded Context
- review/validation guidance is excluded because it belongs to `P25-T04`
- runtime migration tooling and mutation helpers are excluded because this task is only about context assembly

## Context Sufficiency Note
The runtime adapter profile contract, current Phase 25 plan, and existing database context-selection behavior are sufficient because this task is a bounded extension of the same adapter pipeline.
