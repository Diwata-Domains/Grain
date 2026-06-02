# Context: TASK-0157

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — packet lifecycle, review gates, and file-backed workflow rules for operator flows

### Working (load if needed)
- `docs/working/backlog.md` — P23-T06 scope, dependencies, and expected end-to-end coverage
- `docs/working/implementation_plan.md` — Phase 23 sequence and the role of the office smoke/docs closeout task

### Packet Files
- `tasks/P23-T06-TASK-0157/task.md`
- `tasks/P23-T06-TASK-0157/plan.md`
- `tasks/P23-T06-TASK-0157/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a

## Excluded Context
- TUI and desktop integration surfaces are excluded because this task is limited to the office CLI/operator flow
- future adapter work (`obsidian_adapter`, `database_adapter`, `crawler_adapter`) is excluded because Phase 23 is only about writable office artifacts

## Context Sufficiency Note
The workflow spec plus the Phase 23 backlog/plan are sufficient because this task is only hardening and documenting the already-implemented office CLI path.
