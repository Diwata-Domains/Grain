"""Task prepare service — prerequisite checks for one task packet."""

from pathlib import Path

from forge.cli.output import CommandResult
from forge.domain.packets import find_packet_dir, parse_task_metadata

_REQUIRED_PACKET_FILES = ("task.md", "context.md", "plan.md", "deliverable_spec.md")


def prepare_task_packet(root: Path, task_id: str) -> tuple[CommandResult, dict | None]:
    """Check whether one task has the minimal packet/prompt prerequisites.

    This is a read-only check. It does not create or mutate artifacts.
    """
    packet_dir = find_packet_dir(root / "tasks", task_id)
    if packet_dir is None:
        return (
            CommandResult(
                ok=False,
                command="task prepare",
                errors=[f"packet '{task_id}' not found"],
            ),
            None,
        )

    task_md = packet_dir / "task.md"
    metadata = parse_task_metadata(task_md) if task_md.exists() else {}
    task_status = metadata.get("status", "")
    recommended_prompt = "prompts/task.execute.md"
    if task_status == "review":
        recommended_prompt = "prompts/task.close.md"

    missing_inputs: list[str] = []
    for filename in _REQUIRED_PACKET_FILES:
        if not (packet_dir / filename).exists():
            missing_inputs.append(f"missing packet file: {filename}")

    prompt_path = root / recommended_prompt
    if not prompt_path.exists():
        missing_inputs.append(f"missing prompt: {recommended_prompt}")

    payload = {
        "task_id": task_id,
        "packet_dir": str(packet_dir),
        "task_status": task_status,
        "recommended_prompt": recommended_prompt,
        "missing_inputs": missing_inputs,
        "ready": not missing_inputs,
    }

    result = CommandResult(
        ok=not missing_inputs,
        command="task prepare",
        repo=str(root),
        task_id=task_id,
        errors=list(missing_inputs),
    )
    return result, payload
