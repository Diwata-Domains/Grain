# Context: TASK-0146

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — verify the TUI remains a thin shell over existing Grain services and command surfaces

### Working (load if needed)
- `docs/working/current_focus.md` — confirms Phase 22 scope and the locked Textual stack
- `docs/working/backlog.md` — defines the boundary of `P22-T01` versus later TUI tasks
- `docs/working/implementation_plan.md` — records the v0.3.0 sequencing and deferrals for the first TUI slice

### Packet Files
- `tasks/P22-T01-TASK-0146/task.md`
- `tasks/P22-T01-TASK-0146/plan.md`
- `tasks/P22-T01-TASK-0146/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a

## Excluded Context
- `docs/runtime/adapter_profiles.md` — adapter-specific execution logic is not needed for the shell bootstrap
- later Phase 22 task packets — dashboard details, packet inspectors, and action launch flows are intentionally deferred to their own tasks

## Context Sufficiency Note
The selected docs are sufficient because this task only needs the locked TUI boundary, current CLI/service entrypoints, and the active packet contract to scaffold the shell cleanly.
