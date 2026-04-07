# Context: TASK-0055

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/adapter_profiles.md` — source contract for adapter profile fields

### Canonical (load for this task)
- `docs/canonical/architecture.md` — domain/service separation and model-agnostic constraints
- `docs/canonical/workflow_spec.md` — packet lifecycle and execution-stage constraints
- `docs/canonical/product_scope.md` — boundary that Forge orchestrates and remains adapter-neutral by default

### Working (load if needed)
- `docs/working/backlog.md` — task selection and dependency sequencing
- `docs/working/current_focus.md` — current phase priorities
- `docs/working/implementation_plan.md` — phase ordering context
- `docs/working/open_questions.md` — blocker check

### Packet Files
- `tasks/P6-T02-TASK-0055/task.md`
- `tasks/P6-T02-TASK-0055/plan.md`
- `tasks/P6-T02-TASK-0055/deliverable_spec.md`

## Excluded Context
- `src/forge/services/context_service.py` and CLI command modules are excluded because this task is domain-only and does not change runtime behavior.

## Context Sufficiency Note
This document set is sufficient because the task only needs the adapter field contract and established domain-model patterns, without parser or service changes.
