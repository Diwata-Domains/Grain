"""Tests for `forge review summary` command."""

import json
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main

_FIXTURES_DIR = Path(__file__).parent / "fixtures" / "phase5"


def _create_review_packet(packet_repo, phase=5, task_num=5):
    runner = CliRunner()
    runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "create", "--phase", str(phase), "--task-num", str(task_num)],
    )


def _mark_summary_ready(packet_repo):
    packet_dir = packet_repo / "tasks" / "P5-T05-TASK-0001"
    task_md = packet_dir / "task.md"
    task_md.write_text(
        task_md.read_text(encoding="utf-8").replace("draft", "review", 1),
        encoding="utf-8",
    )
    (packet_dir / "results.md").write_text(
        (_FIXTURES_DIR / "review_results.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )


def test_review_summary_reports_packet_state(packet_repo):
    _create_review_packet(packet_repo)
    _mark_summary_ready(packet_repo)

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "review", "summary", "--id", "TASK-0001"],
    )

    assert result.exit_code == 0, result.output
    assert "review summary: ok" in result.output
    assert "review_ready      yes" in result.output
    assert "next_actions" in result.output
    assert "grain review handoff" in result.output


def test_review_summary_json_output(packet_repo):
    _create_review_packet(packet_repo)
    _mark_summary_ready(packet_repo)

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--repo",
            str(packet_repo),
            "--format",
            "json",
            "review",
            "summary",
            "--id",
            "TASK-0001",
        ],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["command"] == "review summary"
    assert data["task_id"] == "TASK-0001"
    assert data["summary"]["packet_status"] == "review"
    assert data["summary"]["recommended_next_status"] == "done"
    assert data["summary"]["next_actions"]


def test_review_summary_reports_blockers(packet_repo):
    _create_review_packet(packet_repo)

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "review", "summary", "--id", "TASK-0001"],
    )

    assert result.exit_code == 0, result.output
    assert "review summary: ok" in result.output
    assert "validation_findings" in result.output
    assert "results.md" in result.output


def test_review_summary_missing_packet_exits_two(packet_repo):
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "review", "summary", "--id", "TASK-9999"],
    )

    assert result.exit_code == 2
