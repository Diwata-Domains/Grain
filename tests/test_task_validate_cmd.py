"""Tests for `forge task validate` command."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main

_ABT = str(Path(sys.executable).parent / "grain")


def _run_forge(*args) -> subprocess.CompletedProcess:
    return subprocess.run([_ABT, *args], capture_output=True, text=True)


def _setup_subprocess_repo(tmp_path: Path) -> Path:
    (tmp_path / "docs" / "runtime").mkdir(parents=True)
    (tmp_path / "docs" / "runtime" / "PROJECT_RULES.md").touch()
    shutil.copytree(
        Path(__file__).parent.parent / "templates" / "tasks",
        tmp_path / "templates" / "tasks",
    )
    (tmp_path / "tasks").mkdir()
    return tmp_path


def _create_packet(packet_repo, phase=3, task_num=1):
    runner = CliRunner()
    runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "create",
         "--phase", str(phase), "--task-num", str(task_num)],
    )


# --- single packet validation ---

def test_validate_one_valid_packet_exits_zero(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "validate", "--id", "TASK-0001"]
    )
    assert result.exit_code == 0, result.output


def test_validate_one_valid_packet_shows_ok(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "validate", "--id", "TASK-0001"]
    )
    assert "ok" in result.output


def test_validate_one_unknown_packet_exits_two(packet_repo):
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "validate", "--id", "TASK-9999"]
    )
    assert result.exit_code == 2


def test_validate_one_invalid_packet_exits_three(tmp_path):
    repo = _setup_subprocess_repo(tmp_path)
    # Create packet then delete a required file to make it invalid
    _run_forge("--repo", str(repo), "task", "create", "--phase", "3", "--task-num", "10")
    (repo / "tasks" / "P3-T10-TASK-0001" / "plan.md").unlink()
    result = _run_forge("--repo", str(repo), "task", "validate", "--id", "TASK-0001")
    assert result.returncode == 3


def test_validate_one_json_output(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "--format", "json", "task", "validate",
         "--id", "TASK-0001"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["errors"] == []


def test_validate_one_legacy_packet_without_adapter_metadata_exits_zero(tmp_path):
    repo = _setup_subprocess_repo(tmp_path)
    _run_forge("--repo", str(repo), "task", "create", "--phase", "3", "--task-num", "10")

    task_md = repo / "tasks" / "P3-T10-TASK-0001" / "task.md"
    content = task_md.read_text(encoding="utf-8")
    content = content.replace("- **Primary Adapter:** none\n", "")
    content = content.replace("- **Secondary Adapters:** none\n", "")
    task_md.write_text(content, encoding="utf-8")

    result = _run_forge("--repo", str(repo), "task", "validate", "--id", "TASK-0001")
    assert result.returncode == 0


# --- validate all ---

def test_validate_all_empty_exits_zero(packet_repo):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(packet_repo), "task", "validate", "--all"])
    assert result.exit_code == 0


def test_validate_all_valid_packets_exits_zero(packet_repo):
    _create_packet(packet_repo, task_num=1)
    _create_packet(packet_repo, task_num=2)
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(packet_repo), "task", "validate", "--all"])
    assert result.exit_code == 0


def test_validate_all_default_when_no_flag(packet_repo):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(packet_repo), "task", "validate"])
    assert result.exit_code == 0


def test_validate_all_with_invalid_packet_exits_three(tmp_path):
    repo = _setup_subprocess_repo(tmp_path)
    _run_forge("--repo", str(repo), "task", "create", "--phase", "3", "--task-num", "10")
    (repo / "tasks" / "P3-T10-TASK-0001" / "context.md").unlink()
    result = _run_forge("--repo", str(repo), "task", "validate", "--all")
    assert result.returncode == 3


def test_validate_id_and_all_together_exits_two(packet_repo):
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "validate",
         "--id", "TASK-0001", "--all"],
    )
    assert result.exit_code == 2
