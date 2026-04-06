"""Tests for `forge review check` command."""

import json
from pathlib import Path

from click.testing import CliRunner

from forge.cli import main

_FIXTURES_DIR = Path(__file__).parent / "fixtures" / "phase5"


def _create_review_packet(packet_repo, phase=5, task_num=2):
    runner = CliRunner()
    runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "create", "--phase", str(phase), "--task-num", str(task_num)],
    )


def _mark_review_ready(packet_repo):
    packet_dir = packet_repo / "tasks" / "P5-T02-TASK-0001"
    task_md = packet_dir / "task.md"
    task_md.write_text(
        task_md.read_text(encoding="utf-8").replace("draft", "review", 1),
        encoding="utf-8",
    )
    (packet_dir / "results.md").write_text(
        (_FIXTURES_DIR / "review_results.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )


def test_review_check_ready_packet(packet_repo):
    _create_review_packet(packet_repo)
    _mark_review_ready(packet_repo)

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "review", "check", "--id", "TASK-0001"],
    )

    assert result.exit_code == 0, result.output
    assert "review check: ok" in result.output
    assert "ready" in result.output


def test_review_check_reports_blockers(packet_repo):
    _create_review_packet(packet_repo)

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "review", "check", "--id", "TASK-0001"],
    )

    assert result.exit_code != 0
    assert "results.md" in result.output


def test_review_check_json_output(packet_repo):
    _create_review_packet(packet_repo)
    _mark_review_ready(packet_repo)

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "--format", "json", "review", "check", "--id", "TASK-0001"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["command"] == "review check"
    assert data["task_id"] == "TASK-0001"
    assert data["status"] == "review"


def test_review_check_missing_packet_exits_two(packet_repo):
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "review", "check", "--id", "TASK-9999"],
    )

    assert result.exit_code == 2
