"""Tests for loading model profile configuration from runtime markdown."""

from pathlib import Path

import pytest

from grain.adapters.model_config import load_model_profiles, parse_agent_profiles_markdown
from grain.domain.errors import ConfigError, MissingPathError


SAMPLE_AGENT_PROFILES = """# Agent Profiles

## Model Classes

### open_model
Use for:
- boilerplate
- formatting

Avoid for:
- architecture ambiguity

### frontier_model
Use for:
- architecture
- difficult debugging

### reviewer_model
Use for:
- review
- acceptance validation

## Escalation Rules
Escalate from open_model to frontier_model when:
- ambiguity blocks progress
- task affects canonical design indirectly

Use reviewer_model when:
- task is marked complete
- CLI contracts changed

## Current Preferred Mapping
- open_model: Claude or Codex
- frontier_model: Claude or Codex
- reviewer_model: Claude or Codex
"""


def test_parse_agent_profiles_returns_expected_classes_and_rules():
    config = parse_agent_profiles_markdown(SAMPLE_AGENT_PROFILES)

    assert config.model_classes() == ["open_model", "frontier_model", "reviewer_model"]
    assert len(config.escalation_rules) == 2

    open_profile = config.by_class("open_model")
    assert open_profile is not None
    assert open_profile.use_for == ["boilerplate", "formatting"]
    assert open_profile.avoid_for == ["architecture ambiguity"]
    assert open_profile.preferred_models == ["Claude", "Codex"]
    assert open_profile.escalation_targets == ["frontier_model", "reviewer_model"]

    frontier_profile = config.by_class("frontier_model")
    assert frontier_profile is not None
    assert frontier_profile.escalation_targets == ["reviewer_model"]

    reviewer_profile = config.by_class("reviewer_model")
    assert reviewer_profile is not None
    assert reviewer_profile.escalation_targets == []


def test_parse_agent_profiles_raises_for_incomplete_model_classes():
    incomplete = SAMPLE_AGENT_PROFILES.replace("### reviewer_model", "### reviewer_missing")
    with pytest.raises(ConfigError) as exc:
        parse_agent_profiles_markdown(incomplete)
    assert "Missing model class section(s)" in exc.value.detail


def test_load_model_profiles_reads_runtime_file(tmp_path: Path):
    profiles_path = tmp_path / "docs" / "runtime" / "agent_profiles.md"
    profiles_path.parent.mkdir(parents=True)
    profiles_path.write_text(SAMPLE_AGENT_PROFILES, encoding="utf-8")

    config = load_model_profiles(tmp_path)
    assert config.by_class("open_model") is not None
    assert config.source_path == "docs/runtime/agent_profiles.md"


def test_load_model_profiles_raises_when_file_missing(tmp_path: Path):
    with pytest.raises(MissingPathError) as exc:
        load_model_profiles(tmp_path)
    assert "Model profile config not found" in exc.value.message
