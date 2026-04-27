# Context: TASK-0058

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/adapter_profiles.md` — adapter pattern and priority rules used for context bias

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — context-preparation and packet execution constraints
- `docs/canonical/architecture.md` — context system boundaries and adapter integration model
- `docs/canonical/data_contracts.md` — packet metadata expectations and compatibility requirements

### Working (load if needed)
- `docs/working/backlog.md` — task sequence and dependency checks
- `docs/working/current_focus.md` — active phase priorities
- `docs/working/open_questions.md` — unresolved blocker checks

### Packet Files
- `tasks/P6-T05-TASK-0058/task.md`
- `tasks/P6-T05-TASK-0058/plan.md`
- `tasks/P6-T05-TASK-0058/deliverable_spec.md`

## Excluded Context
- Adapter review/test hint surfacing details are excluded in this packet because those are scoped to `P6-T06`.

## Context Sufficiency Note
This context is sufficient because the task only requires packet metadata + adapter profile consumption in context assembly and compatibility validation.
