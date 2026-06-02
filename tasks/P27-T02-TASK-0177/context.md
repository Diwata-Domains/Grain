# Context: TASK-0177

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/cli_spec.md` — preserve existing context command boundaries and JSON output expectations.

### Working (load if needed)
- `docs/working/backlog.md` — confirms the Phase 27 token-budget contract.
- `docs/working/current_focus.md` — active token-efficiency and observability goals.

### Packet Files
- `tasks/P27-T02-TASK-0177/task.md`
- `tasks/P27-T02-TASK-0177/plan.md`
- `tasks/P27-T02-TASK-0177/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** this task changes generic context services and CLI surfaces, not one domain-specific adapter.

## Excluded Context
- `src/grain/tui/` — TUI panels belong to `P27-T03`.
- `src/grain/services/task_observability_service.py` — completed in `TASK-0175` and not modified here.

## Context Sufficiency Note
The context service, context CLI, and Phase 27 planning docs are sufficient for the heuristic budget slice.
