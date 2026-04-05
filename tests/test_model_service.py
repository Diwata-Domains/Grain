"""Tests for model selection routing and service behavior."""

from pathlib import Path

from forge.adapters.model_config import parse_agent_profiles_markdown
from forge.domain.routing import select_model_class
from forge.services.model_service import select_model_for_stage_or_role


SAMPLE_AGENT_PROFILES = """# Agent Profiles

## Model Classes

### open_model
Use for:
- boilerplate
- formatting
- narrow implementation
- simple packet drafting

Avoid for:
- architecture ambiguity
- final validation

### frontier_model
Use for:
- architecture
- workflow logic
- ambiguous tasks
- cross-file coordination

### reviewer_model
Use for:
- review
- consistency checks
- acceptance validation

## Escalation Rules
Escalate from open_model to frontier_model when:
- ambiguity blocks progress
- design tradeoffs appear

Use reviewer_model when:
- task is marked complete
- CLI contracts changed

## Current Preferred Mapping
- open_model: Claude or Codex
- frontier_model: Claude or Codex
- reviewer_model: Claude or Codex
"""


def test_select_model_class_uses_stage_mapping_for_review_stage():
    config = parse_agent_profiles_markdown(SAMPLE_AGENT_PROFILES)
    decision = select_model_class(config, stage="Stage 5 — Review and Reconciliation")
    assert decision.selected_class == "reviewer_model"
    assert "stage mapping matched" in decision.reason


def test_select_model_class_stage_mapping_handles_canonical_em_dash_stage():
    config = parse_agent_profiles_markdown(SAMPLE_AGENT_PROFILES)
    decision = select_model_class(config, stage="Stage 6 — Closure and Handoff")
    assert decision.selected_class == "reviewer_model"
    assert "stage mapping matched" in decision.reason


def test_select_model_class_uses_stage_mapping_for_execution_stage():
    config = parse_agent_profiles_markdown(SAMPLE_AGENT_PROFILES)
    decision = select_model_class(config, stage="Task Execution")
    assert decision.selected_class == "open_model"


def test_select_model_class_uses_frontier_for_ambiguity_signals():
    config = parse_agent_profiles_markdown(SAMPLE_AGENT_PROFILES)
    decision = select_model_class(config, role="architecture ambiguity resolution")
    assert decision.selected_class == "frontier_model"


def test_select_model_class_uses_reviewer_for_acceptance_signals():
    config = parse_agent_profiles_markdown(SAMPLE_AGENT_PROFILES)
    decision = select_model_class(config, role="acceptance validation")
    assert decision.selected_class == "reviewer_model"


def test_select_model_class_defaults_to_open_model():
    config = parse_agent_profiles_markdown(SAMPLE_AGENT_PROFILES)
    decision = select_model_class(config, role="small formatting cleanup")
    assert decision.selected_class == "open_model"


def test_model_service_selects_from_runtime_config(tmp_path: Path):
    profiles_path = tmp_path / "docs" / "runtime" / "agent_profiles.md"
    profiles_path.parent.mkdir(parents=True)
    profiles_path.write_text(SAMPLE_AGENT_PROFILES, encoding="utf-8")

    result, decision = select_model_for_stage_or_role(
        tmp_path,
        role="cross-file coordination",
    )

    assert result.ok is True
    assert result.status == "frontier_model"
    assert decision is not None
    assert decision.selected_class == "frontier_model"


def test_model_service_returns_error_when_config_is_missing(tmp_path: Path):
    result, decision = select_model_for_stage_or_role(tmp_path, stage="Task Execution")

    assert result.ok is False
    assert decision is None
    assert any("Model profile config not found" in message for message in result.errors)
