# Task: Phase 14 integration tests

## Metadata
- **ID:** TASK-0102
- **Status:** done
- **Phase:** Phase 14 — Document and Spreadsheet Adapters
- **Backlog:** P14-T04
- **Packet Path:** tasks/P14-T04-TASK-0102/
- **Dependencies:** TASK-0099, TASK-0100, TASK-0101
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
Write cross-adapter integration tests that verify all three document adapters (`SpreadsheetExtractor`, `DocsExtractor`, `PdfExtractor`) work correctly end-to-end through context assembly. Tests cover mixed-file-type bundles, graceful degradation in combination, and `grain context build` selecting document files when the appropriate adapter is active.

## Why This Task Exists
Individual extractor unit tests (in P14-T01 through P14-T03) verify extraction in isolation. This task verifies that all three extractors integrate correctly into the context assembly pipeline together — and that the full `grain context build` command works with mixed document and code file bundles.

## Scope
- Write `tests/test_document_adapters_integration.py`:
  - Mixed-type context bundle: task packet that references `.xlsx`, `.docx`, `.pdf`, and `.py` files — verify all are selected and extracted
  - `grain context build` with `spreadsheet_adapter` active: `.xlsx` and `.csv` files appear with extracted text in bundle
  - `grain context build` with `docs_adapter` active: `.docx`, `.md`, and `.pdf` files appear in bundle
  - Graceful degradation in bundle: a corrupt/unreadable `.pdf` in a bundle doesn't fail the whole build — returns marker and continues
  - `--format json` output includes extracted document content alongside code content
  - `--format text` output includes document sections cleanly
  - Context stats (`context_stats` in output) accurately counts document files by selection method
  - At least 12 new tests
- All test fixtures created in-memory — no binary files committed to the repo
- After all tests pass, update phase close docs and record final test count

## Constraints
- Tests must be hermetic — use temporary directories and synthetic file fixtures
- Do not test extractor internals again — integration tests only (rely on unit tests from T01–T03)
- If creating in-memory PDF fixtures requires a build-time tool, note it clearly in test setup comments

## Escalation Conditions
- If cross-adapter test reveals a context assembly contract gap (e.g. extractors not registering correctly), stop, fix in context_service, and record the change
