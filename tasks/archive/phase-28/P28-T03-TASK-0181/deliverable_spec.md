# Deliverable Spec: TASK-0181

## Required Output

### New Files
- None

### Modified Files
- `src/grain/services/verification_service.py` — add payload validation and packet-local ingestion flow
- `src/grain/cli/verify.py` — add `grain verify ingest`
- `tests/test_verify_submit_cmd.py` — add ingest success/failure coverage
- `tests/test_command_groups.py` — assert the new verify subcommand is exposed

## Acceptance Checklist
- [x] `grain verify ingest --verification-id --payload <path>` exists
- [x] Assay payload validation rejects malformed or mismatched results cleanly
- [x] successful ingest writes `verification_result.json` and updates request/results artifacts
- [x] focused verify command tests pass
- [ ] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- External provider polling
- Automatic packet closure or follow-up generation
