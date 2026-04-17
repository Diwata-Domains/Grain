# Context: TASK-0075

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — §4.14 orchestration service responsibilities, including phase-level outputs
- `docs/canonical/workflow_spec.md` — §15 orchestrator workflow invariance and proposal boundaries
- `docs/canonical/cli_spec.md` — §6.8 orchestrate responsibilities and must-not constraints
- `docs/canonical/data_contracts.md` — proposal artifact contract context

### Working (load if needed)
- `docs/working/backlog.md` — Phase 9 sequence and dependencies
- `docs/working/current_focus.md` — active execution goals and constraints

### Packet Files
- `tasks/P9-T04-TASK-0075/task.md`
- `tasks/P9-T04-TASK-0075/plan.md`
- `tasks/P9-T04-TASK-0075/deliverable_spec.md`

## Excluded Context
- `forge/grain orchestrate` CLI command wiring is excluded (belongs to `P9-T06`).
- Validator/integration bundle for `OrchestratorPlan` is excluded (belongs to `P9-T07`).

## Context Sufficiency Note
These sources are sufficient to implement phase-level orchestration proposal generation while preserving canonical proposal-only boundaries.
