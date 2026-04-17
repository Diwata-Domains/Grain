# Task: Implement Adapter Capability Surface Protocol

## Metadata
- **ID:** TASK-0073
- **Status:** done
- **Phase:** Phase 9 — Orchestration Service Foundation
- **Backlog:** P9-T02
- **Packet Path:** tasks/P9-T02-TASK-0073/
- **Dependencies:** TASK-0072
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective

Define the optional adapter capability interface (`detect_scope`, `collect_context`, `analyze_impact`, `validate_changes`, `export_artifacts`, `suggest_followups`) as a `Protocol` class and supporting result types in `src/forge/domain/adapters.py`. Implement `NullAdapterCapability` for graceful degradation when capabilities are absent. Add an optional `capabilities` field to `AdapterProfile` and a `get_capabilities()` helper that returns the registered implementation or `NullAdapterCapability`. Export new types from the domain package. Add tests.

## Why This Task Exists

The orchestration service (P9-T03) must query adapter capabilities to produce `OrchestratorPlan` proposals. Without a stable capability interface and graceful degradation path, P9-T03 has no typed surface to build against. This task defines that surface so the orchestration service can call capability methods on any adapter profile without requiring capabilities to be implemented.

## Scope
- Add 6 result dataclasses to `src/forge/domain/adapters.py`: `ScopeSignal`, `ContextHint`, `ImpactSignal`, `ValidationRequirement`, `ArtifactPattern`, `FollowupSuggestion`
- Add `AdapterCapabilityProtocol` (runtime-checkable `Protocol`) with the 6 capability methods
- Add `NullAdapterCapability` implementing all 6 methods with empty/no-op returns
- Update `AdapterProfile` with optional `capabilities` field (default `None`, excluded from equality) and `get_capabilities()` method
- Export new public types from `src/forge/domain/__init__.py`
- Add `tests/test_adapter_capability.py` covering all new behavior

## Constraints
- Adapter capability functions are advisory — no state mutation belongs in capability implementations
- `NullAdapterCapability` must return structurally valid (empty) results, not `None`
- `capabilities` field on `AdapterProfile` must not break existing tests or the loader
- Do not modify `adapter_config.py` parser logic — capabilities cannot come from markdown
- Do not modify canonical docs, CLI, or service files

## Escalation Conditions
- If the capability interface requires a shared input type not derivable from architecture.md, stop and record

## Closure Requirements
- `results.md` and `handoff.md` filled
- Tests pass (no regressions)
- New types importable from `src/forge/domain`
