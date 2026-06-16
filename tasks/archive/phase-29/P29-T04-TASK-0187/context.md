# Context: TASK-0187

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/cli_spec.md` — existing workflow CLI contract to extend with a thin diagnostic surface

### Working (load if needed)
- `docs/working/backlog.md` — confirms the hardening goal and task sequencing

### Packet Files
- `tasks/P29-T04-TASK-0187/task.md`
- `tasks/P29-T04-TASK-0187/plan.md`
- `tasks/P29-T04-TASK-0187/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** this slice changes the workflow CLI/service layer and its command coverage.

## Excluded Context
- Broader docs closeout and hardening smoke coverage are excluded; they belong to `P29-T05`.

## Context Sufficiency Note
`workflow.py`, `workflow_service.py`, and the existing workflow command tests are sufficient to add a read-only diagnostic surface without changing the workflow decision engine.
