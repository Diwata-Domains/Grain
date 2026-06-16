# Deliverable Spec: TASK-0152

## Required Output

### New Files
- `src/grain/domain/office_writes.py` — shared office write contract types
- `src/grain/services/office_write_service.py` — shared safety-mode and review-bundle logic
- `tests/test_office_write_service.py` — focused contract and behavior tests

### Modified Files
- `src/grain/domain/__init__.py` — export the office-write domain types
- `tasks/P23-T01-TASK-0152/task.md` — packet metadata and scope
- `tasks/P23-T01-TASK-0152/results.md` — execution summary and verification notes

## Acceptance Checklist
- [x] shared office write contracts exist for artifact refs, requests, decisions, validators, and review bundles
- [x] one shared service resolves `propose`, `apply`, and `export-as-new-file` using the locked Phase 23 safety rules
- [x] focused tests cover safety-mode fallback behavior and review-bundle assembly
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- actual `.docx` mutation logic
- actual spreadsheet mutation logic
- CLI command surfaces for office writes
