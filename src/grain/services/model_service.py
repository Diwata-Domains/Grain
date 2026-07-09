# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Service layer for model routing decisions."""

from pathlib import Path

from grain.adapters.model_config import load_model_profiles
from grain.cli.output import CommandResult
from grain.domain.errors import ForgeError
from grain.domain.routing import ModelSelection, get_escalation_target, select_model_class


def select_model_for_stage_or_role(
    root: Path,
    stage: str | None = None,
    role: str | None = None,
) -> tuple[CommandResult, ModelSelection | None]:
    """Resolve model class for one workflow stage or task role."""
    try:
        config = load_model_profiles(root)
    except ForgeError as exc:
        return (
            CommandResult(
                ok=False,
                command="model select",
                errors=[exc.message],
            ),
            None,
        )

    decision = select_model_class(
        config=config,
        stage=stage,
        role=role,
    )
    return (
        CommandResult(
            ok=True,
            command="model select",
            repo=str(root),
            status=decision.selected_class,
        ),
        decision,
    )


def escalate_model_for_class(
    root: Path,
    current_class: str,
    reason: str | None = None,
) -> tuple[CommandResult, str | None]:
    """Return the escalation target class for the given model class."""
    try:
        config = load_model_profiles(root)
    except ForgeError as exc:
        return (
            CommandResult(
                ok=False,
                command="model escalate",
                errors=[exc.message],
            ),
            None,
        )

    target = get_escalation_target(config, current_class, reason)
    if target is None:
        return (
            CommandResult(
                ok=False,
                command="model escalate",
                errors=[f"no escalation path defined for class '{current_class}'"],
            ),
            None,
        )

    return (
        CommandResult(
            ok=True,
            command="model escalate",
            repo=str(root),
            status=target,
        ),
        target,
    )
