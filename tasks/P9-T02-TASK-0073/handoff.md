# Handoff: TASK-0073

## Final State
Adapter capability surface protocol defined. P9-T03 (orchestration service — task-level) now has a typed capability interface and graceful degradation path to build against.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0073
- **Phase:** Phase 9 — Orchestration Service Foundation
- **Status:** done

### Outcome
- **Review Readiness:** ready
- **Review Decision:** ready
- **Recommended Next Status:** done
- **Short Summary:** Added `AdapterCapabilityProtocol`, `NullAdapterCapability`, 6 result types, and `AdapterProfile.get_capabilities()` to `src/forge/domain/adapters.py`; 15 new passing tests; 521/521 total suite. Trivial fix applied during review: `Recommended Next Status` corrected from `review` to `done` in handoff.md Outcome.

## What Was Built
- 6 result dataclasses: `ScopeSignal`, `ContextHint`, `ImpactSignal`, `ValidationRequirement`, `ArtifactPattern`, `FollowupSuggestion` — each with list fields defaulting to empty
- `AdapterCapabilityProtocol` — `@runtime_checkable Protocol` defining the 6 capability method signatures
- `NullAdapterCapability` — no-op implementation returning empty result instances for all 6 methods
- `AdapterProfile.capabilities` — optional field (`None` by default, excluded from equality and repr)
- `AdapterProfile.get_capabilities()` — returns registered capability or `NullAdapterCapability`
- `src/forge/domain/__init__.py` — 8 new public exports added
- `tests/test_adapter_capability.py` — 15 tests covering all new behavior

## What Review Should Check
- `@runtime_checkable` on `AdapterCapabilityProtocol` — required for `isinstance` checks to work correctly (test confirms this)
- `compare=False` on `capabilities` field — ensures existing adapter equality tests are unaffected
- `NullAdapterCapability` returns new empty instances (not shared mutable objects) on each call
- No changes to `adapter_config.py` loader — capabilities cannot come from markdown; loader still creates profiles with `capabilities=None`
- No canonical docs, CLI, or service files modified

## What Was Not Done
- Orchestration service implementation (P9-T03, P9-T04)
- `forge adapter` or `forge orchestrate` CLI commands (P9-T05, P9-T06)
- Actual capability implementations (e.g. tree-sitter-backed `detect_scope` — deferred to Phase 10)
- Validator for `OrchestratorPlan` (P9-T07)

## Known Issues or Follow-ups
- None. Protocol and result types are straightforward; no ambiguities encountered.

## Files Changed
- `src/forge/domain/adapters.py` — updated (added capability types, protocol, null impl, AdapterProfile field + method)
- `src/forge/domain/__init__.py` — updated (added 8 new exports)
- `tests/test_adapter_capability.py` — new

## Reviewer Notes
The key non-obvious design decision is using `@runtime_checkable Protocol` rather than an abstract base class. This allows `isinstance(NullAdapterCapability(), AdapterCapabilityProtocol)` to work structurally without requiring `NullAdapterCapability` to explicitly inherit from the protocol. The test confirms this works correctly. Future capability implementations will automatically satisfy the protocol as long as they define the 6 required method signatures.

The `compare=False, repr=False` on the `capabilities` field keeps `AdapterProfile` equality and string representation stable — the capability object is runtime behavior, not part of the profile's identity.

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- P9-T03 (orchestration service — task-level) — unblocked by this task; can now call `profile.get_capabilities().detect_scope(...)` etc. unconditionally
