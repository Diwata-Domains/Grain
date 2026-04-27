# Context: TASK-0074

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — §4.14 orchestration service responsibilities and boundaries, §7.7 `OrchestratorPlan`
- `docs/canonical/workflow_spec.md` — §15 orchestrator interaction invariance and proposal-only rule
- `docs/canonical/cli_spec.md` — §6.8 orchestrate surface responsibilities/must-not constraints
- `docs/canonical/data_contracts.md` — artifact contract context for proposal outputs

### Working (load if needed)
- `docs/working/backlog.md` — Phase 9 sequencing and dependency status
- `docs/working/current_focus.md` — active phase and execution priorities

### Packet Files
- `tasks/P9-T03-TASK-0074/task.md`
- `tasks/P9-T03-TASK-0074/plan.md`
- `tasks/P9-T03-TASK-0074/deliverable_spec.md`

## Excluded Context
- CLI command wiring for `forge orchestrate` is excluded (belongs to `P9-T06`).
- Phase-level orchestration behavior is excluded (belongs to `P9-T04`).

## Context Sufficiency Note
These sources are sufficient to implement task-level orchestration proposal generation while preserving canonical proposal-only boundaries.
