# Deliverable Spec: TASK-0100

## Required Output

### New Files
- `tasks/P14-T02-TASK-0100/task.md` ✓
- `tasks/P14-T02-TASK-0100/context.md` ✓
- `tasks/P14-T02-TASK-0100/plan.md` ✓
- `tasks/P14-T02-TASK-0100/deliverable_spec.md` ✓
- `tasks/P14-T02-TASK-0100/results.md` (filled during execute)
- `tasks/P14-T02-TASK-0100/handoff.md` (filled during execute)
- `src/grain/services/docs_extractor.py` — `DocsExtractor` class
- `tests/test_docs_extractor.py` — ≥ 8 tests

### Modified Files
- `pyproject.toml` — add `python-docx>=1.1` to dependencies
- `docs/runtime/adapter_profiles.md` — extend `docs_adapter` profile with .docx patterns
- `src/grain/services/context_service.py` — wire `.docx` to `DocsExtractor`
- `docs/working/backlog.md` — mark P14-T02 done, set P14-T03 ready
- `docs/working/current_task.md` — update active task pointer

## Acceptance Checklist
- [ ] `DocsExtractor.extract()` returns structured text for `.docx` (headings, paragraphs, tables)
- [ ] `DocsExtractor.extract()` returns raw text for `.md` files
- [ ] Empty or unreadable files return a warning string — no exceptions raised
- [ ] `docs_adapter` profile includes `.docx` in `relevant_file_patterns`
- [ ] `.docx` files are selected and extracted in context assembly
- [ ] `python-docx>=1.1` in `pyproject.toml` dependencies
- [ ] ≥ 8 new tests passing, all using in-memory fixtures
- [ ] Full test suite passing with no regressions
- [ ] `results.md` and `handoff.md` filled

## Not Required
- PDF reader (P14-T03)
- Cross-adapter integration tests (P14-T04)
