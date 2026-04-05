"""Tests for `forge task list` command."""

import json

from click.testing import CliRunner

from forge.cli import main


def test_task_list_exits_zero_empty(packet_repo):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(packet_repo), "task", "list"])
    assert result.exit_code == 0


def test_task_list_empty_repo_shows_no_packets(packet_repo):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(packet_repo), "task", "list"])
    assert "no packets found" in result.output


def test_task_list_shows_created_packet(packet_repo):
    runner = CliRunner()
    runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "create", "--phase", "3", "--task-num", "1",
         "--title", "Test Task"],
    )
    result = runner.invoke(main, ["--repo", str(packet_repo), "task", "list"])
    assert result.exit_code == 0
    assert "TASK-0001" in result.output


def test_task_list_shows_status(packet_repo):
    runner = CliRunner()
    runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "create", "--phase", "3", "--task-num", "1"],
    )
    result = runner.invoke(main, ["--repo", str(packet_repo), "task", "list"])
    assert "draft" in result.output


def test_task_list_multiple_packets_sorted(packet_repo):
    runner = CliRunner()
    for task_num in (1, 2, 3):
        runner.invoke(
            main,
            ["--repo", str(packet_repo), "task", "create",
             "--phase", "3", "--task-num", str(task_num)],
        )
    result = runner.invoke(main, ["--repo", str(packet_repo), "task", "list"])
    assert result.exit_code == 0
    idx1 = result.output.index("TASK-0001")
    idx2 = result.output.index("TASK-0002")
    idx3 = result.output.index("TASK-0003")
    assert idx1 < idx2 < idx3


def test_task_list_packet_count_in_output(packet_repo):
    runner = CliRunner()
    for task_num in (1, 2):
        runner.invoke(
            main,
            ["--repo", str(packet_repo), "task", "create",
             "--phase", "3", "--task-num", str(task_num)],
        )
    result = runner.invoke(main, ["--repo", str(packet_repo), "task", "list"])
    assert "2 packets" in result.output


def test_task_list_json_output(packet_repo):
    runner = CliRunner()
    runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "create", "--phase", "3", "--task-num", "1"],
    )
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "--format", "json", "task", "list"]
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["ok"] is True
    assert len(data["packets"]) == 1
    assert data["packets"][0]["id"] == "TASK-0001"
    assert data["packets"][0]["status"] == "draft"


def test_task_list_warns_on_missing_task_md(packet_repo):
    # Create a directory that looks like a packet but has no task.md
    (packet_repo / "tasks" / "P3-T01-TASK-0001").mkdir()
    result = runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(packet_repo), "task", "list"])
    assert result.exit_code == 0
    assert "warning" in result.output
