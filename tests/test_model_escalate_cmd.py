"""Tests for `forge model escalate` command."""

import json

from click.testing import CliRunner

from forge.cli import main


SAMPLE_AGENT_PROFILES = """# Agent Profiles

## Model Classes

### open_model
Use for:
- boilerplate
- narrow implementation

Avoid for:
- architecture ambiguity

### frontier_model
Use for:
- architecture
- workflow logic

### reviewer_model
Use for:
- review
- acceptance validation

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


def _write_agent_profiles(repo_root):
    profiles_path = repo_root / "docs" / "runtime" / "agent_profiles.md"
    profiles_path.parent.mkdir(parents=True, exist_ok=True)
    profiles_path.write_text(SAMPLE_AGENT_PROFILES, encoding="utf-8")


def test_model_escalate_open_to_frontier(tmp_path):
    _write_agent_profiles(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(tmp_path), "model", "escalate", "--from-class", "open_model"]
    )

    assert result.exit_code == 0, result.output
    assert "model escalate: ok" in result.output
    assert "frontier_model" in result.output


def test_model_escalate_wildcard_to_reviewer(tmp_path):
    _write_agent_profiles(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(tmp_path), "model", "escalate", "--from-class", "frontier_model"]
    )

    assert result.exit_code == 0, result.output
    assert "model escalate: ok" in result.output
    assert "reviewer_model" in result.output


def test_model_escalate_with_reason(tmp_path):
    _write_agent_profiles(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--repo", str(tmp_path),
            "model", "escalate",
            "--from-class", "open_model",
            "--reason", "ambiguity blocks progress",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "frontier_model" in result.output
    assert "ambiguity" in result.output


def test_model_escalate_json_output(tmp_path):
    _write_agent_profiles(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--repo", str(tmp_path),
            "--format", "json",
            "model", "escalate",
            "--from-class", "open_model",
        ],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["command"] == "model escalate"
    assert data["from_class"] == "open_model"
    assert data["target_class"] == "frontier_model"
    assert "reason" in data


NO_WILDCARD_PROFILES = """# Agent Profiles

## Model Classes

### open_model
Use for:
- boilerplate

### frontier_model
Use for:
- architecture

### reviewer_model
Use for:
- review

## Escalation Rules
Escalate from open_model to frontier_model when:
- ambiguity blocks progress

## Current Preferred Mapping
- open_model: Claude or Codex
- frontier_model: Claude or Codex
- reviewer_model: Claude or Codex
"""


def _write_no_wildcard_profiles(repo_root):
    profiles_path = repo_root / "docs" / "runtime" / "agent_profiles.md"
    profiles_path.parent.mkdir(parents=True, exist_ok=True)
    profiles_path.write_text(NO_WILDCARD_PROFILES, encoding="utf-8")


def test_model_escalate_unknown_class_exits_nonzero(tmp_path):
    # Use a profile without a wildcard rule so unknown_model has no escalation path.
    _write_no_wildcard_profiles(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(tmp_path), "model", "escalate", "--from-class", "unknown_model"]
    )

    assert result.exit_code != 0
    assert "model escalate: failed" in result.output
    assert "no escalation path defined for class 'unknown_model'" in result.output


def test_model_escalate_missing_profile_exits_nonzero(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(tmp_path), "model", "escalate", "--from-class", "open_model"]
    )

    assert result.exit_code != 0
    assert "model escalate: failed" in result.output
    assert "agent_profiles.md" in result.output


def test_model_escalate_reviewer_model_exits_nonzero(tmp_path):
    # reviewer_model matches the wildcard rule but the target is itself — no valid escalation path.
    _write_agent_profiles(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(tmp_path), "model", "escalate", "--from-class", "reviewer_model"]
    )

    assert result.exit_code != 0


def test_model_escalate_missing_profile_json_failure_shape(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--repo", str(tmp_path),
            "--format", "json",
            "model", "escalate",
            "--from-class", "open_model",
        ],
    )

    assert result.exit_code != 0
    data = json.loads(result.output)
    assert data["ok"] is False
    assert data["command"] == "model escalate"
    assert data["from_class"] == "open_model"
    assert "errors" in data
