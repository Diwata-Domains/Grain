# Context: TASK-0094

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — CLI command registration pattern, service layer conventions
- `docs/canonical/product_scope.md` — FR-013 existing project adoption scope

### Working (load if needed)
- `docs/working/backlog.md` — Phase 13 task sequence and dependencies
- `docs/working/current_focus.md` — active phase goals

### Packet Files
- `tasks/P13-T01-TASK-0094/task.md`
- `tasks/P13-T01-TASK-0094/plan.md`
- `tasks/P13-T01-TASK-0094/deliverable_spec.md`

### Reference (scan for patterns, do not load fully)
- `src/grain/cli/init.py` — existing CLI command pattern to follow
- `src/grain/services/init_service.py` — existing service pattern to follow

## Excluded Context
- Phase 12 loop internals (not relevant)
- Tree-sitter / graph service internals (not needed for scaffold)
- P13-T02+ scanner and doc generation (not in scope for this task)

## Context Sufficiency Note
This context is sufficient to implement the CLI scaffold command and service. The init command (`grain init`) is the closest analog — follow the same registration, output, and service-layer patterns.
