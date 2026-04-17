# Deliverable Spec: TASK-0102

## Required Output

### New Files
- `tasks/P14-T04-TASK-0102/task.md` ✓
- `tasks/P14-T04-TASK-0102/context.md` ✓
- `tasks/P14-T04-TASK-0102/plan.md` ✓
- `tasks/P14-T04-TASK-0102/deliverable_spec.md` ✓
- `tasks/P14-T04-TASK-0102/results.md` (filled during execute)
- `tasks/P14-T04-TASK-0102/handoff.md` (filled during execute)
- `tests/test_document_adapters_integration.py` — ≥ 12 integration tests

### Modified Files
- `docs/working/backlog.md` — mark P14-T04 done, note Phase 14 ready to close
- `docs/working/current_task.md` — clear active task pointer after phase close

## Acceptance Checklist
- [ ] `.xlsx` files: extracted text appears in `grain context build` output
- [ ] `.csv` files: extracted text appears in `grain context build` output
- [ ] `.docx` files: headings/paragraphs appear in `grain context build` output
- [ ] `.pdf` files (text-layer): page content appears in `grain context build` output
- [ ] Corrupt/image-only `.pdf`: bundle succeeds with degradation marker, no crash
- [ ] Mixed-type bundle (code + documents): all file types extracted correctly
- [ ] `--format json` output includes document file content
- [ ] `context_stats` correctly counts document files
- [ ] ≥ 12 new integration tests passing
- [ ] Full test suite passing with no regressions
- [ ] `results.md` and `handoff.md` filled

## Not Required
- Extractor unit tests (covered in P14-T01, T02, T03)
- Phase 15 semantic enrichment work
