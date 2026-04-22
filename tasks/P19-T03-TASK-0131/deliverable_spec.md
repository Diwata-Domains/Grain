# Deliverable Spec: TASK-0131

## Required Output

### New Files
- `src/grain/services/adapter_install_service.py` — local-only install service for validated community adapter packages
- `tests/test_adapter_install_service.py` — focused install-service coverage

### Modified Files
- `src/grain/cli/adapter.py` — add `adapter install`
- `tests/test_adapter_cmd.py` — add CLI coverage for install output and behavior

## Acceptance Checklist
- [ ] `grain adapter install` accepts either `--source` or `--handle` plus `--registry-root`
- [ ] install validates packages before mutating repo files
- [ ] install writes the adapter into `docs/runtime/adapter_profiles.md`
- [ ] duplicate adapter IDs are rejected before install
- [ ] unknown or ambiguous handles fail deterministically
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- remote registry download/fetch behavior
- automatic promotion from Community to Official
- registry submission scaffolding or CI automation
