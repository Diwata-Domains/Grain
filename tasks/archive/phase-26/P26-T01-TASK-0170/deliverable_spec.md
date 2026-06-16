# Deliverable Spec: TASK-0170

## Required Output

### New Files
- no new top-level product areas required; this slice should land inside the existing adapter runtime and parser-test surfaces

### Modified Files
- `docs/runtime/adapter_profiles.md` — add the live `crawler_adapter` contract
- `src/grain/data/runtime/adapter_profiles.md` — keep the shipped runtime copy aligned with the crawler adapter surface
- `tests/test_adapter_config_loader.py` — add parser assertions for the new crawler adapter contract
- `tasks/P26-T01-TASK-0170/*` — complete the packet review artifacts for the crawler adapter scaffold

## Acceptance Checklist
- [ ] `crawler_adapter` exists as a dedicated documented adapter/profile surface
- [ ] the crawler contract explicitly covers crawl config, selectors, extraction schemas, and output-validation work without broadening into behavior yet
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- crawl-config and selector context-selection behavior
- output-validation or extraction-quality prioritization
- crawler runtime tooling or execution helpers
