# Deliverable Spec: TASK-0073

## Required Output

### Modified Files
- `src/forge/domain/adapters.py` — add 6 result dataclasses, `AdapterCapabilityProtocol`, `NullAdapterCapability`; update `AdapterProfile` with `capabilities` field and `get_capabilities()` method
- `src/forge/domain/__init__.py` — export 8 new public types

### New Files
- `tests/test_adapter_capability.py` — tests for capability protocol and graceful degradation

## Acceptance Checklist
- [ ] `ScopeSignal`, `ContextHint`, `ImpactSignal`, `ValidationRequirement`, `ArtifactPattern`, `FollowupSuggestion` defined with list fields defaulting to `[]`
- [ ] `AdapterCapabilityProtocol` is a `@runtime_checkable Protocol` with all 6 methods
- [ ] `NullAdapterCapability` implements all 6 methods with empty-result returns
- [ ] `NullAdapterCapability` satisfies `isinstance(cap, AdapterCapabilityProtocol)`
- [ ] `AdapterProfile.capabilities` defaults to `None` and is excluded from equality
- [ ] `AdapterProfile.get_capabilities()` returns `NullAdapterCapability` when no capabilities registered
- [ ] `AdapterProfile.get_capabilities()` returns registered capability when set
- [ ] All 8 new types exported from `src/forge/domain/__init__.py`
- [ ] Existing `test_adapter_domain.py` tests still pass
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Changes to `adapter_config.py` parser (capabilities cannot come from markdown)
- Changes to canonical docs, CLI, or service files
- Tree-sitter or actual capability implementations (Phase 10)
