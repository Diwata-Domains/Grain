# Context: TASK-0130

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/data_contracts.md` — adapter contract and discovery rules
- `docs/canonical/architecture.md` — adapter-layer trust boundaries
- `docs/canonical/cli_spec.md` — current adapter command surface baseline

### Working (load if needed)
- `docs/working/backlog.md` — Phase 19 task scope and ordering
- `docs/working/open_questions.md` — resolved Q19 hosting/trust model

### Packet Files
- `tasks/P19-T02-TASK-0130/task.md`
- `tasks/P19-T02-TASK-0130/plan.md`
- `tasks/P19-T02-TASK-0130/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** docs_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** This task defines and validates a filesystem package contract before any runtime install behavior exists.

## Excluded Context
- install command implementation — deferred to P19-T03
- registry scaffold/CI docs — deferred to P19-T04 and P19-T05

## Context Sufficiency Note
The resolved Phase 19 trust contract and the existing adapter-profile parser are sufficient to implement the first package-validation surface without widening into install mechanics.
