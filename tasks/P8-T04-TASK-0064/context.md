# Context: TASK-0064

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — task lifecycle and review/close gating behavior
- `docs/canonical/architecture.md` — deterministic service/CLI layering constraints

### Working (load if needed)
- `docs/working/v2_plan.md` — machine-readable command boundary for Phase 8
- `docs/working/backlog.md` — ready/draft task states in active phase
- `docs/working/current_focus.md` — current phase and sequencing priorities
- `docs/working/current_task.md` — active-task gate signal

### Packet Files
- `tasks/P8-T04-TASK-0064/task.md`
- `tasks/P8-T04-TASK-0064/plan.md`
- `tasks/P8-T04-TASK-0064/deliverable_spec.md`

## Excluded Context
- `workflow run` execution logic and mutation paths are excluded.
- Sentinel bridge work is excluded from this packet.

## Context Sufficiency Note
These docs and existing evaluator/service code are sufficient to deliver a deterministic task-selection CLI surface without expanding scope.
