# Context: TASK-0172

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/adapter_profiles.md`

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — preserves the packet-first, file-backed constraints for adapter-driven context selection

### Working (load if needed)
- `docs/working/backlog.md` — P26-T03 scope and dependency on the crawler context foundation
- `docs/working/current_focus.md` — active Phase 26 direction and immediate goals

### Packet Files
- `tasks/P26-T03-TASK-0172/task.md`
- `tasks/P26-T03-TASK-0172/plan.md`
- `tasks/P26-T03-TASK-0172/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** crawler_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** this task extends the crawler adapter with objective-sensitive output-validation and extraction-quality selection rules

## Excluded Context
- review and safety guidance is excluded because it belongs to `P26-T04`
- runtime crawler tooling and execution helpers are excluded because this task is only about context assembly

## Context Sufficiency Note
The runtime adapter profile contract, current Phase 26 plan, and existing crawler context-selection behavior are sufficient because this task is a bounded extension of the same adapter pipeline.
