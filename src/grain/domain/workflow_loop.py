# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Domain models for workflow loop configuration."""

from __future__ import annotations

from dataclasses import dataclass

VALID_SUPERVISION_LEVELS: frozenset[str] = frozenset({"supervised", "gated", "autonomous"})
VALID_STAGE_NAMES: tuple[str, ...] = ("executor", "reviewer", "closer")
VALID_AGENT_SHORTCUTS: frozenset[str] = frozenset({"claude", "codex"})


@dataclass
class WorkflowLoopAgentConfig:
    """Agent invocation settings for one workflow stage."""

    mode: str
    shortcut: str = ""
    model: str = ""
    command: str = ""

    def __post_init__(self) -> None:
        if self.mode not in {"shortcut", "command"}:
            raise ValueError("agent mode must be 'shortcut' or 'command'")

        if self.mode == "shortcut":
            if not self.shortcut:
                raise ValueError("shortcut agent config requires 'shortcut'")
            if self.shortcut not in VALID_AGENT_SHORTCUTS:
                raise ValueError(
                    f"unsupported shortcut {self.shortcut!r}; expected one of "
                    f"{sorted(VALID_AGENT_SHORTCUTS)}"
                )
            if self.command:
                raise ValueError("shortcut agent config must not set 'command'")

        if self.mode == "command":
            if not self.command.strip():
                raise ValueError("command agent config requires non-empty 'command'")
            if self.shortcut:
                raise ValueError("command agent config must not set 'shortcut'")


@dataclass
class WorkflowLoopStageConfig:
    """Agent configs for each workflow loop stage role."""

    executor: WorkflowLoopAgentConfig
    reviewer: WorkflowLoopAgentConfig
    closer: WorkflowLoopAgentConfig

    def for_stage(self, stage: str) -> WorkflowLoopAgentConfig:
        """Return config for one stage name."""
        if stage not in VALID_STAGE_NAMES:
            raise ValueError(
                f"unsupported workflow stage {stage!r}; expected one of {list(VALID_STAGE_NAMES)}"
            )
        return getattr(self, stage)


@dataclass
class WorkflowLoopConfig:
    """Parsed workflow loop runtime configuration."""

    supervision_level: str
    stages: WorkflowLoopStageConfig
    source_path: str = "docs/runtime/workflow_loop.yaml"

    def __post_init__(self) -> None:
        if self.supervision_level not in VALID_SUPERVISION_LEVELS:
            raise ValueError(
                f"invalid supervision_level {self.supervision_level!r}; "
                f"expected one of {sorted(VALID_SUPERVISION_LEVELS)}"
            )
