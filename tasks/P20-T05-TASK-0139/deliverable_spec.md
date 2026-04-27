# Deliverable Spec: TASK-0139

## Required Output

### New Files
- `tests/test_upgrade_cmd.py` additions — coverage for customized-file skip behavior and CLI reporting

### Modified Files
- `src/grain/services/upgrade_service.py` — classify customized managed files and skip them by default in non-interactive upgrade mode
- `src/grain/cli/upgrade.py` — report skipped customized files and guide operators toward interactive or diff review

## Acceptance Checklist
- [x] Customized managed files are detected during upgrade evaluation
- [x] Default non-interactive upgrade skips customized managed files instead of overwriting them
- [x] CLI output surfaces skipped customized files and points operators to `--interactive` / `--diff`
- [x] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Redefining user-owned protected-file boundaries
- Changing upgrade behavior for missing-file seeding or unchanged files
