# Context: TASK-0056

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/adapter_profiles.md` — adapter contract and profile section shape
- `docs/runtime/agent_profiles.md` — reference pattern for markdown config parsing style

### Canonical (load for this task)
- `docs/canonical/architecture.md` — adapter boundary and service/domain separation
- `docs/canonical/workflow_spec.md` — task lifecycle and execution constraints
- `docs/canonical/product_scope.md` — model-agnostic and orchestration-only product boundaries

### Working (load if needed)
- `docs/working/backlog.md` — task selection/dependencies for P6 sequence
- `docs/working/current_focus.md` — active phase priorities
- `docs/working/open_questions.md` — blocker check
- `docs/working/implementation_plan.md` — phase dependency context

### Packet Files
- `tasks/P6-T03-TASK-0056/task.md`
- `tasks/P6-T03-TASK-0056/plan.md`
- `tasks/P6-T03-TASK-0056/deliverable_spec.md`

## Excluded Context
- `src/forge/services/context_service.py` and packet validator modules are excluded because this task only introduces adapter profile loading.

## Context Sufficiency Note
This context is sufficient because implementation only requires adapter profile contract details and existing loader patterns.
