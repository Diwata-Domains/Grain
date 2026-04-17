# Context: TASK-0073

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — §4.13 Adapter capability surface, §4.14 Orchestration Service

### Working (load if needed)
- `docs/working/backlog.md` — P9-T02 description

### Packet Files
- `tasks/P9-T02-TASK-0073/task.md`
- `tasks/P9-T02-TASK-0073/plan.md`
- `tasks/P9-T02-TASK-0073/deliverable_spec.md`

### Prior Task
- `tasks/P9-T01-TASK-0072/handoff.md` — OrchestratorPlan stable types now available

## Excluded Context
- `docs/canonical/data_contracts.md` — not needed; no schema contract for capability types
- `docs/canonical/cli_spec.md` — no CLI changes in this task
- Phase 10+ docs — tree-sitter implementation is deferred

## Context Sufficiency Note
architecture.md §4.13 fully describes the 6 optional capability functions; that plus the existing adapters.py are sufficient to implement this task.
