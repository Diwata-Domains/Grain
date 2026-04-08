# Context: TASK-0065

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — phase and task lifecycle boundaries
- `docs/canonical/architecture.md` — deterministic, service-driven command behavior

### Working (load if needed)
- `docs/working/v2_plan.md` — Phase 8 machine-readable command boundary contract
- `docs/working/backlog.md` — active phase task statuses and phase-bounded readiness
- `docs/working/current_focus.md` — current phase and active sequencing goals
- `docs/working/current_task.md` — active-task pointer for phase-action context

### Packet Files
- `tasks/P8-T05-TASK-0065/task.md`
- `tasks/P8-T05-TASK-0065/plan.md`
- `tasks/P8-T05-TASK-0065/deliverable_spec.md`

## Excluded Context
- Runner step-execution behavior (`workflow run`) is excluded.
- Sentinel bridge and verification ingestion contracts are excluded.

## Context Sufficiency Note
These docs and evaluator services are sufficient to implement a phase-level next-action reporting surface without adding mutation behavior.
