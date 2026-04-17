# Task: `spreadsheet_adapter` extraction service

## Metadata
- **ID:** TASK-0099
- **Status:** done
- **Phase:** Phase 14 — Document and Spreadsheet Adapters
- **Backlog:** P14-T01
- **Packet Path:** tasks/P14-T01-TASK-0099/
- **Dependencies:** TASK-0098 (Phase 13 close)
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
Implement `SpreadsheetExtractor` that reads `.xlsx`, `.xls`, and `.csv` files and returns their content as readable text. Define the full `spreadsheet_adapter` profile in `adapter_profiles.md`. Wire the file patterns into context assembly. Add `openpyxl>=3.1` to project dependencies.

## Why This Task Exists
Phase 14 makes Grain context-aware for document and spreadsheet files. The spreadsheet adapter is the first of three document-type extractors. Operators frequently work with Excel and CSV data files — context assembly must be able to include their content the same way it includes code and markdown.

## Scope
- Implement `src/grain/services/spreadsheet_extractor.py`:
  - `SpreadsheetExtractor` class with `extract(path: Path) -> str` method
  - `.xlsx` / `.xls`: use `openpyxl` — extract sheet names, column headers, and row data as formatted text (one section per sheet)
  - `.csv`: use stdlib `csv` — extract headers and rows as formatted text
  - Returns empty string (with warning) for empty or unreadable files — never raises on content errors
- Add full `spreadsheet_adapter` profile to `docs/runtime/adapter_profiles.md`:
  - `adapter_id`: `spreadsheet_adapter`
  - `relevant_file_patterns`: `**/*.xlsx`, `**/*.xls`, `**/*.csv`
  - context priority, review focus, and build hints
- Wire file patterns into context assembly so `.xlsx`/`.xls`/`.csv` files are selected when `spreadsheet_adapter` is active
- Add `openpyxl>=3.1` to `dependencies` in `pyproject.toml`
- Tests: ≥ 8 (use synthetic in-memory fixture files via `openpyxl` — do not commit binary test fixtures)

## Constraints
- Extraction is read-only — never modify source files
- `.xls` (legacy format): if `openpyxl` cannot read it, return a graceful warning string rather than raising
- Do not add OCR or image extraction — text content only
- Synthetic test fixtures must be created in-memory in test setup, not committed as binary files

## Escalation Conditions
- If context assembly wiring requires a contract change to how adapters register file patterns, stop and log a change proposal
- If `openpyxl` cannot handle `.xls` without `xlrd` and adding `xlrd` has licensing concerns, stop and log open question
