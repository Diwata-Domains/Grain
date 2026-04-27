# Context: TASK-0045

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/context_loading.md`

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — review stage, closure requirements, and packet lifecycle rules
- `docs/canonical/architecture.md` — review/gate and validation-system boundaries
- `docs/canonical/cli_spec.md` — review command responsibilities and output expectations

### Working (load if needed)
- `docs/working/backlog.md` — confirms P5-T01 scope and dependency order
- `docs/working/current_focus.md` — phase sequencing and constraints

### Packet Files
- `tasks/P5-T01-TASK-0045/task.md`
- `tasks/P5-T01-TASK-0045/plan.md`
- `tasks/P5-T01-TASK-0045/deliverable_spec.md`

## Excluded Context
- Phase 4 packet implementation details: already complete and not needed for the review service contract
- Phase 5 CLI command wiring tasks: intentionally out of scope for this packet

## Context Sufficiency Note
These documents are sufficient to implement a review validation service and verify its behavior without broader repository context.
