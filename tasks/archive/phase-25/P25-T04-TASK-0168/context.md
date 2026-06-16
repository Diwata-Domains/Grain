# Context: TASK-0168

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/adapter_profiles.md`

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — preserves the packet-first, CLI-first, file-backed constraints that the database guidance must not violate

### Working (load if needed)
- `docs/working/backlog.md` — P25-T04 scope and dependency chain
- `docs/working/current_focus.md` — active Phase 25 direction and immediate goals

### Packet Files
- `tasks/P25-T04-TASK-0168/task.md`
- `tasks/P25-T04-TASK-0168/plan.md`
- `tasks/P25-T04-TASK-0168/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a — this task documents how operators and agents should handle the existing database adapter safely

## Excluded Context
- new database execution tooling is excluded because this task is only about review and validation guidance
- phase-close smoke/docs work is excluded because it belongs to `P25-T05`

## Context Sufficiency Note
The runtime adapter contract, current Phase 25 plan, and existing shipped operator docs are sufficient because this task only needs to harden review/validation guidance for the database slice.
