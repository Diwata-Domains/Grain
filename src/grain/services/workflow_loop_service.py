"""Workflow loop service for repeated state-driven execution."""

from __future__ import annotations

import shlex
import subprocess
import time
from pathlib import Path
from typing import Any

from grain.cli.output import CommandResult
from grain.services.workflow_loop_config_service import load_workflow_loop_config
from grain.services.workflow_run_service import run_workflow_step
from grain.services.workflow_service import evaluate_workflow_state

DEFAULT_MAX_LOOP_STEPS = 25


def run_workflow_loop(
    root: Path,
    *,
    steps: int | None = None,
    supervision_level_override: str | None = None,
    dry_run: bool = False,
) -> tuple[CommandResult, dict[str, Any] | None]:
    """Run workflow loop until stop condition or step limit.

    The loop can activate ready tasks through ``workflow run`` behavior and can
    invoke stage agents for execute/close actions.
    """
    try:
        config = load_workflow_loop_config(
            root,
            supervision_level_override=supervision_level_override,
        )
    except Exception as exc:  # pragma: no cover - normalized to command error
        return (
            CommandResult(
                ok=False,
                command="workflow loop",
                repo=str(root),
                errors=[str(exc)],
            ),
            None,
        )

    progress: list[dict[str, Any]] = []
    steps_requested = steps if steps is not None else DEFAULT_MAX_LOOP_STEPS

    while True:
        result, evaluation = evaluate_workflow_state(root)
        if evaluation is None:
            return result, None

        if not evaluation.ok:
            return (
                CommandResult(
                    ok=False,
                    command="workflow loop",
                    repo=str(root),
                    errors=list(evaluation.blocking_reasons),
                ),
                _payload(
                    supervision_level=config.supervision_level,
                    steps_requested=steps_requested,
                    steps_completed=len(progress),
                    stop_reason="state_gate",
                    active_phase=evaluation.active_phase,
                    active_task_id=evaluation.active_task_id,
                    recommended_prompt=evaluation.recommended_prompt,
                    steps=progress,
                    blocking_reasons=list(evaluation.blocking_reasons),
                ),
            )

        if len(progress) >= steps_requested:
            return (
                CommandResult(
                    ok=True,
                    command="workflow loop",
                    repo=str(root),
                ),
                _payload(
                    supervision_level=config.supervision_level,
                    steps_requested=steps_requested,
                    steps_completed=len(progress),
                    stop_reason="steps_limit_reached",
                    active_phase=evaluation.active_phase,
                    active_task_id=evaluation.active_task_id,
                    recommended_prompt=evaluation.recommended_prompt,
                    steps=progress,
                    blocking_reasons=[],
                ),
            )

        next_action = evaluation.next_action
        if dry_run:
            if next_action == "task_execute" and not evaluation.active_task_id:
                progress.append(
                    {
                        "index": len(progress) + 1,
                        "action": "activate_task",
                        "stage": "system",
                        "prompt": evaluation.recommended_prompt or "prompts/task.execute.md",
                        "command": "workflow_run.activate_task",
                        "exit_code": 0,
                        "changed_state": False,
                        "dry_run": True,
                        "duration_ms": 0,
                        "detail": "would activate ready task",
                    }
                )
            else:
                stage = _stage_for_action(next_action)
                stage_config = config.stages.for_stage(stage)
                prompt_path = evaluation.recommended_prompt or _default_prompt(next_action)
                progress.append(
                    {
                        "index": len(progress) + 1,
                        "action": next_action,
                        "stage": stage,
                        "prompt": prompt_path,
                        "command": " ".join(_build_command(stage_config, prompt_path)),
                        "exit_code": 0,
                        "changed_state": False,
                        "dry_run": True,
                        "duration_ms": 0,
                        "detail": "dry-run only; command not executed",
                    }
                )

            return (
                CommandResult(
                    ok=True,
                    command="workflow loop",
                    repo=str(root),
                    warnings=["dry-run: no stage commands executed and no state files mutated"],
                ),
                _payload(
                    supervision_level=config.supervision_level,
                    steps_requested=steps_requested,
                    steps_completed=len(progress),
                    stop_reason="dry_run_preview",
                    active_phase=evaluation.active_phase,
                    active_task_id=evaluation.active_task_id,
                    recommended_prompt=evaluation.recommended_prompt,
                    steps=progress,
                    blocking_reasons=[],
                ),
            )

        if config.supervision_level == "supervised":
            return (
                CommandResult(
                    ok=True,
                    command="workflow loop",
                    repo=str(root),
                ),
                _payload(
                    supervision_level=config.supervision_level,
                    steps_requested=steps_requested,
                    steps_completed=len(progress),
                    stop_reason="supervision_required",
                    active_phase=evaluation.active_phase,
                    active_task_id=evaluation.active_task_id,
                    recommended_prompt=evaluation.recommended_prompt,
                    steps=progress,
                    blocking_reasons=[
                        f"operator approval required before action: {next_action or 'none'}"
                    ],
                ),
            )

        if config.supervision_level == "gated" and next_action == "task_close":
            return (
                CommandResult(
                    ok=True,
                    command="workflow loop",
                    repo=str(root),
                ),
                _payload(
                    supervision_level=config.supervision_level,
                    steps_requested=steps_requested,
                    steps_completed=len(progress),
                    stop_reason="review_close_gate",
                    active_phase=evaluation.active_phase,
                    active_task_id=evaluation.active_task_id,
                    recommended_prompt=evaluation.recommended_prompt,
                    steps=progress,
                    blocking_reasons=["gated mode stops at task_close"],
                ),
            )

        # If workflow reports task_execute with no active task, activate one
        # first and continue the loop.
        if next_action == "task_execute" and not evaluation.active_task_id:
            activate_result, activate_payload = run_workflow_step(root)
            step_record: dict[str, Any] = {
                "index": len(progress) + 1,
                "action": "activate_task",
                "stage": "system",
                "prompt": evaluation.recommended_prompt or "prompts/task.execute.md",
                "command": "workflow_run.activate_task",
                "exit_code": 0 if activate_result.ok else 1,
                "changed_state": bool(activate_result.ok),
                "dry_run": False,
                "duration_ms": 0,
                "detail": "",
            }
            if activate_payload:
                step_record["detail"] = activate_payload.get("action_taken", "")
            progress.append(step_record)
            if not activate_result.ok:
                return (
                    CommandResult(
                        ok=False,
                        command="workflow loop",
                        repo=str(root),
                        errors=list(activate_result.errors),
                    ),
                    _payload(
                        supervision_level=config.supervision_level,
                        steps_requested=steps_requested,
                        steps_completed=len(progress),
                        stop_reason="activation_failed",
                        active_phase=evaluation.active_phase,
                        active_task_id=evaluation.active_task_id,
                        recommended_prompt=evaluation.recommended_prompt,
                        steps=progress,
                        blocking_reasons=list(activate_result.errors),
                    ),
                )
            continue

        stage = _stage_for_action(next_action)
        stage_config = config.stages.for_stage(stage)
        prompt_path = evaluation.recommended_prompt or _default_prompt(next_action)
        started = time.perf_counter()
        invocation = _invoke_stage(stage_config, prompt_path, root)
        duration_ms = int((time.perf_counter() - started) * 1000)

        step_record = {
            "index": len(progress) + 1,
            "action": next_action,
            "stage": stage,
            "prompt": prompt_path,
            "command": invocation["command"],
            "exit_code": invocation["exit_code"],
            "changed_state": False,
            "dry_run": False,
            "duration_ms": duration_ms,
            "detail": "",
        }
        progress.append(step_record)

        if invocation["exit_code"] != 0:
            return (
                CommandResult(
                    ok=False,
                    command="workflow loop",
                    repo=str(root),
                    errors=[f"stage invocation failed for {stage}"],
                ),
                _payload(
                    supervision_level=config.supervision_level,
                    steps_requested=steps_requested,
                    steps_completed=len(progress),
                    stop_reason="invocation_failed",
                    active_phase=evaluation.active_phase,
                    active_task_id=evaluation.active_task_id,
                    recommended_prompt=prompt_path,
                    steps=progress,
                    blocking_reasons=[invocation.get("stderr", "").strip() or "non-zero exit"],
                ),
            )

        _, new_evaluation = evaluate_workflow_state(root)
        if new_evaluation is None:
            return (
                CommandResult(
                    ok=False,
                    command="workflow loop",
                    repo=str(root),
                    errors=["workflow state unavailable after invocation"],
                ),
                None,
            )

        changed = _state_signature(evaluation) != _state_signature(new_evaluation)
        step_record["changed_state"] = changed
        if not changed:
            return (
                CommandResult(
                    ok=True,
                    command="workflow loop",
                    repo=str(root),
                ),
                _payload(
                    supervision_level=config.supervision_level,
                    steps_requested=steps_requested,
                    steps_completed=len(progress),
                    stop_reason="no_state_change",
                    active_phase=new_evaluation.active_phase,
                    active_task_id=new_evaluation.active_task_id,
                    recommended_prompt=new_evaluation.recommended_prompt,
                    steps=progress,
                    blocking_reasons=["stage invocation completed but workflow state did not change"],
                ),
            )


def _stage_for_action(action: str) -> str:
    if action == "task_close":
        return "closer"
    return "executor"


def _default_prompt(action: str) -> str:
    if action == "task_close":
        return "prompts/task.close.md"
    if action == "task_planning":
        return "prompts/task.plan.next.md"
    return "prompts/task.execute.md"


def _invoke_stage(stage_config, prompt_path: str, root: Path) -> dict[str, Any]:
    command = _build_command(stage_config, prompt_path)
    completed = subprocess.run(  # noqa: S603
        command,
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "command": " ".join(command),
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def _build_command(stage_config, prompt_path: str) -> list[str]:
    if stage_config.mode == "command":
        base = shlex.split(stage_config.command)
    else:
        base = [stage_config.shortcut]
        if stage_config.model:
            base.extend(["--model", stage_config.model])
    return [*base, prompt_path]


def _state_signature(evaluation) -> tuple[Any, ...]:
    return (
        evaluation.ok,
        evaluation.next_action,
        evaluation.stop_reason,
        evaluation.active_task_id,
        tuple(evaluation.blocking_reasons),
    )


def _payload(
    *,
    supervision_level: str,
    steps_requested: int,
    steps_completed: int,
    stop_reason: str,
    active_phase: str,
    active_task_id: str,
    recommended_prompt: str,
    steps: list[dict[str, Any]],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    return {
        "supervision_level": supervision_level,
        "steps_requested": steps_requested,
        "steps_completed": steps_completed,
        "stop_reason": stop_reason,
        "active_phase": active_phase,
        "active_task_id": active_task_id,
        "recommended_prompt": recommended_prompt,
        "blocking_reasons": blocking_reasons,
        "steps": steps,
    }
