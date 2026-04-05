"""Tests for `forge task create` command."""

import json

from click.testing import CliRunner

from forge.cli import main


def test_task_create_exits_zero(packet_repo):
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "create", "--phase", "3", "--task-num", "1"]
    )
    assert result.exit_code == 0, result.output


def test_task_create_output_shows_ok(packet_repo):
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "create", "--phase", "3", "--task-num", "1"]
    )
    assert "ok" in result.output


def test_task_create_output_shows_task_id(packet_repo):
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "create", "--phase", "3", "--task-num", "1"]
    )
    assert "TASK-0001" in result.output


def test_task_create_creates_packet_directory(packet_repo):
    runner = CliRunner()
    runner.invoke(
        main, ["--repo", str(packet_repo), "task", "create", "--phase", "3", "--task-num", "1"]
    )
    assert (packet_repo / "tasks" / "P3-T01-TASK-0001").exists()


def test_task_create_creates_required_files(packet_repo):
    runner = CliRunner()
    runner.invoke(
        main, ["--repo", str(packet_repo), "task", "create", "--phase", "3", "--task-num", "4"]
    )
    packet_dir = packet_repo / "tasks" / "P3-T04-TASK-0001"
    for filename in ("task.md", "context.md", "plan.md", "deliverable_spec.md"):
        assert (packet_dir / filename).exists(), f"missing {filename}"


def test_task_create_with_title(packet_repo):
    runner = CliRunner()
    runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "create", "--phase", "3", "--task-num", "1",
         "--title", "My Test Task"],
    )
    task_md = packet_repo / "tasks" / "P3-T01-TASK-0001" / "task.md"
    content = task_md.read_text()
    assert "My Test Task" in content
    assert "[Title]" not in content


def test_task_create_json_output(packet_repo):
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "--format", "json", "task", "create",
         "--phase", "3", "--task-num", "1"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["task_id"] == "TASK-0001"
    assert any("task.md" in f for f in data["files_created"])


def test_task_create_increments_id_on_second_call(packet_repo):
    runner = CliRunner()
    runner.invoke(
        main, ["--repo", str(packet_repo), "task", "create", "--phase", "3", "--task-num", "1"]
    )
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "create", "--phase", "3", "--task-num", "2"]
    )
    assert "TASK-0002" in result.output


def test_task_create_missing_phase_exits_two(packet_repo):
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "create", "--task-num", "1"]
    )
    assert result.exit_code == 2
