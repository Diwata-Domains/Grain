# Plan: TASK-0073

## Approach

Add capability result types, the `AdapterCapabilityProtocol` Protocol, and `NullAdapterCapability` to `src/forge/domain/adapters.py`. Update `AdapterProfile` to accept an optional capabilities reference. Export from the domain `__init__`. Write tests. No service, CLI, or canonical doc changes.

---

## Step 1 — Add result dataclasses to `src/forge/domain/adapters.py`

Add six result dataclasses above `AdapterProfile`:
- `ScopeSignal(file_patterns: list[str], relevant_areas: list[str])`
- `ContextHint(file_patterns: list[str], priority_rules: list[str])`
- `ImpactSignal(affected_files: list[str], downstream_areas: list[str])`
- `ValidationRequirement(requirements: list[str])`
- `ArtifactPattern(patterns: list[str])`
- `FollowupSuggestion(followups: list[str])`

All list fields use `field(default_factory=list)`.

---

## Step 2 — Add `AdapterCapabilityProtocol` and `NullAdapterCapability`

After result types, add:
- `AdapterCapabilityProtocol` — a `@runtime_checkable` `Protocol` with the 6 methods, each accepting the relevant input and returning the matching result type
- `NullAdapterCapability` — concrete class implementing all 6 methods with empty-result returns

---

## Step 3 — Update `AdapterProfile`

Add to `AdapterProfile`:
- `capabilities: AdapterCapabilityProtocol | None = field(default=None, compare=False)`
- `get_capabilities(self) -> AdapterCapabilityProtocol` — returns `self.capabilities` if set, else `NullAdapterCapability()`

The `compare=False` ensures existing equality tests pass.

---

## Step 4 — Update `src/forge/domain/__init__.py`

Export the new public types:
`AdapterCapabilityProtocol`, `NullAdapterCapability`, `ScopeSignal`, `ContextHint`, `ImpactSignal`, `ValidationRequirement`, `ArtifactPattern`, `FollowupSuggestion`

---

## Step 5 — Write `tests/test_adapter_capability.py`

Cover:
- Each `NullAdapterCapability` method returns the correct empty result type
- `NullAdapterCapability` satisfies `AdapterCapabilityProtocol` (isinstance check)
- `AdapterProfile.capabilities` defaults to `None`
- `AdapterProfile.get_capabilities()` returns `NullAdapterCapability` when `capabilities is None`
- `AdapterProfile.get_capabilities()` returns the registered capability when set
- Result dataclass default field independence (list shared-state guard)
- `AdapterProfile` equality excludes `capabilities` field

---

## Verification

Run `pytest tests/test_adapter_capability.py -v` — all new tests pass.
Run full suite `pytest` — no regressions.
