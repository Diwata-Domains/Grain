# Context: TASK-0099

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — service layer conventions, context assembly pipeline
- `docs/canonical/product_scope.md` — FR-002 spreadsheet adapter scope

### Runtime Config (load for this task)
- `docs/runtime/adapter_profiles.md` — existing adapter profile format to extend

### Working (load if needed)
- `docs/working/backlog.md` — Phase 14 task sequence
- `docs/working/current_focus.md` — active phase goals

### Packet Files
- `tasks/P14-T01-TASK-0099/task.md`
- `tasks/P14-T01-TASK-0099/plan.md`
- `tasks/P14-T01-TASK-0099/deliverable_spec.md`

### Reference (scan for patterns, do not load fully)
- `src/grain/services/context_service.py` — how context assembly selects files by pattern, where to wire new file types
- `src/grain/adapters/adapter_config.py` — adapter registration pattern

## Excluded Context
- Phase 13 onboard internals (not relevant)
- Tree-sitter / graph service (not applicable to spreadsheet extraction)
- P14-T02+ docs_adapter and PDF extractor (not in scope for this task)

## Context Sufficiency Note
This context is sufficient to implement `SpreadsheetExtractor`, define the adapter profile, and wire file patterns into the context pipeline. Check `context_service.py` and `adapter_config.py` briefly to confirm the exact wiring points before implementing.
