# Context: TASK-0180

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/cli_spec.md` — `grain verify status` contract

### Working (load if needed)
- `docs/working/backlog.md` — Phase 28 task contract
- `docs/working/v2_plan.md` — deferred verification bridge notes

### Packet Files
- `tasks/P28-T02-TASK-0180/task.md`
- `tasks/P28-T02-TASK-0180/plan.md`
- `tasks/P28-T02-TASK-0180/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** this task extends the verification CLI and service layer.

## Excluded Context
- Verification ingest payload handling — reserved for `P28-T03`
- Workflow close gates — reserved for `P28-T04`

## Context Sufficiency Note
The existing verification request artifact, CLI spec, and current bridge implementation are sufficient for the status slice.
