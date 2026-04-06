"""Tests for `forge review handoff` command."""

import json
from pathlib import Path

from click.testing import CliRunner

from forge.cli import main

_FIXTURES_DIR = Path(__file__).parent / "fixtures" / "phase5"


def _create_review_packet(packet_repo, phase=5, task_num=4):
    runner = CliRunner()
    runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "create", "--phase", str(phase), "--task-num", str(task_num)],
    )


def _mark_handoff_ready(packet_repo, status="review"):
    packet_dir = packet_repo / "tasks" / "P5-T04-TASK-0001"
    task_md = packet_dir / "task.md"
    current = task_md.read_text(encoding="utf-8")
    task_md.write_text(current.replace("draft", status, 1), encoding="utf-8")
    (packet_dir / "results.md").write_text(
        (_FIXTURES_DIR / "review_results.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )


def test_review_handoff_generates_default_artifact(packet_repo):
    _create_review_packet(packet_repo)
    _mark_handoff_ready(packet_repo, status="review")

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "review", "handoff", "--id", "TASK-0001"],
    )

    assert result.exit_code == 0, result.output
    assert "review handoff: ok" in result.output
    assert (packet_repo / "tasks" / "P5-T04-TASK-0001" / "handoff.md").exists()


def test_review_handoff_supports_custom_output(packet_repo):
    _create_review_packet(packet_repo)
    _mark_handoff_ready(packet_repo, status="done")
    packet_dir = packet_repo / "tasks" / "P5-T04-TASK-0001"
    task_md = packet_dir / "task.md"
    task_md.write_text(
        task_md.read_text(encoding="utf-8").replace("review", "done", 1),
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--repo",
            str(packet_repo),
            "review",
            "handoff",
            "--id",
            "TASK-0001",
            "--output",
            "exports/handoff.md",
        ],
    )

    assert result.exit_code == 0, result.output
    assert (packet_repo / "exports" / "handoff.md").exists()


def test_review_handoff_json_output(packet_repo):
    _create_review_packet(packet_repo)
    _mark_handoff_ready(packet_repo, status="review")

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--repo",
            str(packet_repo),
            "--format",
            "json",
            "review",
            "handoff",
            "--id",
            "TASK-0001",
        ],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["command"] == "review handoff"
    assert data["task_id"] == "TASK-0001"
    assert data["files_updated"]


def test_review_handoff_missing_packet_exits_two(packet_repo):
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "review", "handoff", "--id", "TASK-9999"],
    )

    assert result.exit_code == 2


def test_review_handoff_incomplete_packet_exits_three(packet_repo):
    _create_review_packet(packet_repo)

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "review", "handoff", "--id", "TASK-0001"],
    )

    assert result.exit_code != 0
