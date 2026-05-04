# Context: TASK-0150

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — preserve the thin-shell, existing-service preview boundary

### Working (load if needed)
- `docs/working/current_focus.md` — confirms Phase 22 preview/detail scope
- `docs/working/backlog.md` — confirms this task’s boundary before the Phase 22 validation/docs pass
- `docs/working/implementation_plan.md` — keeps the v0.3.0 sequence explicit

### Packet Files
- `tasks/P22-T05-TASK-0150/task.md`
- `tasks/P22-T05-TASK-0150/plan.md`
- `tasks/P22-T05-TASK-0150/deliverable_spec.md`
- `tasks/P22-T04-TASK-0149/results.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a

## Excluded Context
- full prompt bodies and full context markdown exports — this task only needs compact operator previews
- non-code workflow docs — the preview/detail plumbing is generic Phase 22 TUI work

## Context Sufficiency Note
The selected docs are sufficient because this task only needs the existing prompt, context, and workflow surfaces plus the current TUI shell contract to add compact preview/detail panels.
