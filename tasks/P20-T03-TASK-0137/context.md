# Context: TASK-0137

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md` — workflow-state and repo-operation constraints

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — intended workflow-state transitions
- `docs/canonical/data_contracts.md` — stable command-output expectations

### Working (load if needed)
- `docs/working/backlog.md` — Phase 20 contract for P20-T03
- `docs/working/tooling_notes.md` — source signal for stale current-task drift

### Packet Files
- `tasks/P20-T03-TASK-0137/task.md`
- `tasks/P20-T03-TASK-0137/plan.md`
- `tasks/P20-T03-TASK-0137/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** [adapter_id or none]
- **Secondary Adapters:** [adapter_ids or none]
- **Adapter Rationale:** n/a

## Excluded Context
- Reconcile auto-fix implementation details beyond the stale done-pointer case
- Terminal project-complete state work, which belongs to P20-T04

## Context Sufficiency Note
The workflow evaluator, reconcile service, and focused workflow-state tests are sufficient to implement this read-only stale-pointer hardening without touching unrelated command groups.
