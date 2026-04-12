# Plan: TASK-0101

## Approach

Follow the same extractor pattern from P14-T01 and P14-T02. Add `pdfplumber`, implement `PdfExtractor`, extend `docs_adapter` profile with `.pdf`, wire into context assembly. For tests, use the minimal valid PDF bytes approach (`%PDF-1.4 ...`) or `fpdf2` as a test-only dependency — confirm the lightest option that produces readable fixtures.

---

## Step 1 — Add `pdfplumber` Dependency

In `pyproject.toml`:
- Add `"pdfplumber>=0.11"` to the `dependencies` list
- If a PDF generation library is needed for test fixtures (e.g. `fpdf2`), add it under `[project.optional-dependencies]` dev group — not core

---

## Step 2 — Implement `PdfExtractor`

In `src/grain/services/pdf_extractor.py`:
- `PdfExtractor` class
- `extract(path: Path) -> str`:
  - Open with `pdfplumber.open(str(path))`
  - Iterate `pdf.pages` with index `i`
  - Per page: call `page.extract_text()` → if `None` or empty, emit `[page {i+1}: no extractable text]`
  - Join page texts with `\n\n--- Page {i+1} ---\n\n`
  - If all pages have no text: return image-only/layout-heavy marker
  - Wrap entire logic in `try/except Exception as e`: return error marker on failure

---

## Step 3 — Extend `docs_adapter` Profile

In `docs/runtime/adapter_profiles.md`, in `docs_adapter` entry:
- Add `**/*.pdf` to `relevant_file_patterns`
- Note: PDF extraction is best-effort — image-only PDFs return a degradation marker
- Update `context_priority_rules` to note partial extraction behavior

---

## Step 4 — Wire into Context Assembly

In `src/grain/services/context_service.py`:
- Register `.pdf` as a file type that invokes `PdfExtractor.extract()`

---

## Step 5 — Tests

In `tests/test_pdf_extractor.py`:
- Test text-layer PDF → verify page content appears in output
- Test multi-page PDF → verify page separators appear
- Test image-only/empty-text PDF → returns degradation marker, no exception
- Test corrupt/unreadable path → returns error marker, no exception
- Test context assembly includes extracted text for `.pdf` in bundle
- Test single-page PDF returns content without spurious separators
- Test that page N marker appears for pages with no extractable text
- At least 8 tests

---

## Verification

- `.venv/bin/pip install pdfplumber` (or rebuild)
- `.venv/bin/pytest -q tests/test_pdf_extractor.py`
- `.venv/bin/pytest -q`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0101`
