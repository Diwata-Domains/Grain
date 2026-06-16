# Context: TASK-0154

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/working/current_focus.md` — Phase 23 safety rules and writable office scope
- `docs/working/backlog.md` — `P23-T03` scope and dependencies
- `tasks/P23-T01-TASK-0152/results.md` — shared office-write contract decisions from the prior task

### Working (load if needed)
- `docs/working/implementation_plan.md` — Phase 23 sequencing
- `tasks/P23-T02-TASK-0153/results.md` — `.docx` artifact-specific pattern for the prior sibling task

### Packet Files
- `tasks/P23-T03-TASK-0154/task.md`
- `tasks/P23-T03-TASK-0154/plan.md`
- `tasks/P23-T03-TASK-0154/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a

## Excluded Context
- `.docx` mutation implementation details — already handled in `P23-T02`
- validator-pipeline and CLI wiring work — deferred to `P23-T04` and `P23-T05`

## Context Sufficiency Note
The Phase 23 planning docs, the shared contract task results, and the prior `.docx` sibling task are sufficient to implement the first spreadsheet propose/export workflow without pulling in later CLI or validator-pipeline surfaces.
