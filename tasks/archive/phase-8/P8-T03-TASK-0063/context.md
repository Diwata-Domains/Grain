# Context: TASK-0063

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — workflow sequencing and review/close behavior contract
- `docs/canonical/architecture.md` — service/CLI separation and deterministic command boundaries

### Working (load if needed)
- `docs/working/v2_plan.md` — Phase 8 machine-readable command boundary and stop conditions
- `docs/working/backlog.md` — task dependency/order for Phase 8
- `docs/working/current_focus.md` — immediate workflow-automation priorities

### Packet Files
- `tasks/P8-T03-TASK-0063/task.md`
- `tasks/P8-T03-TASK-0063/plan.md`
- `tasks/P8-T03-TASK-0063/deliverable_spec.md`

## Excluded Context
- Runner mutation/execute behavior (`workflow run`) is excluded; this task only reports next-action state.
- Sentinel bridge contract work is excluded (separate later tasks).

## Context Sufficiency Note
These docs are sufficient to implement and validate a CLI reporting surface for evaluator decisions without changing workflow semantics.
