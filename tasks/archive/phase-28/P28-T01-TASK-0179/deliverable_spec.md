# Deliverable Spec: TASK-0179

## Required Output

### New Files
- `src/grain/cli/verify.py` — verification command group
- `src/grain/services/verification_service.py` — packet-local verification request service
- `tests/test_verify_submit_cmd.py` — submit bridge coverage

### Modified Files
- `src/grain/cli/__init__.py` — register `verify`
- `tests/test_command_groups.py` — assert the new command surface

## Acceptance Checklist
- [x] `grain verify submit` exists and is registered in the CLI
- [x] Submit writes a packet-local verification request artifact
- [x] Submit marks packet verification state as pending in `results.md`
- [x] Unsupported providers fail explicitly
- [x] All new tests passing
- [ ] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Verification polling
- Result ingestion
- Workflow close gating
