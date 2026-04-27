"""Tests for the adapter capability surface protocol (P9-T02)."""

from grain.domain.adapters import (
    AdapterCapabilityProtocol,
    AdapterProfile,
    ArtifactPattern,
    ContextHint,
    FollowupSuggestion,
    ImpactSignal,
    NullAdapterCapability,
    ScopeSignal,
    ValidationRequirement,
)


# ---------------------------------------------------------------------------
# NullAdapterCapability — per-method return type and empty-result contract
# ---------------------------------------------------------------------------


def test_null_capability_detect_scope_returns_scope_signal():
    cap = NullAdapterCapability()
    result = cap.detect_scope("add payment integration")
    assert isinstance(result, ScopeSignal)
    assert result.file_patterns == []
    assert result.relevant_areas == []


def test_null_capability_collect_context_returns_context_hint():
    cap = NullAdapterCapability()
    result = cap.collect_context("implement checkout flow")
    assert isinstance(result, ContextHint)
    assert result.file_patterns == []
    assert result.priority_rules == []


def test_null_capability_analyze_impact_returns_impact_signal():
    cap = NullAdapterCapability()
    result = cap.analyze_impact(["src/payments.py", "src/checkout.py"])
    assert isinstance(result, ImpactSignal)
    assert result.affected_files == []
    assert result.downstream_areas == []


def test_null_capability_validate_changes_returns_validation_requirement():
    cap = NullAdapterCapability()
    result = cap.validate_changes("add stripe integration")
    assert isinstance(result, ValidationRequirement)
    assert result.requirements == []


def test_null_capability_export_artifacts_returns_artifact_pattern():
    cap = NullAdapterCapability()
    result = cap.export_artifacts("implement payment module")
    assert isinstance(result, ArtifactPattern)
    assert result.patterns == []


def test_null_capability_suggest_followups_returns_followup_suggestion():
    cap = NullAdapterCapability()
    result = cap.suggest_followups("payment module implemented")
    assert isinstance(result, FollowupSuggestion)
    assert result.followups == []


def test_null_capability_satisfies_protocol():
    cap = NullAdapterCapability()
    assert isinstance(cap, AdapterCapabilityProtocol)


# ---------------------------------------------------------------------------
# Result type default field independence
# ---------------------------------------------------------------------------


def test_scope_signal_default_lists_are_independent():
    a = ScopeSignal()
    b = ScopeSignal()
    a.file_patterns.append("src/**/*.py")
    assert b.file_patterns == []


def test_context_hint_default_lists_are_independent():
    a = ContextHint()
    b = ContextHint()
    a.priority_rules.append("prefer task-local files")
    assert b.priority_rules == []


def test_impact_signal_default_lists_are_independent():
    a = ImpactSignal()
    b = ImpactSignal()
    a.affected_files.append("src/api.py")
    assert b.affected_files == []


# ---------------------------------------------------------------------------
# AdapterProfile.capabilities field and get_capabilities()
# ---------------------------------------------------------------------------


def test_adapter_profile_capabilities_defaults_to_none():
    profile = AdapterProfile(
        adapter_id="code_adapter",
        domain_type="code",
        applies_to=["Python"],
    )
    assert profile.capabilities is None


def test_adapter_profile_get_capabilities_returns_null_when_not_set():
    profile = AdapterProfile(
        adapter_id="code_adapter",
        domain_type="code",
        applies_to=["Python"],
    )
    caps = profile.get_capabilities()
    assert isinstance(caps, NullAdapterCapability)


def test_adapter_profile_get_capabilities_returns_registered_capability():
    custom = NullAdapterCapability()
    profile = AdapterProfile(
        adapter_id="code_adapter",
        domain_type="code",
        applies_to=["Python"],
        capabilities=custom,
    )
    assert profile.get_capabilities() is custom


def test_adapter_profile_capabilities_excluded_from_equality():
    cap_a = NullAdapterCapability()
    cap_b = NullAdapterCapability()
    profile_a = AdapterProfile(
        adapter_id="code_adapter",
        domain_type="code",
        applies_to=["Python"],
        capabilities=cap_a,
    )
    profile_b = AdapterProfile(
        adapter_id="code_adapter",
        domain_type="code",
        applies_to=["Python"],
        capabilities=cap_b,
    )
    assert profile_a == profile_b


def test_adapter_profile_equality_unaffected_by_null_vs_registered():
    custom = NullAdapterCapability()
    profile_with = AdapterProfile(
        adapter_id="code_adapter",
        domain_type="code",
        applies_to=["Python"],
        capabilities=custom,
    )
    profile_without = AdapterProfile(
        adapter_id="code_adapter",
        domain_type="code",
        applies_to=["Python"],
    )
    assert profile_with == profile_without
