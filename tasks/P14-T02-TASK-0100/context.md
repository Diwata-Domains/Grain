# Context: TASK-0100

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — service layer conventions, context assembly pipeline
- `docs/canonical/product_scope.md` — FR-001 docs_adapter scope

### Runtime Config (load for this task)
- `docs/runtime/adapter_profiles.md` — existing docs_adapter profile to extend with .docx

### Working (load if needed)
- `docs/working/backlog.md` — Phase 14 task sequence

### Packet Files
- `tasks/P14-T02-TASK-0100/task.md`
- `tasks/P14-T02-TASK-0100/plan.md`
- `tasks/P14-T02-TASK-0100/deliverable_spec.md`

### Reference (scan for patterns, do not load fully)
- `src/grain/services/spreadsheet_extractor.py` — P14-T01 extractor pattern to follow
- `src/grain/services/context_service.py` — confirm wiring point for .docx

## Excluded Context
- PDF extractor (P14-T03) — not in scope
- Phase 13 onboard internals — not relevant
- Tree-sitter / graph internals — not applicable

## Context Sufficiency Note
Read P14-T01's `spreadsheet_extractor.py` result first — follow the same class/method pattern. The docs_adapter profile already exists in `adapter_profiles.md`; extend it rather than replacing it.
