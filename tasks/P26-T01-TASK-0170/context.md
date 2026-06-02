# Context: TASK-0170

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/adapter_profiles.md`

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — preserves the packet-first, file-backed constraints for new adapter surfaces

### Working (load if needed)
- `docs/working/backlog.md` — P26-T01 scope and the seeded crawler-adapter sequence
- `docs/working/current_focus.md` — active Phase 26 direction and immediate goals

### Packet Files
- `tasks/P26-T01-TASK-0170/task.md`
- `tasks/P26-T01-TASK-0170/plan.md`
- `tasks/P26-T01-TASK-0170/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a — this task defines the crawler adapter surface itself rather than using a pre-existing adapter during implementation

## Excluded Context
- crawl-config and selector context-selection behavior is excluded because it belongs to `P26-T02`
- crawler recipes, runtime tooling, and execution helpers are excluded because this slice is only the adapter contract scaffold

## Context Sufficiency Note
The runtime adapter profile contract plus the Phase 26 working-doc plan are sufficient because this task is only establishing the dedicated crawler adapter boundary and shipped profile shape.
