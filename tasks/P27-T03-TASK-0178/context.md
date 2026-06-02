# Context: TASK-0178

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/cli_spec.md` — preserve the “thin shell over strong core” boundary.

### Working (load if needed)
- `docs/working/backlog.md` — confirms the final Phase 27 TUI contract.
- `docs/working/current_focus.md` — active observability and token-efficiency goals.

### Packet Files
- `tasks/P27-T03-TASK-0178/task.md`
- `tasks/P27-T03-TASK-0178/plan.md`
- `tasks/P27-T03-TASK-0178/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** this task changes the TUI shell and snapshot rendering only.

## Excluded Context
- `src/grain/services/workflow_run_service.py` — already covered in `TASK-0175`.
- `src/grain/services/context_service.py` — already covered in `TASK-0177`; this task consumes its outputs.

## Context Sufficiency Note
The TUI app, the new observability service, and the context-budget metadata are sufficient for this final Phase 27 slice.
