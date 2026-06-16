# Deliverable Spec: TASK-0157

## Required Output

### New Files
- no new product modules required; this task is expected to harden tests and docs around the existing office CLI slice

### Modified Files
- `tests/test_office_cmd.py` and/or related focused test files — add smoke-flow or end-to-end coverage for the office CLI path
- `README.md` and/or runtime guidance — document the first office-artifact workflow, review artifact expectations, and validator surface
- `tasks/P23-T06-TASK-0157/*` — complete the packet review artifacts for the office closeout slice

## Acceptance Checklist
- [ ] end-to-end or smoke-flow coverage exists for the current `.docx` and spreadsheet office CLI path
- [ ] docs explain how to use the office commands within the packet-first workflow and how to inspect persisted review artifacts
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- new office write capabilities beyond the current propose/export surface
- TUI integration or desktop/MCP wiring
