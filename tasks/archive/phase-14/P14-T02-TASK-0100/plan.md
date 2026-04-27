# Plan: TASK-0100

## Approach

Follow the same pattern established in P14-T01 (`SpreadsheetExtractor`). Add `python-docx`, implement the extractor, extend the adapter profile, wire context assembly, and test with in-memory `.docx` fixtures.

---

## Step 1 — Add `python-docx` Dependency

In `pyproject.toml`:
- Add `"python-docx>=1.1"` to the `dependencies` list

---

## Step 2 — Implement `DocsExtractor`

In `src/grain/services/docs_extractor.py`:
- `DocsExtractor` class
- `extract(path: Path) -> str` — dispatch on suffix:
  - `.docx`: open with `python_docx.Document(path)`, iterate paragraphs and tables
    - Headings: prefix with `#` marks matching heading level (e.g. `## Section Title`)
    - Paragraphs: emit as plain text lines
    - Tables: emit each row as pipe-delimited cells (`| cell1 | cell2 |`)
  - `.md`: read raw text (already plain text, no transformation needed)
- On any `Exception`: return `f"[docs_extractor: could not read {path.name} — {e}]"` — no raises
- Empty document: return `f"[docs_extractor: {path.name} is empty]"`

---

## Step 3 — Extend `docs_adapter` Profile

In `docs/runtime/adapter_profiles.md`, in the existing `docs_adapter` entry:
- Add `**/*.docx` to `relevant_file_patterns`
- Update `context_priority_rules` to note `.docx` content is extracted via `DocsExtractor`
- Update `review_focus_hints` to cover document content changes

---

## Step 4 — Wire into Context Assembly

In `src/grain/services/context_service.py`:
- Register `.docx` as a file type that invokes `DocsExtractor.extract()` instead of raw read
- `.md` files already read as plain text — verify no change needed, or unify under `DocsExtractor`

---

## Step 5 — Tests

In `tests/test_docs_extractor.py`:
- Test `.docx` with headings → verify heading markers appear in output
- Test `.docx` with paragraphs → verify paragraph text in output
- Test `.docx` with a table → verify pipe-delimited rows in output
- Test empty `.docx` → returns empty marker string, no exception
- Test unreadable path → returns error marker string, no exception
- Test `.md` extraction → returns raw file content
- Test context assembly includes extracted text for `.docx` in bundle
- At least 8 tests, all using in-memory fixtures

---

## Verification

- `.venv/bin/pip install python-docx` (or rebuild with updated pyproject.toml)
- `.venv/bin/pytest -q tests/test_docs_extractor.py`
- `.venv/bin/pytest -q`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0100`
