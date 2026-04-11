"""Tests for `forge model select` command."""

import json

from click.testing import CliRunner

from grain.cli import main


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

Avoid for:
- simple formatting

### reviewer_model
Use for:
- review
- acceptance validation
- consistency checks

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


def test_model_select_text_stage(tmp_path):
    _write_agent_profiles(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(tmp_path), "model", "select", "--stage", "task execution"]
    )

    assert result.exit_code == 0, result.output
    assert "model select: ok" in result.output
    assert "open_model" in result.output
    assert "stage" in result.output


def test_model_select_text_role_review(tmp_path):
    _write_agent_profiles(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(tmp_path), "model", "select", "--role", "review"]
    )

    assert result.exit_code == 0, result.output
    assert "model select: ok" in result.output
    assert "reviewer_model" in result.output


def test_model_select_json_output(tmp_path):
    _write_agent_profiles(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--repo", str(tmp_path),
            "--format", "json",
            "model", "select",
            "--stage", "task execution",
        ],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["command"] == "model select"
    assert data["selected_class"] == "open_model"
    assert "reason" in data
    assert data["stage"] == "task execution"
    assert "role" in data


def test_model_select_no_args_exits_nonzero(tmp_path):
    _write_agent_profiles(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "model", "select"])

    assert result.exit_code != 0
    assert "stage" in result.output.lower() or "role" in result.output.lower()


def test_model_select_missing_profile_exits_nonzero(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(tmp_path), "model", "select", "--stage", "execute"]
    )

    assert result.exit_code != 0
    assert "model select: failed" in result.output
    assert "agent_profiles.md" in result.output


def test_model_select_missing_profile_json_failure_shape(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--repo", str(tmp_path),
            "--format", "json",
            "model", "select",
            "--stage", "execute",
        ],
    )

    assert result.exit_code != 0
    data = json.loads(result.output)
    assert data["ok"] is False
    assert data["command"] == "model select"
    assert data["stage"] == "execute"
    assert "errors" in data
