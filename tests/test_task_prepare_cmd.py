"""Tests for `forge task prepare` command."""

import json

from click.testing import CliRunner

from forge.cli import main


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _create_packet(repo):
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(repo), "task", "create", "--phase", "8", "--task-num", "6"],
    )
    assert result.exit_code == 0, result.output


def test_task_prepare_reports_ok_when_prereqs_exist(packet_repo):
    _create_packet(packet_repo)
    _write(packet_repo / "prompts" / "task.execute.md", "# Prompt\n")

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "prepare", "--id", "TASK-0001"],
    )

    assert result.exit_code == 0, result.output
    assert "task prepare: ok" in result.output
    assert "missing_inputs    0" in result.output


def test_task_prepare_reports_missing_inputs(packet_repo):
    _create_packet(packet_repo)
    packet_dir = packet_repo / "tasks" / "P8-T06-TASK-0001"
    (packet_dir / "plan.md").unlink()
    _write(packet_repo / "prompts" / "task.execute.md", "# Prompt\n")

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "prepare", "--id", "TASK-0001"],
    )

    assert result.exit_code == 0, result.output
    assert "task prepare: missing_inputs" in result.output
    assert "missing packet file: plan.md" in result.output


def test_task_prepare_json_output(packet_repo):
    _create_packet(packet_repo)
    _write(packet_repo / "prompts" / "task.execute.md", "# Prompt\n")

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "--format", "json", "task", "prepare", "--id", "TASK-0001"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["command"] == "task prepare"
    assert data["prepare"]["task_id"] == "TASK-0001"
    assert data["prepare"]["ready"] is True


def test_task_prepare_missing_packet_exits_two(packet_repo):
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "prepare", "--id", "TASK-9999"],
    )

    assert result.exit_code == 2
