# Context: TASK-0062

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — task/phase lifecycle and review/close expectations
- `docs/canonical/architecture.md` — service-first, deterministic behavior constraints

### Working (load if needed)
- `docs/working/v2_plan.md` — Phase 8 minimal slice contract and stop-condition rules
- `docs/working/backlog.md` — active-phase task readiness/status signals
- `docs/working/current_focus.md` — active phase source of truth
- `docs/working/current_task.md` — active task pointer and status

### Packet Files
- `tasks/P8-T02-TASK-0062/task.md`
- `tasks/P8-T02-TASK-0062/plan.md`
- `tasks/P8-T02-TASK-0062/deliverable_spec.md`

## Excluded Context
- CLI command implementation files are excluded in this task (`src/forge/cli/*`); this packet is service/domain only.
- Sentinel bridge files are excluded; out of scope until later Phase 8 tasks.

## Context Sufficiency Note
These sources are sufficient to implement deterministic next-step evaluation and stop-condition logic without introducing runner execution behavior.
