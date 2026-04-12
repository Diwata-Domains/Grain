"""Tests for `grain workflow loop` command."""

import json
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _base_repo(repo: Path) -> None:
    _write(repo / "docs" / "runtime" / "PROJECT_RULES.md", "")
    _write(
        repo / "docs" / "working" / "current_focus.md",
        "# Current Focus\n\n## Current Phase\nPhase 12 — Automated Workflow Loop\n",
    )
    _write(
        repo / "docs" / "working" / "current_task.md",
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: unset\n",
    )


def _write_loop_config(repo: Path, *, supervision: str = "gated", command: str = "true") -> None:
    _write(
        repo / "docs" / "runtime" / "workflow_loop.yaml",
        (
            "version: 1\n"
            f"supervision_level: {supervision}\n"
            "agents:\n"
            "  executor:\n"
            f"    command: \"{command}\"\n"
            "  reviewer:\n"
            f"    command: \"{command}\"\n"
            "  closer:\n"
            f"    command: \"{command}\"\n"
        ),
    )


def _packet(
    repo: Path,
    task_ref: str,
    task_id: str,
    status: str,
    *,
    with_results: bool = False,
    with_handoff: bool = False,
) -> Path:
    packet_dir = repo / "tasks" / f"{task_ref}-{task_id}"
    packet_dir.mkdir(parents=True, exist_ok=True)
    _write(
        packet_dir / "task.md",
        (
            "# Task: Example\n\n## Metadata\n"
            f"- **ID:** {task_id}\n"
            f"- **Status:** {status}\n"
            "- **Phase:** Phase 12 — Automated Workflow Loop\n"
        ),
    )
    _write(packet_dir / "context.md", "# Context\n")
    _write(packet_dir / "plan.md", "# Plan\n")
    _write(packet_dir / "deliverable_spec.md", "# Deliverable\n")
    if with_results:
        _write(packet_dir / "results.md", "# Results\nComplete.\n")
    if with_handoff:
        _write(packet_dir / "handoff.md", "# Handoff\nReady.\n")
    return packet_dir


def _active_task(repo: Path, task_id: str, task_ref: str, status: str) -> None:
    _write(
        repo / "docs" / "working" / "current_task.md",
        (
            "# Current Task\n\n"
            f"Task ID: {task_id}\n"
            f"Task Path: tasks/{task_ref}-{task_id}/\n"
            f"Status: {status}\n"
        ),
    )


def test_workflow_loop_supervised_stops_before_invocation(tmp_path: Path):
    _base_repo(tmp_path)
    _write_loop_config(tmp_path, supervision="supervised", command="false")
    _packet(tmp_path, "P12-T02", "TASK-0091", "in_progress")
    _active_task(tmp_path, "TASK-0091", "P12-T02", "in_progress")
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        "## 15. Phase 12 — Automated Workflow Loop\n\n### P12-T02 — Example\n- **Status:** in_progress\n",
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "loop"])

    assert result.exit_code == 0, result.output
    assert "workflow loop: ok" in result.output
    assert "stop_reason        supervision_required" in result.output
    assert "steps_completed    0" in result.output
    assert "steps_requested    25" in result.output


def test_workflow_loop_gated_stops_on_task_close_gate(tmp_path: Path):
    _base_repo(tmp_path)
    _write_loop_config(tmp_path, supervision="gated", command="true")
    _packet(tmp_path, "P12-T02", "TASK-0091", "review", with_results=True, with_handoff=True)
    _active_task(tmp_path, "TASK-0091", "P12-T02", "review")
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        "## 15. Phase 12 — Automated Workflow Loop\n\n### P12-T02 — Example\n- **Status:** review\n",
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "loop"])

    assert result.exit_code == 0, result.output
    assert "stop_reason        review_close_gate" in result.output
    assert "steps_completed    0" in result.output


def test_workflow_loop_invokes_executor_and_reports_no_state_change(tmp_path: Path):
    _base_repo(tmp_path)
    _write_loop_config(tmp_path, supervision="gated", command="true")
    _packet(tmp_path, "P12-T02", "TASK-0091", "in_progress")
    _active_task(tmp_path, "TASK-0091", "P12-T02", "in_progress")
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        "## 15. Phase 12 — Automated Workflow Loop\n\n### P12-T02 — Example\n- **Status:** in_progress\n",
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "loop", "--steps", "1"])

    assert result.exit_code == 0, result.output
    assert "steps_completed    1" in result.output
    assert "stop_reason        no_state_change" in result.output
    assert "step[1] action=task_execute stage=executor exit=0 changed=False dry_run=False" in result.output


def test_workflow_loop_json_output_shape(tmp_path: Path):
    _base_repo(tmp_path)
    _write_loop_config(tmp_path, supervision="gated", command="true")
    _packet(tmp_path, "P12-T02", "TASK-0091", "in_progress")
    _active_task(tmp_path, "TASK-0091", "P12-T02", "in_progress")
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        "## 15. Phase 12 — Automated Workflow Loop\n\n### P12-T02 — Example\n- **Status:** in_progress\n",
    )

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "--format", "json", "workflow", "loop", "--steps", "1"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["command"] == "workflow loop"
    assert "workflow_loop" in data
    payload = data["workflow_loop"]
    assert payload["supervision_level"] == "gated"
    assert payload["steps_completed"] == 1
    assert payload["stop_reason"] == "no_state_change"
    assert payload["steps_requested"] == 1
    assert len(payload["steps"]) == 1
    assert payload["steps"][0]["dry_run"] is False


def test_workflow_loop_dry_run_previews_without_state_mutation(tmp_path: Path):
    _base_repo(tmp_path)
    _write_loop_config(tmp_path, supervision="gated", command="false")
    _packet(tmp_path, "P12-T03", "TASK-0092", "ready")
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        "## 15. Phase 12 — Automated Workflow Loop\n\n### P12-T03 — Example\n- **Status:** ready\n",
    )

    before = (tmp_path / "docs" / "working" / "current_task.md").read_text(encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "loop", "--dry-run"])

    after = (tmp_path / "docs" / "working" / "current_task.md").read_text(encoding="utf-8")
    assert result.exit_code == 0, result.output
    assert "stop_reason        dry_run_preview" in result.output
    assert "dry_run=True" in result.output
    assert before == after
