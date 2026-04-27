# Context: TASK-0076

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/cli_spec.md` — §6.7 adapter command surface expectations
- `docs/canonical/architecture.md` — adapter system and orchestration boundaries
- `docs/canonical/workflow_spec.md` — orchestration interaction boundary (proposal-only)

### Working (load if needed)
- `docs/working/backlog.md` — Phase 9 sequencing and readiness
- `docs/working/current_focus.md` — active priorities

### Packet Files
- `tasks/P9-T05-TASK-0076/task.md`
- `tasks/P9-T05-TASK-0076/plan.md`
- `tasks/P9-T05-TASK-0076/deliverable_spec.md`

## Excluded Context
- `grain orchestrate` command implementation is excluded (belongs to `P9-T06`).
- Phase-level orchestration service changes are excluded (already covered by `P9-T04`).

## Context Sufficiency Note
This context is sufficient to implement adapter inspection commands with stable text/json output while preserving phase boundaries.
