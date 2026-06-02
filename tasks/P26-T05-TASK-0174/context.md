# Context: TASK-0174

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/adapter_profiles.md`

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — preserves the packet-first, file-backed boundary for the crawler smoke and closeout work

### Working (load if needed)
- `docs/working/backlog.md` — P26-T05 closeout scope and dependency chain
- `docs/working/current_focus.md` — active Phase 26 direction and phase-close requirements
- `docs/working/workflow_metrics.md` — phase metrics format for closeout

### Packet Files
- `tasks/P26-T05-TASK-0174/task.md`
- `tasks/P26-T05-TASK-0174/plan.md`
- `tasks/P26-T05-TASK-0174/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a — this is a smoke and closeout slice spanning the existing crawler adapter surfaces

## Excluded Context
- new crawler features are excluded because this task is only validation and phase closeout
- recipe-layer work is excluded because it belongs to the next phase, not this closeout task

## Context Sufficiency Note
The runtime adapter contract, current Phase 26 plan, and existing crawler integration surfaces are sufficient because this task is only validating and closing out the phase.
