# Context: TASK-0189

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/cli_spec.md` — workflow CLI contract and read-only workflow state surfaces

### Working (load if needed)
- `docs/working/backlog.md` — confirms the final Phase 29 closeout scope and sequencing

### Packet Files
- `tasks/P29-T05-TASK-0189/task.md`
- `tasks/P29-T05-TASK-0189/plan.md`
- `tasks/P29-T05-TASK-0189/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** this slice changes workflow parsing, workflow command coverage, and shipped operator guidance.

## Excluded Context
- New feature work outside Phase 29 is excluded; this task is closeout hardening only.

## Context Sufficiency Note
`workflow_service.py`, the workflow command tests, README, and runtime guidance are sufficient to close out the hardening phase without widening scope.
