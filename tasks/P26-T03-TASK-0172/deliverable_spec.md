# Deliverable Spec: TASK-0172

## Required Output

### New Files
- no new top-level product areas required; this slice should stay inside the crawler adapter patterns, context service, and integration tests

### Modified Files
- `src/grain/services/context_service.py` — extend crawler source prioritization for extraction-quality objectives
- `docs/runtime/adapter_profiles.md` and the shipped runtime copy — add any output/normalization patterns needed to match the implemented behavior
- `tests/test_document_adapters_integration.py` — add focused output-validation integration coverage
- `tests/test_adapter_config_loader.py` — keep the runtime crawler contract assertions aligned
- `tasks/P26-T03-TASK-0172/*` — complete the packet review artifacts for the output-validation slice

## Acceptance Checklist
- [ ] extraction-quality objectives can bring output fixtures and normalization surfaces into the focused crawler bundle
- [ ] config/selector-first behavior remains the default when the objective is not about extraction-quality work
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- crawler review and safety guidance
- runtime crawl execution tooling
- crawler graph or dependency modeling
