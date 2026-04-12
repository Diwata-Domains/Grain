# Deliverable Spec: TASK-0101

## Required Output

### New Files
- `tasks/P14-T03-TASK-0101/task.md` ✓
- `tasks/P14-T03-TASK-0101/context.md` ✓
- `tasks/P14-T03-TASK-0101/plan.md` ✓
- `tasks/P14-T03-TASK-0101/deliverable_spec.md` ✓
- `tasks/P14-T03-TASK-0101/results.md` (filled during execute)
- `tasks/P14-T03-TASK-0101/handoff.md` (filled during execute)
- `src/grain/services/pdf_extractor.py` — `PdfExtractor` class
- `tests/test_pdf_extractor.py` — ≥ 8 tests

### Modified Files
- `pyproject.toml` — add `pdfplumber>=0.11` to dependencies
- `docs/runtime/adapter_profiles.md` — extend `docs_adapter` profile with .pdf patterns and degradation note
- `src/grain/services/context_service.py` — wire `.pdf` to `PdfExtractor`
- `docs/working/backlog.md` — mark P14-T03 done, set P14-T04 ready
- `docs/working/current_task.md` — update active task pointer

## Acceptance Checklist
- [ ] `PdfExtractor.extract()` returns text content for text-layer PDFs
- [ ] Multi-page PDFs include page separators in output
- [ ] Image-only or layout-heavy PDFs return degradation marker string — no exception
- [ ] Unreadable files return error marker string — no exception
- [ ] `docs_adapter` profile includes `**/*.pdf` in `relevant_file_patterns`
- [ ] `.pdf` files are selected and extracted in context assembly
- [ ] `pdfplumber>=0.11` in `pyproject.toml` dependencies
- [ ] ≥ 8 new tests passing
- [ ] Full test suite passing with no regressions
- [ ] `results.md` and `handoff.md` filled

## Not Required
- OCR for image-only PDFs (future enhancement)
- Cross-adapter integration tests (P14-T04)
