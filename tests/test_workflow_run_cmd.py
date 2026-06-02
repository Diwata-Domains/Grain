"""Tests for `forge workflow run` command."""

import json
import shutil
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _base_repo(repo: Path) -> None:
    _write(repo / "docs" / "runtime" / "PROJECT_RULES.md", "")
    shutil.copytree(
        Path(__file__).parent.parent / "templates" / "tasks",
        repo / "templates" / "tasks",
    )
    _write(
        repo / "docs" / "working" / "current_focus.md",
        "# Current Focus\n\n## Current Phase\nPhase 8 — Workflow Automation Runner Foundation\n",
    )
    _write(
        repo / "docs" / "working" / "current_task.md",
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: unset\n",
    )


def _ready_backlog(repo: Path, task_ref: str = "P8-T08") -> None:
    _write(
        repo / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            f"### {task_ref} — Example task\n"
            "- **Status:** ready\n"
        ),
    )


def _packet(
    repo: Path,
    task_ref: str,
    task_id: str,
    status: str,
    with_results: bool = False,
    with_handoff: bool = False,
) -> Path:
    dir_name = f"{task_ref}-{task_id}"
    packet_dir = repo / "tasks" / dir_name
    packet_dir.mkdir(parents=True, exist_ok=True)
    _write(
        packet_dir / "task.md",
        (
            "# Task: Example\n\n## Metadata\n"
            f"- **ID:** {task_id}\n"
            f"- **Status:** {status}\n"
            "- **Phase:** Phase 8 — Workflow Automation Runner Foundation\n"
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
    dir_name = f"{task_ref}-{task_id}"
    _write(
        repo / "docs" / "working" / "current_task.md",
        (
            "# Current Task\n\n"
            f"Task ID: {task_id}\n"
            f"Task Path: tasks/{dir_name}/\n"
            f"Status: {status}\n"
        ),
    )


def test_workflow_run_activates_ready_task(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path, "P8-T08")
    _packet(tmp_path, "P8-T08", "TASK-0068", "ready")

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    assert result.exit_code == 0, result.output
    assert "workflow run: ok" in result.output
    assert "action_taken      activate_task" in result.output
    assert "task_activated    TASK-0068" in result.output

    current_task = (tmp_path / "docs" / "working" / "current_task.md").read_text()
    assert "Task ID: TASK-0068" in current_task
    assert "Status: in_progress" in current_task
    assert "tasks/P8-T08-TASK-0068/" in current_task


def test_workflow_run_records_observability_on_activation(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path, "P8-T08")
    packet_dir = _packet(tmp_path, "P8-T08", "TASK-0068", "ready")

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    assert result.exit_code == 0, result.output
    payload = json.loads((packet_dir / "observability.json").read_text(encoding="utf-8"))
    assert payload["last_stage"] == "execute"
    assert payload["last_workflow_action"] == "workflow_run:activate_task"


def test_workflow_run_auto_created_packet_is_hydrated(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path, "P8-T08")

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    assert result.exit_code == 0, result.output
    packet_dir = tmp_path / "tasks" / "P8-T08-TASK-0001"
    task_md = (packet_dir / "task.md").read_text(encoding="utf-8")
    context_md = (packet_dir / "context.md").read_text(encoding="utf-8")
    plan_md = (packet_dir / "plan.md").read_text(encoding="utf-8")
    deliverable_md = (packet_dir / "deliverable_spec.md").read_text(encoding="utf-8")

    assert "[Title]" not in task_md
    assert "[phase name]" not in task_md
    assert "TASK-####" not in context_md
    assert "TASK-####" not in plan_md
    assert "TASK-####" not in deliverable_md


def test_workflow_run_activation_syncs_packet_and_backlog_to_in_progress(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path, "P8-T08")

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    assert result.exit_code == 0, result.output
    packet_dir = tmp_path / "tasks" / "P8-T08-TASK-0001"
    task_md = (packet_dir / "task.md").read_text(encoding="utf-8")
    backlog = (tmp_path / "docs" / "working" / "backlog.md").read_text(encoding="utf-8")

    assert "- **Status:** in_progress" in task_md
    assert "### P8-T08 — Example task\n- **Status:** in_progress" in backlog


def test_workflow_run_gates_on_in_progress_task(tmp_path):
    _base_repo(tmp_path)
    _packet(tmp_path, "P8-T08", "TASK-0068", "in_progress")
    _active_task(tmp_path, "TASK-0068", "P8-T08", "in_progress")
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T08 — Example task\n"
            "- **Status:** in_progress\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    assert result.exit_code == 0, result.output
    assert "workflow run: gated" in result.output
    assert "execution_in_flight" in result.output


def test_workflow_run_gates_on_blocked_task(tmp_path):
    _base_repo(tmp_path)
    _packet(tmp_path, "P8-T08", "TASK-0068", "blocked")
    _active_task(tmp_path, "TASK-0068", "P8-T08", "blocked")
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T08 — Example task\n"
            "- **Status:** blocked\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    assert result.exit_code == 0, result.output
    assert "workflow run: gated" in result.output
    assert "task_blocked" in result.output


def test_workflow_run_gates_on_review_ready_packet(tmp_path):
    _base_repo(tmp_path)
    _packet(tmp_path, "P8-T08", "TASK-0068", "review", with_results=True, with_handoff=True)
    _active_task(tmp_path, "TASK-0068", "P8-T08", "review")
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T08 — Example task\n"
            "- **Status:** review\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    assert result.exit_code == 0, result.output
    assert "workflow run: gated" in result.output
    assert "review_close_blocked" in result.output


def test_workflow_run_gates_on_planning_required(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T08 — Example task\n"
            "- **Status:** draft\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    assert result.exit_code == 0, result.output
    assert "workflow run: gated" in result.output
    assert "planning_required" in result.output


def test_workflow_run_gates_on_phase_boundary(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T01 — Lock minimal workflow automation slice\n"
            "- **Status:** done\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    assert result.exit_code == 0, result.output
    assert "workflow run: gated" in result.output
    assert "phase_boundary" in result.output


def test_workflow_run_gates_on_conflicting_ready_tasks(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T08 — Example task A\n"
            "- **Status:** ready\n\n"
            "### P8-T09 — Example task B\n"
            "- **Status:** ready\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    assert result.exit_code == 0, result.output
    assert "workflow run: gated" in result.output
    assert "ambiguous_next_action" in result.output


def test_workflow_run_json_output_includes_payload(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path, "P8-T08")
    _packet(tmp_path, "P8-T08", "TASK-0068", "ready")

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "--format", "json", "workflow", "run"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["command"] == "workflow run"
    assert "workflow_run" in data
    payload = data["workflow_run"]
    assert payload["action_taken"] == "activate_task"
    assert payload["task_activated"] == "TASK-0068"
    assert payload["gate_reason"] == ""
    assert payload["gate_condition"] == ""
    assert "recommended_prompt" in payload
    assert "active_phase" in payload
    assert "blocking_reasons" in payload
    assert "affected_artifacts" in payload


def test_workflow_run_json_output_gated_shape(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T08 — Example task\n"
            "- **Status:** draft\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "--format", "json", "workflow", "run"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    payload = data["workflow_run"]
    assert payload["action_taken"] == "none"
    assert payload["gate_reason"] == "planning_required"
    assert payload["task_activated"] == ""


def test_workflow_run_fails_when_required_docs_missing(tmp_path):
    # No docs at all — evaluate_workflow_state will return ok=False with stop_reason
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    # Should gate (exit 0) with required_docs_missing, not crash
    assert result.exit_code == 0, result.output
    assert "workflow run: gated" in result.output
    assert "required_docs_missing" in result.output


def test_workflow_run_does_not_mutate_state_on_gate(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T08 — Example task\n"
            "- **Status:** draft\n"
        ),
    )

    original = (tmp_path / "docs" / "working" / "current_task.md").read_text()

    runner = CliRunner()
    runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    after = (tmp_path / "docs" / "working" / "current_task.md").read_text()
    assert original == after, "current_task.md must not be mutated on a gate"


def test_workflow_next_routes_to_review_once_results_md_written(tmp_path):
    """Once results.md exists, in_progress task should route to review."""
    _base_repo(tmp_path)
    _packet(tmp_path, "P8-T08", "TASK-0068", "in_progress", with_results=True)
    _active_task(tmp_path, "TASK-0068", "P8-T08", "in_progress")
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T08 — Example task\n"
            "- **Status:** in_progress\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "--format", "json", "workflow", "next"])

    assert result.exit_code == 0, result.output
    import json
    data = json.loads(result.output)
    assert data["evaluation"]["ok"] is True
    assert data["evaluation"]["next_action"] == "task_review"
    assert data["evaluation"]["recommended_prompt"] == "prompts/task.review.md"


def test_workflow_run_gates_on_task_review_state(tmp_path):
    _base_repo(tmp_path)
    _packet(tmp_path, "P8-T08", "TASK-0068", "in_progress", with_results=True)
    _active_task(tmp_path, "TASK-0068", "P8-T08", "in_progress")
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T08 — Example task\n"
            "- **Status:** in_progress\n"
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    assert result.exit_code == 0, result.output
    assert "workflow run: gated" in result.output
    assert "human_review_required" in result.output
    assert "task_review" in result.output


# ---------------------------------------------------------------------------
# P15-T02: auto-packet bootstrap
# ---------------------------------------------------------------------------

def _ready_backlog_no_packet(repo: Path, task_ref: str = "P8-T01") -> None:
    """Seed a backlog with one ready task but no corresponding packet directory."""
    _write(
        repo / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            f"### {task_ref} — Example task\n"
            "- **Status:** ready\n"
        ),
    )
    # Ensure tasks/ dir exists but has no packet for this task_ref
    (repo / "tasks").mkdir(parents=True, exist_ok=True)


def _seed_templates(repo: Path) -> None:
    """Seed minimal task templates so create_packet_directory works."""
    import shutil
    from pathlib import Path as _Path
    templates_src = _Path(__file__).resolve().parents[1] / "src" / "grain" / "data" / "templates" / "tasks"
    templates_dst = repo / "templates" / "tasks"
    templates_dst.mkdir(parents=True, exist_ok=True)
    for f in templates_src.iterdir():
        shutil.copy(f, templates_dst / f.name)


def test_workflow_run_auto_creates_packet_when_missing(tmp_path):
    """workflow run creates a packet for a ready task that has no packet directory."""
    _base_repo(tmp_path)
    _ready_backlog_no_packet(tmp_path, task_ref="P8-T01")
    _seed_templates(tmp_path)

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    assert result.exit_code == 0, result.output
    assert "create_and_activate_task" in result.output
    assert "packet_created    true" in result.output

    # Packet directory was actually created
    task_dirs = list((tmp_path / "tasks").iterdir())
    assert len(task_dirs) == 1
    assert task_dirs[0].name.startswith("P8-T01-")


def test_workflow_run_auto_creates_packet_json_output(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog_no_packet(tmp_path, task_ref="P8-T01")
    _seed_templates(tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(tmp_path), "--format", "json", "workflow", "run"]
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["workflow_run"]["action_taken"] == "create_and_activate_task"
    assert data["workflow_run"]["packet_created"] is True


def test_workflow_run_simple_flag_creates_simple_packet(tmp_path):
    """--simple flag passes through to create a simple-mode packet."""
    _base_repo(tmp_path)
    _ready_backlog_no_packet(tmp_path, task_ref="P8-T01")
    _seed_templates(tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(tmp_path), "workflow", "run", "--simple"]
    )

    assert result.exit_code == 0, result.output
    task_dirs = list((tmp_path / "tasks").iterdir())
    assert len(task_dirs) == 1
    packet_dir = task_dirs[0]
    # Simple packet: task.md + results.md, no context/plan/deliverable_spec
    assert (packet_dir / "task.md").exists()
    assert (packet_dir / "results.md").exists()
    assert not (packet_dir / "context.md").exists()


def test_workflow_run_activates_existing_packet_unchanged(tmp_path):
    """workflow run still activates an existing packet normally (no auto-create)."""
    _base_repo(tmp_path)
    _ready_backlog(tmp_path, task_ref="P8-T08")
    _packet(tmp_path, "P8-T08", "TASK-0068", "ready")

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "workflow", "run"])

    assert result.exit_code == 0, result.output
    assert "activate_task" in result.output
    assert "packet_created" not in result.output
