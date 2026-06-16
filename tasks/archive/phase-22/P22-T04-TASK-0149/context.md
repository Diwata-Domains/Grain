# Context: TASK-0149

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — preserve the thin-shell, existing-service action boundary

### Working (load if needed)
- `docs/working/current_focus.md` — confirms Phase 22 action-launch scope and deferrals
- `docs/working/backlog.md` — confirms this task’s boundary relative to later prompt/context work
- `docs/working/implementation_plan.md` — keeps the v0.3.0 sequence explicit

### Packet Files
- `tasks/P22-T04-TASK-0149/task.md`
- `tasks/P22-T04-TASK-0149/plan.md`
- `tasks/P22-T04-TASK-0149/deliverable_spec.md`
- `tasks/P22-T03-TASK-0148/results.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a

## Excluded Context
- prompt body previews and context bundle inspectors — those are later Phase 22 work
- non-code artifact workflow docs — launcher wiring is generic workflow plumbing, not adapter-specific behavior

## Context Sufficiency Note
The selected docs are sufficient because this task only needs the existing workflow, review, and close service surfaces plus the current TUI shell contract to add safe action launches.
