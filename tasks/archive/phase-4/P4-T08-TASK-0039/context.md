# Context: TASK-0039

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/agent_profiles.md`
- `docs/runtime/context_loading.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — model routing system requirements and model profile domain contract
- `docs/canonical/workflow_spec.md` — model class usage and escalation behavior
- `docs/canonical/cli_spec.md` — model command responsibilities and provider-agnostic rule

### Working (load if needed)
- `docs/working/backlog.md` — P4-T08 scope and dependencies
- `docs/working/current_focus.md` — confirms P4-T08 as the next target
- `docs/working/open_questions.md` — Q8 resolved: `agent_profiles.md` is the config source

### Packet Files
- `tasks/P4-T08-TASK-0039/task.md`
- `tasks/P4-T08-TASK-0039/plan.md`
- `tasks/P4-T08-TASK-0039/deliverable_spec.md`

## Excluded Context
- Phase 5 review/handoff implementation tasks: not needed for config loader implementation
- Unrelated task packets: excluded to keep context narrow per runtime rules

## Context Sufficiency Note
These sources define loader scope, routing constraints, and execution order sufficiently for a narrow P4-T08 implementation and review.
