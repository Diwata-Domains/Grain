# Context: TASK-0101

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — service layer conventions

### Runtime Config (load for this task)
- `docs/runtime/adapter_profiles.md` — docs_adapter profile (extended in P14-T02) to further extend with .pdf

### Working (load if needed)
- `docs/working/backlog.md` — Phase 14 task sequence

### Packet Files
- `tasks/P14-T03-TASK-0101/task.md`
- `tasks/P14-T03-TASK-0101/plan.md`
- `tasks/P14-T03-TASK-0101/deliverable_spec.md`

### Reference (scan for patterns, do not load fully)
- `src/grain/services/spreadsheet_extractor.py` — extractor class pattern
- `src/grain/services/docs_extractor.py` — P14-T02 pattern to follow
- `src/grain/services/context_service.py` — confirm .pdf wiring point

## Excluded Context
- Phase 13 onboard internals — not relevant
- Spreadsheet adapter internals (already done) — reference pattern only
- Cross-adapter integration tests (P14-T04) — not in scope

## Context Sufficiency Note
Read `docs_extractor.py` from P14-T02 for the exact pattern. Add `.pdf` to `docs_adapter` rather than creating a new adapter — PDFs are document content, not a separate domain.
