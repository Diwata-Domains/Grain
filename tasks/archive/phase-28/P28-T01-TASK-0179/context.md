# Context: TASK-0179

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/cli_spec.md` — `grain verify` contract and deferred bridge surface

### Working (load if needed)
- `docs/working/backlog.md` — Phase 28 task contract
- `docs/working/v2_plan.md` — deferred verification payload/runner contract inherited from earlier planning

### Packet Files
- `tasks/P28-T01-TASK-0179/task.md`
- `tasks/P28-T01-TASK-0179/plan.md`
- `tasks/P28-T01-TASK-0179/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** this task changes CLI and service code for the verification bridge.

## Excluded Context
- Assay internals or remote services — out of scope for the first submit bridge
- Workflow gate logic — reserved for `P28-T04`

## Context Sufficiency Note
The CLI spec, deferred verification contract, and current CLI/service patterns are sufficient for the submit bridge slice.
