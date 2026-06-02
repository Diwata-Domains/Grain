# Deliverable Spec: TASK-0153

## Required Output

### New Files
- `.docx` write service module(s) — safe propose/export implementation and structural summary support
- `.docx` workflow tests and fixtures — focused write-path verification

### Modified Files
- packet files for `TASK-0153`
- any shared exports or small helper surfaces needed for the `.docx` implementation

## Acceptance Checklist
- [ ] `.docx` propose and `export-as-new-file` behavior exists on top of the shared office-write contract
- [ ] the service emits a structural change summary suitable for later review-bundle wiring
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- spreadsheet mutation support
- CLI command surfaces for office writes
- in-place `.docx` `apply` behavior
