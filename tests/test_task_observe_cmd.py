import json

from click.testing import CliRunner

from grain.cli import main


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _base_repo(repo):
    _write(repo / "docs" / "runtime" / "PROJECT_RULES.md", "")
    _write(
        repo / "docs" / "working" / "current_focus.md",
        "# Current Focus\n\n## Current Phase\nPhase 27 — Recipe Layer and Operator Ergonomics\nPhase 26 closed: 2026-05-06 — 5 tasks done (grain-verified)\n",
    )
    _write(
        repo / "docs" / "working" / "current_task.md",
        "# Current Task\n\nTask ID: TASK-0175\nTask Path: tasks/P27-T01-TASK-0175/\nStatus: in_progress\n",
    )
    _write(
        repo / "docs" / "working" / "backlog.md",
        "## 30. Phase 27 — Recipe Layer and Operator Ergonomics\n\n### P27-T01 — Task-level observability metadata and CLI surfaces\n- **Status:** in_progress\n",
    )
    packet_dir = repo / "tasks" / "P27-T01-TASK-0175"
    packet_dir.mkdir(parents=True, exist_ok=True)
    _write(
        packet_dir / "task.md",
        (
            "# Task: Observability\n\n## Metadata\n"
            "- **ID:** TASK-0175\n"
            "- **Status:** in_progress\n"
            "- **Phase:** Phase 27 — Recipe Layer and Operator Ergonomics\n"
        ),
    )
    _write(packet_dir / "context.md", "# Context\n")
    _write(packet_dir / "plan.md", "# Plan\n")
    _write(packet_dir / "deliverable_spec.md", "# Deliverable\n")


def test_task_observe_updates_packet_local_observability_file(tmp_path):
    _base_repo(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "--repo",
            str(tmp_path),
            "task",
            "observe",
            "--executor",
            "codex",
            "--model-class",
            "frontier_model",
            "--stage",
            "execute",
            "--action",
            "manual_execute",
        ],
    )

    assert result.exit_code == 0, result.output
    observability_path = tmp_path / "tasks" / "P27-T01-TASK-0175" / "observability.json"
    payload = json.loads(observability_path.read_text(encoding="utf-8"))
    assert payload["executor_identity"] == "codex"
    assert payload["model_class"] == "frontier_model"
    assert payload["last_stage"] == "execute"
    assert payload["last_workflow_action"] == "manual_execute"
    assert payload["started_at"].endswith("Z")


def test_task_observe_json_output_shows_existing_record(tmp_path):
    _base_repo(tmp_path)
    observability_path = tmp_path / "tasks" / "P27-T01-TASK-0175" / "observability.json"
    observability_path.write_text(
        json.dumps(
            {
                "task_id": "TASK-0175",
                "packet_dir": "tasks/P27-T01-TASK-0175",
                "executor_identity": "claude",
                "model_class": "reviewer_model",
                "last_stage": "review",
                "last_stage_at": "2026-05-06T12:00:00Z",
                "last_workflow_action": "review_handoff",
                "last_workflow_action_at": "2026-05-06T12:00:00Z",
                "started_at": "2026-05-06T11:00:00Z",
                "updated_at": "2026-05-06T12:00:00Z",
                "stage_timestamps": {"execute_at": "2026-05-06T11:00:00Z", "review_at": "2026-05-06T12:00:00Z"},
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "--format", "json", "task", "observe"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["task_id"] == "TASK-0175"
    assert data["observability"]["executor_identity"] == "claude"
    assert data["observability"]["last_workflow_action"] == "review_handoff"


def test_task_close_records_close_observability(tmp_path):
    _base_repo(tmp_path)
    packet_dir = tmp_path / "tasks" / "P27-T01-TASK-0175"

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--repo",
            str(tmp_path),
            "task",
            "close",
            "--id",
            "TASK-0175",
            "--quick",
            "--summary",
            "Implemented task observability.",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads((packet_dir / "observability.json").read_text(encoding="utf-8"))
    assert payload["last_stage"] == "close"
    assert payload["last_workflow_action"] == "task_close"
