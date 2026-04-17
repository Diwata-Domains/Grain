# Plan: TASK-0099

## Approach

Follow the existing service pattern in `src/grain/services/`. Implement a focused extractor class, define the adapter profile, wire the file pattern into context assembly, and add the dependency. Use in-memory openpyxl workbooks in tests to avoid binary fixture files.

---

## Step 1 — Add `openpyxl` Dependency

In `pyproject.toml`:
- Add `"openpyxl>=3.1"` to the `dependencies` list

---

## Step 2 — Implement `SpreadsheetExtractor`

In `src/grain/services/spreadsheet_extractor.py`:
- `SpreadsheetExtractor` class
- `extract(path: Path) -> str` — dispatch on suffix:
  - `.xlsx` / `.xls`: open with `openpyxl.load_workbook(path, read_only=True, data_only=True)`, iterate sheets, emit text block per sheet: sheet name header, column headers row, data rows
  - `.csv`: open with `csv.reader`, emit headers + rows as text
- On any `Exception` during extraction: return `f"[spreadsheet_extractor: could not read {path.name} — {e}]"` — no raises
- Empty workbooks/files: return `f"[spreadsheet_extractor: {path.name} is empty]"`

---

## Step 3 — Define `spreadsheet_adapter` Profile

In `docs/runtime/adapter_profiles.md`, add a full profile entry:
- `adapter_id`: `spreadsheet_adapter`
- `domain_type`: `data`
- `applies_to`: Excel spreadsheets, CSV data files
- `relevant_file_patterns`: `**/*.xlsx`, `**/*.xls`, `**/*.csv`
- `ignore_file_patterns`: `node_modules/**`, `dist/**`
- `context_priority_rules`: prioritize sheets with headers; row data summarized if >100 rows
- `review_focus_hints`: data shape changes, new columns, structural shifts
- `default_model_bias`: `frontier_model` for structural reasoning, `open_model` for data formatting

---

## Step 4 — Wire into Context Assembly

In `src/grain/services/context_service.py` (or wherever file-pattern selection lives):
- Register `.xlsx`, `.xls`, `.csv` as file types that invoke `SpreadsheetExtractor.extract()` instead of raw `open().read()`
- The extracted text replaces the raw file content in the context bundle

---

## Step 5 — Tests

In `tests/test_spreadsheet_extractor.py`:
- Test `.xlsx` extraction: in-memory workbook with headers and rows → verify extracted text contains sheet name, headers, row values
- Test `.csv` extraction: in-memory StringIO → verify headers and rows in output
- Test empty workbook → returns empty marker string, no exception
- Test unreadable file path → returns error marker string, no exception
- Test multi-sheet workbook → all sheets appear in output
- Test `.xls` path with openpyxl fallback behavior
- Test context assembly includes extracted text for `.xlsx` file in bundle
- Test extracted text is included in context bundle for `.csv` file
- At least 8 tests

---

## Verification

- `.venv/bin/pip install openpyxl` (or `uv add openpyxl` and rebuild)
- `.venv/bin/pytest -q tests/test_spreadsheet_extractor.py`
- `.venv/bin/pytest -q`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0099`
