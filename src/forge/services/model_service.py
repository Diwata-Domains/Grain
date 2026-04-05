"""Service layer for model routing decisions."""

from pathlib import Path

from forge.adapters.model_config import load_model_profiles
from forge.cli.output import CommandResult
from forge.domain.errors import ForgeError
from forge.domain.routing import ModelSelection, select_model_class


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
