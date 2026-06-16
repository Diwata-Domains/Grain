# Deliverable Spec: TASK-0167

## Required Output

### New Files
- no new top-level product areas required; this slice should stay inside the database adapter patterns, context service, and integration tests

### Modified Files
- `src/grain/services/context_service.py` — extend database source prioritization for persistence-oriented objectives
- `docs/runtime/adapter_profiles.md` and the shipped runtime copy — add any query/repository patterns needed to match the implemented behavior
- `tests/test_document_adapters_integration.py` — add focused query/repository integration coverage
- `tests/test_adapter_config_loader.py` — keep the runtime database contract assertions aligned
- `tasks/P25-T03-TASK-0167/*` — complete the packet review artifacts for the query/ORM slice

## Acceptance Checklist
- [ ] persistence-oriented objectives can bring query and repository/data-access files into the focused database bundle
- [ ] schema/migration-first behavior remains the default when the objective is not about persistence work
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- database review/validation guidance
- runtime query execution tooling
- database graph or dependency modeling
