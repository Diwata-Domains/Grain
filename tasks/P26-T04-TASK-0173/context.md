# Context: TASK-0173

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/adapter_profiles.md`

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — preserves the packet-first, CLI-first, file-backed constraints that the crawler guidance must not violate

### Working (load if needed)
- `docs/working/backlog.md` — P26-T04 scope and dependency chain
- `docs/working/current_focus.md` — active Phase 26 direction and immediate goals

### Packet Files
- `tasks/P26-T04-TASK-0173/task.md`
- `tasks/P26-T04-TASK-0173/plan.md`
- `tasks/P26-T04-TASK-0173/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a — this task documents how operators and agents should handle the existing crawler adapter safely

## Excluded Context
- new crawler execution tooling is excluded because this task is only about review and safety guidance
- phase-close smoke/docs work is excluded because it belongs to `P26-T05`

## Context Sufficiency Note
The runtime adapter contract, current Phase 26 plan, and existing shipped operator docs are sufficient because this task only needs to harden review/safety guidance for the crawler slice.
