# Context: TASK-0070

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/cli_spec.md` — primary target; §5.1 (placeholder behavior), §6 (command groups), §12 (coverage summary)
- `docs/canonical/architecture.md` — §4.12 (Review/Gate Layer), §4.14 (Orchestration Service) for compatibility check

### Working (load if needed)
- `docs/working/v2_plan.md` — §9 (operator surface), §10 (runner stop conditions); §11 to be created
- `docs/working/open_questions.md` — check for any Sentinel-related unresolved questions; update if needed
- `docs/working/backlog.md` — update P8-T10 status

### Packet Files
- `tasks/P8-T10-TASK-0070/task.md`
- `tasks/P8-T10-TASK-0070/plan.md`
- `tasks/P8-T10-TASK-0070/deliverable_spec.md`

## Excluded Context
- product_scope.md — not needed; bridge contract is implementation-level
- workflow_spec.md — not needed; runner behavior already locked in v2_plan.md §10
- data_contracts.md — not needed; payload schema goes in v2_plan.md, not data_contracts
- src/ and tests/ — no implementation in this task

## Context Sufficiency Note
cli_spec.md (for command surface) and v2_plan.md §10 (for stop conditions) are sufficient to define the bridge contract without ambiguity.
