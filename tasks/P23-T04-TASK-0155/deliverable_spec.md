# Deliverable Spec: TASK-0155

## Required Output

### New Files
- office artifact validator service/module(s) — structure, reference, and policy checks
- office artifact review-bundle service/module(s) — shared assembly over `.docx` and spreadsheet write results
- focused validator/review tests and fixtures

### Modified Files
- packet files for `TASK-0155`
- any shared office-write exports or helper surfaces needed by the validator layer

## Acceptance Checklist
- [ ] `.docx` and spreadsheet write outputs can be converted into one shared office review-bundle shape
- [ ] the first structure, reference, and policy validators exist and feed residual-risk handling correctly
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- CLI mutation entrypoints
- TUI-specific observability panels
- end-to-end office smoke docs
