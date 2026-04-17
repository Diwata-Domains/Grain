# Context: TASK-0095

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/product_scope.md` — FR-013 existing-project adoption scope
- `docs/canonical/architecture.md` — services/domain layering and read-only scan behavior
- `docs/canonical/workflow_spec.md` — task execution and packet lifecycle boundaries

### Working (load if needed)
- `docs/working/backlog.md` — P13 sequencing and dependencies
- `docs/working/current_focus.md` — active phase priorities
- `docs/working/open_questions.md` — blocker check
- `docs/working/change_proposals.md` — canonical change routing guardrail

### Packet Files
- `tasks/P13-T02-TASK-0095/task.md`
- `tasks/P13-T02-TASK-0095/plan.md`
- `tasks/P13-T02-TASK-0095/deliverable_spec.md`

## Excluded Context
- P13-T03 doc generation implementation details (not part of scanner service task)
- Phase 14 adapter extraction internals (out of scope)

## Context Sufficiency Note
The selected docs and local code patterns are sufficient to implement a deterministic scanner service and validate its outputs without changing canonical contracts.
