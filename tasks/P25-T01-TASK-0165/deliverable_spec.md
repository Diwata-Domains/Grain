# Deliverable Spec: TASK-0165

## Required Output

### New Files
- no new top-level product areas required; this slice should land inside the existing adapter runtime and parser-test surfaces

### Modified Files
- `docs/runtime/adapter_profiles.md` — add the live `database_adapter` contract
- `src/grain/data/runtime/adapter_profiles.md` — keep the shipped runtime copy aligned with the database adapter surface
- `tests/test_adapter_config_loader.py` — add parser assertions for the new database adapter contract
- `tasks/P25-T01-TASK-0165/*` — complete the packet review artifacts for the database adapter scaffold

## Acceptance Checklist
- [ ] `database_adapter` exists as a dedicated documented adapter/profile surface
- [ ] the database contract explicitly covers schema, migration, query, and ORM-oriented work without broadening into behavior yet
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- schema and migration context-selection behavior
- query or ORM selection behavior
- database runtime tooling or mutation helpers
