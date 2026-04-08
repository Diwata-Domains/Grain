# Context: TASK-0062

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/product_scope.md` — onboarding is prompt-first and agent-assisted; keep scope/model assumptions aligned
- `docs/canonical/workflow_spec.md` — packet lifecycle, prompt authority boundaries, and single-task execution constraints
- `docs/canonical/architecture.md` — initialization/scaffolding and CLI-service responsibility boundaries

### Working (load if needed)
- `docs/working/backlog.md` — active Phase 7 backlog item and dependencies
- `docs/working/current_focus.md` — immediate phase priorities and out-of-scope boundaries
- `docs/working/v2_onboarding.md` — locked planning decisions for this onboarding slice
- `docs/working/open_questions.md` — confirm no unresolved blockers

### Packet Files
- `tasks/P7-T02-TASK-0062/task.md`
- `tasks/P7-T02-TASK-0062/plan.md`
- `tasks/P7-T02-TASK-0062/deliverable_spec.md`

## Excluded Context
- Existing-project adoption implementation details (`P7-T07`) are excluded because this task is new-project onboarding only.
- Phase 7 tasks after `P7-T03` are excluded to keep this packet narrow.

## Context Sufficiency Note
These sources are sufficient to implement the prompt entrypoint and compatibility guidance without expanding into unrelated onboarding implementation tasks.
