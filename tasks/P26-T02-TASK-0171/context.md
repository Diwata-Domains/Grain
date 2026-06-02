# Context: TASK-0171

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/adapter_profiles.md`

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — preserves the packet-first, file-backed constraints for adapter-driven context selection

### Working (load if needed)
- `docs/working/backlog.md` — P26-T02 scope and dependency on the crawler adapter scaffold
- `docs/working/current_focus.md` — active Phase 26 direction and immediate goals

### Packet Files
- `tasks/P26-T02-TASK-0171/task.md`
- `tasks/P26-T02-TASK-0171/plan.md`
- `tasks/P26-T02-TASK-0171/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** crawler_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** this task implements the first concrete context-selection behavior for the new crawler adapter surface

## Excluded Context
- output-validation and extraction-quality prioritization is excluded because it belongs to `P26-T03`
- runtime crawler tooling and execution helpers are excluded because this task is only about context assembly

## Context Sufficiency Note
The runtime adapter profile contract, current Phase 26 plan, and existing context-service code are sufficient because this task is a bounded context-selection change inside the current adapter pipeline.
