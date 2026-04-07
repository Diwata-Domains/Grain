"""Tests for the adapter profile domain model."""

from forge.domain.adapters import AdapterProfile


def test_adapter_profile_preserves_required_fields():
    profile = AdapterProfile(
        adapter_id="code_adapter",
        domain_type="code",
        applies_to=["Python", "Rust"],
    )

    assert profile.adapter_id == "code_adapter"
    assert profile.domain_type == "code"
    assert profile.applies_to == ["Python", "Rust"]


def test_adapter_profile_optional_hints_default_to_empty_lists():
    profile = AdapterProfile(
        adapter_id="frontend_adapter",
        domain_type="frontend",
        applies_to=["React"],
    )

    assert profile.relevant_file_patterns == []
    assert profile.ignore_file_patterns == []
    assert profile.build_or_run_hints == []
    assert profile.test_or_validation_hints == []
    assert profile.review_focus_hints == []
    assert profile.context_priority_rules == []
    assert profile.default_model_bias == []


def test_adapter_profile_optional_hints_use_distinct_default_lists():
    first = AdapterProfile(
        adapter_id="first_adapter",
        domain_type="code",
        applies_to=["Python"],
    )
    second = AdapterProfile(
        adapter_id="second_adapter",
        domain_type="docs",
        applies_to=["Markdown"],
    )

    first.review_focus_hints.append("behavior regressions")
    first.default_model_bias.append("open_model")

    assert second.review_focus_hints == []
    assert second.default_model_bias == []
