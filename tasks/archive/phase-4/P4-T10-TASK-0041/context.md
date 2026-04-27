# Context: TASK-0041

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/agent_profiles.md`
- `docs/runtime/context_loading.md`

### Canonical (load for this task)
- `docs/canonical/cli_spec.md` — `model show` command purpose and output expectations
- `docs/canonical/workflow_spec.md` — model class usage and provider-agnostic routing guidance
- `docs/canonical/architecture.md` — model routing system constraints

### Working (load if needed)
- `docs/working/backlog.md` — P4-T10 scope and dependency
- `docs/working/current_focus.md` — active phase and immediate goals
- `docs/working/current_task.md` — active packet state for execution flow

### Packet Files
- `tasks/P4-T10-TASK-0041/task.md`
- `tasks/P4-T10-TASK-0041/plan.md`
- `tasks/P4-T10-TASK-0041/deliverable_spec.md`

## Excluded Context
- Phase 5 review/handoff implementation backlog: outside current Phase 4 command scope
- Unrelated task packet directories: excluded to keep context packet-local and minimal

## Context Sufficiency Note
These documents define command contract, model-routing constraints, and active sequencing context sufficiently to implement and validate `forge model show`.
