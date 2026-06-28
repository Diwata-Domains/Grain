# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""Prompt recommendation service — surfaces the next prompt entrypoint for current state."""

from __future__ import annotations

import re
from pathlib import Path

from grain.cli.output import CommandResult

_METADATA_FIELD = re.compile(r"^-\s+([\w_]+):\s+(\S.*)")
_METADATA_SECTION = "Metadata:"


def show_prompt(root: Path) -> tuple[CommandResult, dict | None]:
    """Return the recommended prompt entrypoint for the current workflow state.

    Evaluates the current workflow state, extracts the recommended prompt from
    the evaluation, and enriches it with parsed prompt metadata (model class,
    scope, stage) when available.

    This is a read-only operation. It never mutates repo state.
    """
    from grain.services.workflow_service import evaluate_workflow_state

    result, evaluation = evaluate_workflow_state(root)
    if evaluation is None:
        return result, None

    recommended = evaluation.recommended_prompt or "prompts/task.execute.md"
    prompt_path = root / recommended
    metadata = _parse_prompt_metadata(prompt_path)

    payload: dict = {
        "recommended_prompt": recommended,
        "prompt_exists": prompt_path.exists(),
        "model_class": metadata.get("recommended_model_class", ""),
        "escalation_model_class": metadata.get("escalation_model_class", ""),
        "scope": metadata.get("scope", ""),
        "stage": metadata.get("stage", ""),
        "next_action": evaluation.next_action,
        "stop_reason": evaluation.stop_reason,
        "blocking_reasons": evaluation.blocking_reasons,
        "active_phase": evaluation.active_phase,
        "active_task_id": evaluation.active_task_id,
    }

    cmd_result = CommandResult(
        ok=evaluation.ok,
        command="prompt show",
        repo=str(root),
        errors=list(evaluation.blocking_reasons) if not evaluation.ok else [],
    )
    return cmd_result, payload


def _parse_prompt_metadata(prompt_path: Path) -> dict[str, str]:
    """Extract the Metadata: block from a prompt file."""
    if not prompt_path.exists():
        return {}
    metadata: dict[str, str] = {}
    in_metadata = False
    for line in prompt_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == _METADATA_SECTION:
            in_metadata = True
            continue
        if in_metadata:
            if not stripped or (stripped.startswith("#") and not stripped.startswith("##")):
                break
            m = _METADATA_FIELD.match(stripped)
            if m:
                metadata[m.group(1)] = m.group(2).strip()
    return metadata
