# Context: TASK-0135

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md` — workflow and repo-operation constraints

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — intended Execute -> Review -> Close flow
- `docs/canonical/data_contracts.md` — workflow-state and machine-readable output expectations

### Working (load if needed)
- `docs/working/backlog.md` — Phase 20 backlog contract for P20-T01
- `docs/working/tooling_notes.md` — local report that seeded this task

### Packet Files
- `tasks/P20-T01-TASK-0135/task.md`
- `tasks/P20-T01-TASK-0135/plan.md`
- `tasks/P20-T01-TASK-0135/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a

## Excluded Context
- Assay feature-planning docs — out of scope for this Grain workflow-state fix
- Unrelated Phase 20 follow-up items — deferred until P20-T01 is complete

## Context Sufficiency Note
The workflow service, runner service, and existing workflow/prompt tests provide enough context to implement and verify this routing fix without touching unrelated subsystems.
