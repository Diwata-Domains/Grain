# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Task prepare service — prerequisite checks for one task packet."""

from pathlib import Path

from grain.cli.output import CommandResult
from grain.domain.packets import find_packet_dir, parse_task_metadata

_PLANNING_FILES = ("context.md", "plan.md", "deliverable_spec.md")
_STUB_MARKER = "TASK-####"


def _is_stub(file_path: Path) -> bool:
    """Return True if file exists but still contains unresolved template placeholders."""
    try:
        return _STUB_MARKER in file_path.read_text(encoding="utf-8")
    except OSError:
        return False


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
    task_mode = metadata.get("mode", "")
    is_simple = task_mode == "simple"

    recommended_prompt = "prompts/task.execute.md"
    if task_status == "review":
        recommended_prompt = "prompts/task.close.md"

    missing_inputs: list[str] = []

    if not task_md.exists():
        missing_inputs.append("missing packet file: task.md")

    if not is_simple:
        for filename in _PLANNING_FILES:
            fpath = packet_dir / filename
            if not fpath.exists():
                missing_inputs.append(f"missing packet file: {filename}")
            elif _is_stub(fpath):
                missing_inputs.append(
                    f"stub packet file: {filename} (contains unresolved placeholders — fill in before executing)"
                )

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
