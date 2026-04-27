# Context: TASK-0136

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md` — repo-operation and workflow constraints

### Canonical (load for this task)
- `docs/canonical/data_contracts.md` — stable expectations for task identity and packet lifecycle
- `docs/canonical/workflow_spec.md` — packet and workflow-state invariants

### Working (load if needed)
- `docs/working/backlog.md` — Phase 20 contract for P20-T02
- `docs/working/tooling_notes.md` — source report describing the archived-ID reuse bug

### Packet Files
- `tasks/P20-T02-TASK-0136/task.md`
- `tasks/P20-T02-TASK-0136/plan.md`
- `tasks/P20-T02-TASK-0136/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** [adapter_id or none]
- **Secondary Adapters:** [adapter_ids or none]
- **Adapter Rationale:** n/a

## Excluded Context
- Review/close workflows beyond task-ID allocation — out of scope for this task
- Unrelated Phase 20 follow-up items — deferred until this packet is closed

## Context Sufficiency Note
The packet allocator implementation and its dedicated tests are sufficient to implement and verify this bug fix without loading unrelated services.
