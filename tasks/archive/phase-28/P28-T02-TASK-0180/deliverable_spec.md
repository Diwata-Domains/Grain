# Deliverable Spec: TASK-0180

## Required Output

### Modified Files
- `src/grain/services/verification_service.py` — add request lookup and status read path
- `src/grain/cli/verify.py` — add `verify status`
- `tests/test_verify_submit_cmd.py` — add status coverage
- `tests/test_command_groups.py` — keep verify command-group surface current

## Acceptance Checklist
- [x] `grain verify status` exists and is registered in the CLI
- [x] Status resolves packet-local verification requests by `verification_id`
- [x] Text and JSON output both surface request state cleanly
- [x] All new tests passing
- [ ] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- External polling
- Result ingestion
- Workflow gate changes
