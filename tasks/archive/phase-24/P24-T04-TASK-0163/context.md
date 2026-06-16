# Context: TASK-0163

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/adapter_profiles.md`

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — packet-first and file-backed workflow constraints that the Obsidian slice must preserve

### Working (load if needed)
- `docs/working/backlog.md` — P24-T04 scope and dependency on the Obsidian adapter scaffold
- `docs/working/current_focus.md` — active Phase 24 objective for desktop integrations and Obsidian support

### Packet Files
- `tasks/P24-T04-TASK-0163/task.md`
- `tasks/P24-T04-TASK-0163/plan.md`
- `tasks/P24-T04-TASK-0163/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** obsidian_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** this task is the first real vault-aware behavior for the dedicated Obsidian adapter, so the Obsidian profile and context-selection service are the direct surfaces under change

## Excluded Context
- desktop/MCP wrapper behavior is excluded because it was already handled in `P24-T01` and `P24-T02`
- Obsidian mutation flows are excluded because this phase is limited to context and operator-surface scaffolding

## Context Sufficiency Note
The runtime adapter profile, current Phase 24 plan, and existing context-service code are sufficient because this task is a bounded ordering/selection behavior inside the existing packet context pipeline.
