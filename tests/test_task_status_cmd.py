"""Tests for `forge task status` command."""

import subprocess
import sys
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main
from grain.domain.packets import parse_task_metadata

_ABT = str(Path(sys.executable).parent / "grain")


def _run_forge(*args) -> subprocess.CompletedProcess:
    return subprocess.run([_ABT, *args], capture_output=True, text=True)


def _create_packet(packet_repo, phase=3, task_num=1):
    runner = CliRunner()
    runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "create",
         "--phase", str(phase), "--task-num", str(task_num)],
    )


def test_task_status_valid_transition_exits_zero(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "status",
         "--id", "TASK-0001", "--status", "ready"],
    )
    assert result.exit_code == 0, result.output


def test_task_status_updates_task_md(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "status",
         "--id", "TASK-0001", "--status", "ready"],
    )
    packet_dir = packet_repo / "tasks" / "P3-T01-TASK-0001"
    metadata = parse_task_metadata(packet_dir / "task.md")
    assert metadata["status"] == "ready"


def test_task_status_output_shows_new_status(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "status",
         "--id", "TASK-0001", "--status", "ready"],
    )
    assert "ready" in result.output


def test_task_status_output_shows_updated_file(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "status",
         "--id", "TASK-0001", "--status", "ready"],
    )
    assert "task.md" in result.output


def test_task_status_unknown_packet_exits_two(packet_repo):
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "status",
         "--id", "TASK-9999", "--status", "ready"],
    )
    assert result.exit_code == 2


def test_task_status_missing_id_exits_two(packet_repo):
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "status", "--status", "ready"]
    )
    assert result.exit_code == 2


def test_task_status_missing_status_exits_two(packet_repo):
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "status", "--id", "TASK-0001"]
    )
    assert result.exit_code == 2


def test_task_status_invalid_transition_exits_five(tmp_path):
    # Use the live repo so `forge` can find a real manifest-bearing root;
    # create a real packet in a temp tasks dir isn't possible without full
    # repo structure — use subprocess against the live repo and a known
    # impossible transition from an existing packet.
    #
    # We need a real packet on disk that is in "draft" status, then try
    # to transition it directly to "done" (disallowed).
    import shutil
    # Set up a minimal repo that forge can resolve
    rules = tmp_path / "docs" / "runtime" / "PROJECT_RULES.md"
    rules.parent.mkdir(parents=True)
    rules.touch()
    templates_src = Path(__file__).parent.parent / "templates" / "tasks"
    templates_dst = tmp_path / "templates" / "tasks"
    shutil.copytree(templates_src, templates_dst)
    (tmp_path / "tasks").mkdir()

    # Create a packet
    result = _run_forge("--repo", str(tmp_path), "task", "create",
                      "--phase", "3", "--task-num", "8")
    assert result.returncode == 0

    # Attempt disallowed transition: draft -> done
    result = _run_forge("--repo", str(tmp_path), "task", "status",
                      "--id", "TASK-0001", "--status", "done")
    assert result.returncode == 5


def test_task_status_sequential_transitions(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()

    runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "status",
         "--id", "TASK-0001", "--status", "ready"],
    )
    runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "status",
         "--id", "TASK-0001", "--status", "in_progress"],
    )

    packet_dir = packet_repo / "tasks" / "P3-T01-TASK-0001"
    metadata = parse_task_metadata(packet_dir / "task.md")
    assert metadata["status"] == "in_progress"
