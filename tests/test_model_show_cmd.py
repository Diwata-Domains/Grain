"""Tests for `forge model show` command."""

import json

from click.testing import CliRunner

from forge.cli import main


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
- workflow logic

### reviewer_model
Use for:
- review
- acceptance validation

## Escalation Rules
Escalate from open_model to frontier_model when:
- ambiguity blocks progress

Use reviewer_model when:
- task is marked complete

## Current Preferred Mapping
- open_model: Claude or Codex
- frontier_model: Claude or Codex
- reviewer_model: Claude or Codex
"""


def _write_agent_profiles(repo_root):
    profiles_path = repo_root / "docs" / "runtime" / "agent_profiles.md"
    profiles_path.parent.mkdir(parents=True, exist_ok=True)
    profiles_path.write_text(SAMPLE_AGENT_PROFILES, encoding="utf-8")


def test_model_show_text_output(tmp_path):
    _write_agent_profiles(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "model", "show"])

    assert result.exit_code == 0, result.output
    assert "model show: ok" in result.output
    assert "open_model" in result.output
    assert "frontier_model" in result.output
    assert "reviewer_model" in result.output


def test_model_show_json_output(tmp_path):
    _write_agent_profiles(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "--format", "json", "model", "show"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["command"] == "model show"
    assert data["source_path"] == "docs/runtime/agent_profiles.md"
    assert [profile["model_class"] for profile in data["model_profiles"]] == [
        "open_model",
        "frontier_model",
        "reviewer_model",
    ]


def test_model_show_missing_profile_file_exits_four(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "model", "show"])
    assert result.exit_code != 0
    assert "Model profile config not found" in str(result.exception)
