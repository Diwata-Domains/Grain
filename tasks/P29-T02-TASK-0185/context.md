# Context: TASK-0185

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/cli_spec.md` — existing workflow-next and packet-close contract

### Working (load if needed)
- `docs/working/backlog.md` — confirms the Phase 29 enforcement scope

### Packet Files
- `tasks/P29-T02-TASK-0185/task.md`
- `tasks/P29-T02-TASK-0185/plan.md`
- `tasks/P29-T02-TASK-0185/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** this slice changes read-only workflow evaluation behavior and its tests.

## Excluded Context
- Runner activation fixes and broader diagnostics are excluded; those belong to later Phase 29 tasks.

## Context Sufficiency Note
The workflow evaluator, workflow domain types, and workflow-state tests are sufficient to add early misuse blockers without expanding the workflow model.
