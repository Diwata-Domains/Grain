"""Tests for model selection and escalation routing."""

from forge.adapters.model_config import parse_agent_profiles_markdown
from forge.domain.routing import get_escalation_target, select_model_class


SAMPLE_AGENT_PROFILES = """# Agent Profiles

## Model Classes

### open_model
Use for:
- boilerplate
- formatting
- narrow implementation

Avoid for:
- architecture ambiguity

### frontier_model
Use for:
- architecture
- workflow logic
- ambiguous tasks

### reviewer_model
Use for:
- review
- acceptance validation
- consistency checks

## Escalation Rules
Escalate from open_model to frontier_model when:
- ambiguity blocks progress
- design tradeoffs appear

Use reviewer_model when:
- task is marked complete
- phase gate or release gate is reached

## Current Preferred Mapping
- open_model: Claude or Codex
- frontier_model: Claude or Codex
- reviewer_model: Claude or Codex
"""


def test_select_model_class_routes_execution_stages_to_open_model():
    config = parse_agent_profiles_markdown(SAMPLE_AGENT_PROFILES)

    decision = select_model_class(config, stage="Task Execution")

    assert decision.selected_class == "open_model"
    assert "stage mapping matched" in decision.reason


def test_select_model_class_routes_review_signals_to_reviewer_model():
    config = parse_agent_profiles_markdown(SAMPLE_AGENT_PROFILES)

    decision = select_model_class(config, role="acceptance validation")

    assert decision.selected_class == "reviewer_model"
    assert "review-oriented signal" in decision.reason


def test_select_model_class_routes_ambiguity_signals_to_frontier_model():
    config = parse_agent_profiles_markdown(SAMPLE_AGENT_PROFILES)

    decision = select_model_class(config, role="architecture ambiguity resolution")

    assert decision.selected_class == "frontier_model"
    assert "escalation profile" in decision.reason


def test_select_model_class_defaults_to_open_model_when_no_signal_matches():
    config = parse_agent_profiles_markdown(SAMPLE_AGENT_PROFILES)

    decision = select_model_class(config, role="minor maintenance")

    assert decision.selected_class == "open_model"
    assert "defaulted to simplest safe model class" in decision.reason


def test_get_escalation_target_uses_specific_then_wildcard_rules():
    config = parse_agent_profiles_markdown(SAMPLE_AGENT_PROFILES)

    assert get_escalation_target(config, "open_model") == "frontier_model"
    assert get_escalation_target(config, "frontier_model") == "reviewer_model"
    assert get_escalation_target(config, "reviewer_model") is None
