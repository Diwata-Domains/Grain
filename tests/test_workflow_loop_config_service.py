"""Tests for workflow loop configuration loading/validation."""

from pathlib import Path

import pytest

from grain.domain.errors import ConfigError, MissingPathError
from grain.domain.workflow_loop import WorkflowLoopAgentConfig
from grain.services.workflow_loop_config_service import (
    WORKFLOW_LOOP_CONFIG_PATH,
    load_workflow_loop_config,
    with_supervision_level,
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _valid_yaml() -> str:
    return """
version: 1
supervision_level: gated
agents:
  executor:
    shortcut: codex
    model: gpt-5.4
  reviewer:
    shortcut: claude
  closer:
    command: "python -m tools.close"
""".strip()


def test_load_workflow_loop_config_parses_valid_yaml(tmp_path: Path):
    _write(tmp_path / WORKFLOW_LOOP_CONFIG_PATH, _valid_yaml())

    config = load_workflow_loop_config(tmp_path)

    assert config.supervision_level == "gated"
    assert config.stages.executor.mode == "shortcut"
    assert config.stages.executor.shortcut == "codex"
    assert config.stages.closer.mode == "command"
    assert config.stages.closer.command == "python -m tools.close"


def test_load_workflow_loop_config_raises_when_file_missing(tmp_path: Path):
    with pytest.raises(MissingPathError) as exc:
        load_workflow_loop_config(tmp_path)
    assert WORKFLOW_LOOP_CONFIG_PATH in exc.value.message


def test_load_workflow_loop_config_raises_on_invalid_yaml(tmp_path: Path):
    _write(tmp_path / WORKFLOW_LOOP_CONFIG_PATH, "agents: [\n")

    with pytest.raises(ConfigError) as exc:
        load_workflow_loop_config(tmp_path)
    assert "not valid YAML" in exc.value.message


def test_load_workflow_loop_config_raises_on_invalid_supervision_level(tmp_path: Path):
    _write(
        tmp_path / WORKFLOW_LOOP_CONFIG_PATH,
        _valid_yaml().replace("supervision_level: gated", "supervision_level: unsafe"),
    )

    with pytest.raises(ConfigError) as exc:
        load_workflow_loop_config(tmp_path)
    assert "invalid workflow loop supervision_level" in exc.value.message


def test_load_workflow_loop_config_raises_when_stage_missing(tmp_path: Path):
    _write(
        tmp_path / WORKFLOW_LOOP_CONFIG_PATH,
        """
version: 1
supervision_level: gated
agents:
  executor:
    shortcut: codex
  reviewer:
    shortcut: codex
""".strip(),
    )

    with pytest.raises(ConfigError) as exc:
        load_workflow_loop_config(tmp_path)
    assert "missing stage agent entries" in exc.value.message


def test_load_workflow_loop_config_applies_overrides(tmp_path: Path):
    _write(tmp_path / WORKFLOW_LOOP_CONFIG_PATH, _valid_yaml())

    override = {"reviewer": WorkflowLoopAgentConfig(mode="command", command="bin/review")}
    config = load_workflow_loop_config(
        tmp_path,
        supervision_level_override="autonomous",
        stage_overrides=override,
    )

    assert config.supervision_level == "autonomous"
    assert config.stages.reviewer.mode == "command"
    assert config.stages.reviewer.command == "bin/review"


def test_with_supervision_level_returns_updated_copy(tmp_path: Path):
    _write(tmp_path / WORKFLOW_LOOP_CONFIG_PATH, _valid_yaml())
    config = load_workflow_loop_config(tmp_path)

    updated = with_supervision_level(config, "supervised")

    assert config.supervision_level == "gated"
    assert updated.supervision_level == "supervised"
