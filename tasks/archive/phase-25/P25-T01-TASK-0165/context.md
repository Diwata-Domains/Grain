# Context: TASK-0165

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/adapter_profiles.md`

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — preserves the packet-first, file-backed constraints for new adapter surfaces

### Working (load if needed)
- `docs/working/backlog.md` — P25-T01 scope and the seeded database-adapter sequence
- `docs/working/current_focus.md` — active Phase 25 direction and immediate goals

### Packet Files
- `tasks/P25-T01-TASK-0165/task.md`
- `tasks/P25-T01-TASK-0165/plan.md`
- `tasks/P25-T01-TASK-0165/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a — this task defines the adapter surface itself rather than using a pre-existing adapter during implementation

## Excluded Context
- schema and migration context-selection behavior is excluded because it belongs to `P25-T02`
- database recipes, runtime tooling, and mutation helpers are excluded because this slice is only the adapter contract scaffold

## Context Sufficiency Note
The runtime adapter profile contract plus the Phase 25 working-doc plan are sufficient because this task is only establishing the dedicated database adapter boundary and shipped profile shape.
