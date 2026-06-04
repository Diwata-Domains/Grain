"""Tests for `forge prompt show` command and prompt_service."""

import json

from click.testing import CliRunner

from grain.cli import main
from grain.services.prompt_service import _parse_prompt_metadata, show_prompt


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _base_repo(repo, task_status="unset", task_id="none", task_path="none"):
    _write(repo / "docs" / "runtime" / "PROJECT_RULES.md", "")
    _write(
        repo / "docs" / "working" / "current_focus.md",
        "# Current Focus\n\n## Current Phase\nPhase 8 — Workflow Automation Runner Foundation\n",
    )
    _write(
        repo / "docs" / "working" / "current_task.md",
        f"# Current Task\n\nTask ID: {task_id}\nTask Path: {task_path}\nStatus: {task_status}\n",
    )


def _ready_backlog(repo):
    _write(
        repo / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T07 — Add forge prompt show\n"
            "- **Status:** ready\n"
        ),
    )


# --- service unit tests ---


def test_parse_prompt_metadata_extracts_fields(tmp_path):
    prompt = tmp_path / "test_prompt.md"
    prompt.write_text(
        "# Title\n\nMetadata:\n- scope: task\n- stage: execute\n"
        "- recommended_model_class: open_model\n- escalation_model_class: frontier_model\n\n## Body\n",
        encoding="utf-8",
    )
    meta = _parse_prompt_metadata(prompt)
    assert meta["scope"] == "task"
    assert meta["stage"] == "execute"
    assert meta["recommended_model_class"] == "open_model"
    assert meta["escalation_model_class"] == "frontier_model"


def test_parse_prompt_metadata_missing_file_returns_empty(tmp_path):
    meta = _parse_prompt_metadata(tmp_path / "nonexistent.md")
    assert meta == {}


def test_show_prompt_returns_payload_for_ready_task(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path)
    _write(
        tmp_path / "prompts" / "task.execute.md",
        "# Execute\n\nMetadata:\n- scope: task\n- stage: execute\n"
        "- recommended_model_class: open_model\n- escalation_model_class: frontier_model\n",
    )
    result, payload = show_prompt(tmp_path)
    assert result.ok
    assert payload is not None
    assert payload["recommended_prompt"] == "prompts/task.execute.md"
    assert payload["prompt_exists"] is True
    assert payload["model_class"] == "open_model"
    assert payload["next_action"] == "task_execute"


def test_show_prompt_prompt_missing_from_disk_still_returns_payload(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path)
    # Do NOT create the prompt file
    result, payload = show_prompt(tmp_path)
    assert payload is not None
    assert payload["recommended_prompt"] == "prompts/task.execute.md"
    assert payload["prompt_exists"] is False
    assert payload["model_class"] == ""


# --- CLI tests ---


def test_prompt_show_exits_zero_for_ready_state(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "prompt", "show"])
    assert result.exit_code == 0, result.output


def test_prompt_show_text_output_includes_recommended_prompt(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "prompt", "show"])
    assert "recommended_prompt" in result.output
    assert "task.execute.md" in result.output


def test_prompt_show_text_output_includes_next_action(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "prompt", "show"])
    assert "task_execute" in result.output


def test_prompt_show_json_output_has_prompt_key(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(tmp_path), "--format", "json", "prompt", "show"]
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert "prompt" in data
    assert data["prompt"]["recommended_prompt"] == "prompts/task.execute.md"
    assert data["prompt"]["next_action"] == "task_execute"


def test_prompt_show_json_includes_model_class_when_prompt_exists(tmp_path):
    _base_repo(tmp_path)
    _ready_backlog(tmp_path)
    _write(
        tmp_path / "prompts" / "task.execute.md",
        "# Execute\n\nMetadata:\n- scope: task\n- stage: execute\n"
        "- recommended_model_class: open_model\n- escalation_model_class: frontier_model\n",
    )
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(tmp_path), "--format", "json", "prompt", "show"]
    )
    data = json.loads(result.output)
    assert data["prompt"]["model_class"] == "open_model"
    assert data["prompt"]["scope"] == "task"
    assert data["prompt"]["stage"] == "execute"


def test_prompt_show_stopped_state_still_returns_zero(tmp_path):
    _base_repo(tmp_path)
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        "## 10. Phase 8 — Workflow Automation Runner Foundation\n",
    )
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "prompt", "show"])
    # Stopped state should still exit 0 and surface a stop_reason
    assert result.exit_code == 0, result.output
    assert "stop_reason" in result.output


def test_prompt_show_task_review_state_recommends_close_prompt(tmp_path):
    # Create a valid packet in review state (all required files present)
    packet_dir = tmp_path / "tasks" / "P8-T07-TASK-0001"
    packet_dir.mkdir(parents=True)
    (packet_dir / "task.md").write_text(
        "# Task\n\n## Metadata\n- **ID:** TASK-0001\n- **Status:** review\n- **Phase:** Phase 8\n",
        encoding="utf-8",
    )
    for name in ("context.md", "plan.md", "deliverable_spec.md", "handoff.md"):
        (packet_dir / name).write_text(f"# {name}\ncontent", encoding="utf-8")
    # results.md must have user_review_state=approved for close to be recommended
    (packet_dir / "results.md").write_text(
        "# Results: TASK-0001\n\n## Summary\nWork completed.\n\n"
        "## User Review\n- **State:** approved\n- **Summary:** Ready to close.\n"
        "- **Resolution Mode:** close_task\n",
        encoding="utf-8",
    )

    _base_repo(tmp_path, task_status="review", task_id="TASK-0001", task_path="tasks/P8-T07-TASK-0001")
    _write(tmp_path / "docs" / "working" / "backlog.md", "")

    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(tmp_path), "--format", "json", "prompt", "show"]
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert "close" in data["prompt"]["recommended_prompt"]


def test_prompt_show_in_progress_task_with_results_recommends_review_prompt(tmp_path):
    packet_dir = tmp_path / "tasks" / "P8-T07-TASK-0001"
    packet_dir.mkdir(parents=True)
    (packet_dir / "task.md").write_text(
        "# Task\n\n## Metadata\n- **ID:** TASK-0001\n- **Status:** in_progress\n- **Phase:** Phase 8\n",
        encoding="utf-8",
    )
    for name in ("context.md", "plan.md", "deliverable_spec.md", "results.md"):
        (packet_dir / name).write_text(f"# {name}\ncontent", encoding="utf-8")

    _base_repo(tmp_path, task_status="in_progress", task_id="TASK-0001", task_path="tasks/P8-T07-TASK-0001")
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 10. Phase 8 — Workflow Automation Runner Foundation\n\n"
            "### P8-T07 — Add forge prompt show\n"
            "- **Status:** in_progress\n"
        ),
    )
    _write(
        tmp_path / "prompts" / "task.review.md",
        "# Review\n\nMetadata:\n- scope: task\n- stage: review\n- recommended_model_class: reviewer_model\n",
    )

    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(tmp_path), "--format", "json", "prompt", "show"]
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["prompt"]["recommended_prompt"] == "prompts/task.review.md"
    assert data["prompt"]["next_action"] == "task_review"
