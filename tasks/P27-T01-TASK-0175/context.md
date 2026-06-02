# Context: TASK-0175

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/cli_spec.md` — preserve CLI-first boundaries and machine-readable output expectations.

### Working (load if needed)
- `docs/working/backlog.md` — Phase 27 scope and task contract for observability metadata.
- `docs/working/current_focus.md` — active phase constraints and token-efficiency direction.

### Packet Files
- `tasks/P27-T01-TASK-0175/task.md`
- `tasks/P27-T01-TASK-0175/plan.md`
- `tasks/P27-T01-TASK-0175/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** this task changes workflow, task, and CLI service code rather than artifact-specific adapters.

## Excluded Context
- `src/grain/tui/` — deferred to later Phase 27 tasks once observability data exists.
- `src/grain/services/context_service.py` — token-budget logic belongs to P27-T02, not this task.

## Context Sufficiency Note
The workflow, task, and CLI surfaces plus the Phase 27 planning docs are sufficient for the first packet-local observability slice.
