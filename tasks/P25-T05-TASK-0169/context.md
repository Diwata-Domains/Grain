# Context: TASK-0169

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/adapter_profiles.md`

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — preserves the packet-first, file-backed boundary for the database smoke and closeout work

### Working (load if needed)
- `docs/working/backlog.md` — P25-T05 closeout scope and dependency chain
- `docs/working/current_focus.md` — active Phase 25 direction and phase-close requirements
- `docs/working/workflow_metrics.md` — phase metrics format for closeout

### Packet Files
- `tasks/P25-T05-TASK-0169/task.md`
- `tasks/P25-T05-TASK-0169/plan.md`
- `tasks/P25-T05-TASK-0169/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a — this is a smoke and closeout slice spanning the existing database adapter surfaces

## Excluded Context
- new database features are excluded because this task is only validation and phase closeout
- crawler and later-phase recipe work are excluded because they belong to later phases

## Context Sufficiency Note
The runtime adapter contract, current Phase 25 plan, and existing database integration surfaces are sufficient because this task is only validating and closing out the phase.
