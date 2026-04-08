# Deliverable Spec: TASK-0063

## Required Output

### New Files
- `tasks/P7-T03-TASK-0063/results.md` — execution results and verification summary
- `tasks/P7-T03-TASK-0063/handoff.md` — review handoff bundle

### Modified Files
- `src/forge/services/init_service.py` — seed missing baseline runtime/task-template files from template sources and report create/skip/update/blocked actions
- `src/forge/cli/init.py` — include init-service updates in CLI output result
- `tests/test_init_service.py` — add coverage for seed-file creation, skip behavior, force updates, and dry-run no-write behavior

## Acceptance Checklist
- [ ] Missing baseline runtime docs are seeded during init
- [ ] Missing task template files are seeded during init
- [ ] Existing files are skipped by default (additive-only behavior)
- [ ] Dry-run reports intended actions without writing files
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Adapter-selection onboarding options (`P7-T04`)
- Starter task bootstrap behavior (`P7-T05`)
- Existing-project adoption flow work (`P7-T07`)
