# Deliverable Spec: TASK-0171

## Required Output

### New Files
- no new top-level product areas required; this slice should land inside the existing context service and adapter integration test surfaces

### Modified Files
- `src/grain/services/context_service.py` — add the first crawler-specific context-selection and prioritization behavior
- `tests/test_document_adapters_integration.py` — add focused integration coverage for crawler configs, selectors, and extraction schemas
- `tasks/P26-T02-TASK-0171/*` — complete the packet review artifacts for the first crawler context slice

## Acceptance Checklist
- [ ] `crawler_adapter` can select crawl configs, selectors, and extraction-schema artifacts without relying on graph traces
- [ ] unrelated application code stays out of the focused crawler context bundle
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- output-validation and extraction-quality prioritization
- crawler execution tooling
- crawler runtime state or mutation helpers
