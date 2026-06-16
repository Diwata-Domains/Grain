# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Service for loading workflow loop configuration from runtime YAML."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import yaml

from grain.domain.errors import ConfigError, MissingPathError
from grain.domain.workflow_loop import (
    VALID_STAGE_NAMES,
    VALID_SUPERVISION_LEVELS,
    WorkflowLoopAgentConfig,
    WorkflowLoopConfig,
    WorkflowLoopStageConfig,
)

WORKFLOW_LOOP_CONFIG_PATH = "docs/runtime/workflow_loop.yaml"


def load_workflow_loop_config(
    root: Path,
    supervision_level_override: str | None = None,
    stage_overrides: dict[str, WorkflowLoopAgentConfig] | None = None,
) -> WorkflowLoopConfig:
    """Load and validate workflow loop runtime config.

    Args:
        root: Repository root.
        supervision_level_override: Optional CLI override for supervision level.
        stage_overrides: Optional stage-specific agent config overrides.

    Raises:
        MissingPathError: config file missing.
        ConfigError: invalid YAML or schema values.
    """
    config_path = root / WORKFLOW_LOOP_CONFIG_PATH
    if not config_path.exists():
        raise MissingPathError(
            f"Workflow loop config not found: {WORKFLOW_LOOP_CONFIG_PATH}",
            detail=str(config_path),
        )

    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(
            f"Workflow loop config is not valid YAML: {WORKFLOW_LOOP_CONFIG_PATH}",
            detail=str(exc),
        ) from exc

    if not isinstance(raw, dict):
        raise ConfigError(
            "Workflow loop config root must be a mapping",
            detail=WORKFLOW_LOOP_CONFIG_PATH,
        )

    supervision_level = raw.get("supervision_level", "gated")
    if not isinstance(supervision_level, str):
        raise ConfigError(
            "workflow loop supervision_level must be a string",
            detail=f"got type: {type(supervision_level).__name__}",
        )

    if supervision_level_override is not None:
        supervision_level = supervision_level_override

    if supervision_level not in VALID_SUPERVISION_LEVELS:
        raise ConfigError(
            f"invalid workflow loop supervision_level: {supervision_level}",
            detail=f"expected one of {sorted(VALID_SUPERVISION_LEVELS)}",
        )

    agents = raw.get("agents")
    if not isinstance(agents, dict):
        raise ConfigError(
            "workflow loop config requires an 'agents' mapping",
            detail=WORKFLOW_LOOP_CONFIG_PATH,
        )

    missing_stages = [stage for stage in VALID_STAGE_NAMES if stage not in agents]
    if missing_stages:
        raise ConfigError(
            "workflow loop config is missing stage agent entries",
            detail=f"missing: {', '.join(missing_stages)}",
        )

    parsed: dict[str, WorkflowLoopAgentConfig] = {}
    for stage in VALID_STAGE_NAMES:
        parsed[stage] = _parse_stage_agent(stage, agents[stage])

    for stage, override in (stage_overrides or {}).items():
        if stage not in VALID_STAGE_NAMES:
            raise ConfigError(
                f"invalid workflow loop stage override: {stage}",
                detail=f"expected one of {list(VALID_STAGE_NAMES)}",
            )
        parsed[stage] = override

    return WorkflowLoopConfig(
        supervision_level=supervision_level,
        stages=WorkflowLoopStageConfig(
            executor=parsed["executor"],
            reviewer=parsed["reviewer"],
            closer=parsed["closer"],
        ),
        source_path=WORKFLOW_LOOP_CONFIG_PATH,
    )


def with_supervision_level(config: WorkflowLoopConfig, supervision_level: str) -> WorkflowLoopConfig:
    """Return a copy of config with updated supervision level."""
    if supervision_level not in VALID_SUPERVISION_LEVELS:
        raise ConfigError(
            f"invalid workflow loop supervision_level: {supervision_level}",
            detail=f"expected one of {sorted(VALID_SUPERVISION_LEVELS)}",
        )
    return replace(config, supervision_level=supervision_level)


def _parse_stage_agent(stage: str, raw_stage: object) -> WorkflowLoopAgentConfig:
    if not isinstance(raw_stage, dict):
        raise ConfigError(
            f"workflow loop agent config for stage '{stage}' must be a mapping",
            detail=f"got type: {type(raw_stage).__name__}",
        )

    shortcut = raw_stage.get("shortcut")
    command = raw_stage.get("command")
    model = raw_stage.get("model", "")

    if shortcut and command:
        raise ConfigError(
            f"stage '{stage}' must set either shortcut or command, not both",
            detail="remove one of: shortcut, command",
        )

    if shortcut:
        try:
            return WorkflowLoopAgentConfig(
                mode="shortcut",
                shortcut=str(shortcut).strip(),
                model=str(model).strip() if model is not None else "",
            )
        except ValueError as exc:
            raise ConfigError(
                f"invalid stage '{stage}' shortcut agent config",
                detail=str(exc),
            ) from exc

    if command:
        try:
            return WorkflowLoopAgentConfig(
                mode="command",
                command=str(command),
                model=str(model).strip() if model is not None else "",
            )
        except ValueError as exc:
            raise ConfigError(
                f"invalid stage '{stage}' command agent config",
                detail=str(exc),
            ) from exc

    raise ConfigError(
        f"stage '{stage}' must define one invocation mode",
        detail="set shortcut or command",
    )
