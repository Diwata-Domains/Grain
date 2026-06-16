# Deliverable Spec: TASK-0166

## Required Output

### New Files
- no new top-level product areas required; this slice should land inside the existing context service and adapter integration test surfaces

### Modified Files
- `src/grain/services/context_service.py` — add the first database-specific context-selection and prioritization behavior
- `docs/runtime/adapter_profiles.md` and the shipped runtime copy if needed — keep the database adapter patterns aligned with the implemented selection behavior
- `tests/test_document_adapters_integration.py` — add focused integration coverage for database schema, migration, and model selection
- `tasks/P25-T02-TASK-0166/*` — complete the packet review artifacts for the first database context slice

## Acceptance Checklist
- [ ] `database_adapter` can select schema, migration, and nearby model artifacts without relying on graph traces
- [ ] unrelated application code stays out of the focused database context bundle
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- query-file and broader ORM repository selection
- migration execution tooling
- database runtime state or mutation helpers
