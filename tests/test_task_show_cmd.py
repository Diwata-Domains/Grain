"""Tests for `forge task show` command."""

import json

from click.testing import CliRunner

from forge.cli import main


def _create_packet(packet_repo, phase=3, task_num=1, title="Test Task"):
    runner = CliRunner()
    runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "create",
         "--phase", str(phase), "--task-num", str(task_num), "--title", title],
    )


def test_task_show_exits_zero(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "show", "--id", "TASK-0001"]
    )
    assert result.exit_code == 0, result.output


def test_task_show_displays_id(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "show", "--id", "TASK-0001"]
    )
    assert "TASK-0001" in result.output


def test_task_show_displays_status(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "show", "--id", "TASK-0001"]
    )
    assert "draft" in result.output


def test_task_show_displays_file_inventory(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "show", "--id", "TASK-0001"]
    )
    assert "task.md" in result.output
    assert "present" in result.output
    assert "results.md" in result.output
    assert "absent" in result.output


def test_task_show_unknown_id_exits_two(packet_repo):
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "show", "--id", "TASK-9999"]
    )
    assert result.exit_code == 2


def test_task_show_missing_id_option_exits_two(packet_repo):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(packet_repo), "task", "show"])
    assert result.exit_code == 2


def test_task_show_json_output(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "--format", "json", "task", "show", "--id", "TASK-0001"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["packet"]["id"] == "TASK-0001"
    assert data["packet"]["status"] == "draft"
    assert "task.md" in data["packet"]["files"]
    assert data["packet"]["files"]["task.md"] is True
    assert data["packet"]["files"]["results.md"] is False


def test_task_show_displays_path(packet_repo):
    _create_packet(packet_repo, phase=3, task_num=6)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "show", "--id", "TASK-0001"]
    )
    assert "P3-T06-TASK-0001" in result.output
