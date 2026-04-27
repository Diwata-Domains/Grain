# Deliverable Spec: TASK-0099

## Required Output

### New Files
- `tasks/P14-T01-TASK-0099/task.md` ✓
- `tasks/P14-T01-TASK-0099/context.md` ✓
- `tasks/P14-T01-TASK-0099/plan.md` ✓
- `tasks/P14-T01-TASK-0099/deliverable_spec.md` ✓
- `tasks/P14-T01-TASK-0099/results.md` (filled during execute)
- `tasks/P14-T01-TASK-0099/handoff.md` (filled during execute)
- `src/grain/services/spreadsheet_extractor.py` — `SpreadsheetExtractor` class
- `tests/test_spreadsheet_extractor.py` — ≥ 8 tests

### Modified Files
- `pyproject.toml` — add `openpyxl>=3.1` to dependencies
- `docs/runtime/adapter_profiles.md` — full `spreadsheet_adapter` profile entry
- `src/grain/services/context_service.py` — wire `.xlsx`/`.xls`/`.csv` to extractor
- `docs/working/backlog.md` — mark P14-T01 done, set P14-T02 ready
- `docs/working/current_task.md` — update active task pointer

## Acceptance Checklist
- [ ] `SpreadsheetExtractor.extract()` returns text for `.xlsx` files (sheet name, headers, rows)
- [ ] `SpreadsheetExtractor.extract()` returns text for `.csv` files
- [ ] Empty or unreadable files return a warning string — no exceptions raised
- [ ] `spreadsheet_adapter` profile fully defined in `adapter_profiles.md`
- [ ] `.xlsx`/`.xls`/`.csv` files are selected and extracted in context assembly
- [ ] `openpyxl>=3.1` in `pyproject.toml` dependencies
- [ ] ≥ 8 new tests passing, all using in-memory fixtures (no binary files committed)
- [ ] Full test suite passing with no regressions
- [ ] `results.md` and `handoff.md` filled

## Not Required
- `docs_adapter` / `.docx` support (P14-T02)
- PDF reader (P14-T03)
- Cross-adapter integration tests (P14-T04)
