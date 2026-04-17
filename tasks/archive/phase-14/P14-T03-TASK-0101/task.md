# Task: PDF document reader

## Metadata
- **ID:** TASK-0101
- **Status:** done
- **Phase:** Phase 14 — Document and Spreadsheet Adapters
- **Backlog:** P14-T03
- **Packet Path:** tasks/P14-T03-TASK-0101/
- **Dependencies:** TASK-0100
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
Implement `PdfExtractor` that reads `.pdf` files using `pdfplumber` and returns extracted text content. Handles graceful degradation for layout-heavy or image-only PDFs. Wires `.pdf` into the `docs_adapter` context assembly. Adds `pdfplumber>=0.11` to project dependencies.

## Why This Task Exists
PDFs are a common format for specs, reports, design documents, and reference materials. Grain must be able to include PDF text content in context bundles so agents can reason about these files without manual copy-paste.

## Scope
- Implement `src/grain/services/pdf_extractor.py`:
  - `PdfExtractor` class with `extract(path: Path) -> str` method
  - Open with `pdfplumber.open(path)`, iterate pages, extract `.extract_text()` per page
  - Join pages with `\n\n--- Page N ---\n\n` separators
  - If a page returns `None` from `extract_text()`: include a `[page N: no extractable text]` marker
  - If all pages yield no text: return `f"[pdf_extractor: {path.name} — no extractable text (may be image-only or layout-heavy)]"`
  - On any `Exception`: return `f"[pdf_extractor: could not read {path.name} — {e}]"` — no raises
- Add `.pdf` to `docs_adapter` profile in `docs/runtime/adapter_profiles.md` (under same adapter, since PDFs are document content)
- Wire `.pdf` patterns into context assembly to invoke `PdfExtractor.extract()`
- Add `pdfplumber>=0.11` to `dependencies` in `pyproject.toml`
- Tests: ≥ 8 (use `pdfplumber`-compatible in-memory PDF fixtures via `reportlab` or pre-generated minimal PDFs as bytes — no binary committed files)

## Constraints
- Extraction is read-only — never modify source PDF files
- No OCR in this task — text extraction only from `pdfplumber` (text-layer PDFs only). OCR is a future enhancement.
- Graceful degradation is mandatory — never propagate exceptions to callers
- If synthetic PDF fixture generation requires an additional library (`reportlab`, `fpdf2`), add it as a `dev` or `test` optional dependency, not a core one

## Escalation Conditions
- If creating minimal synthetic PDF fixtures without a third-party library is not feasible, stop and log an open question about test fixture approach
- If `pdfplumber` version conflicts with existing dependencies, stop and log
