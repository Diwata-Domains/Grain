# Plan: TASK-0102

## Approach

Model tests on `test_context_build_cmd.py`. Use pytest `tmp_path` fixtures and create synthetic document files in-memory. Test each adapter via `grain context build`, then test mixed-type scenarios.

---

## Step 1 — Review Existing Integration Test Pattern

Read `tests/test_context_build_cmd.py` to confirm:
- How task manifests are constructed for test scenarios
- How `grain context build` is invoked in tests
- How bundle output is asserted

---

## Step 2 — Write Spreadsheet Integration Tests (3 tests)

In `tests/test_document_adapters_integration.py`:
- `test_context_build_includes_xlsx_extracted_text` — `.xlsx` file in manifest → extracted text appears in bundle output
- `test_context_build_includes_csv_extracted_text` — `.csv` file → extracted text in bundle
- `test_context_build_json_includes_spreadsheet_content` — `--format json` bundle contains extracted spreadsheet text

---

## Step 3 — Write Docs/PDF Integration Tests (4 tests)

- `test_context_build_includes_docx_extracted_text` — `.docx` in manifest → headings and paragraphs in bundle
- `test_context_build_includes_pdf_extracted_text` — text-layer `.pdf` → page content in bundle
- `test_context_build_pdf_degradation_does_not_fail_bundle` — image-only/corrupt `.pdf` in manifest → bundle succeeds, degradation marker in output
- `test_context_build_includes_md_and_docx_together` — mixed `.md` + `.docx` in same bundle → both appear

---

## Step 4 — Write Mixed-Type Integration Tests (3 tests)

- `test_context_build_mixed_code_and_spreadsheet` — `.py` + `.xlsx` in same bundle → both extracted correctly
- `test_context_build_mixed_code_and_pdf` — `.py` + `.pdf` → both in bundle
- `test_context_build_context_stats_counts_document_files` — `context_stats` in JSON output reflects document file count and selection method

---

## Step 5 — Write Cross-Adapter Edge Tests (2+ tests)

- `test_context_build_all_three_document_types` — `.xlsx`, `.docx`, `.pdf` all in one bundle → all extracted
- Any additional edge case caught during implementation

---

## Step 6 — Phase Close Working Doc Updates

After all tests pass:
- Update `docs/working/backlog.md` — mark P14-T04 done
- Update `docs/working/current_task.md` — clear active task
- Record final test count in `results.md`

---

## Verification

- `.venv/bin/pytest -q tests/test_document_adapters_integration.py`
- `.venv/bin/pytest -q` (full suite, no regressions)
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0102`
