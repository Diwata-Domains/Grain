"""Tests for `grain review approve` / `grain review reject` commands."""

import json

from click.testing import CliRunner

from grain.cli import main


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


_RESULTS_PENDING = """# Results: TASK-0179

## Summary
Implemented the demo.

## User Review
- **State:** pending
- **Summary:** [reviewer fills]
- **Resolution Mode:** [revise_current_task / replan_current_task / create_followup_task / close_task]

### Required Fixes
- None

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None

### Residual Risks
- None

## Verification Review
- **State:** waived
- **Summary:** No verifier configured.

### Findings
- None

## Closure Decision
- **Decision:** pending
- **Reason:** Awaiting review.

### Closure Blockers
- None
"""


def _base_repo(repo, status="review"):
    _write(repo / "docs" / "runtime" / "PROJECT_RULES.md", "")
    packet_dir = repo / "tasks" / "P28-T01-TASK-0179"
    _write(
        packet_dir / "task.md",
        (
            "# Task: Demo\n\n## Metadata\n"
            "- **ID:** TASK-0179\n"
            f"- **Status:** {status}\n"
            "- **Phase:** Phase 28 — Demo\n"
        ),
    )
    _write(packet_dir / "context.md", "# Context\n")
    _write(packet_dir / "plan.md", "# Plan\n")
    _write(packet_dir / "deliverable_spec.md", "# Deliverable\n")
    _write(packet_dir / "handoff.md", "# Handoff\nReady.\n")
    _write(packet_dir / "results.md", _RESULTS_PENDING)
    return packet_dir


def test_review_approve_sets_state_and_preserves_rest_of_file(tmp_path):
    packet_dir = _base_repo(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "review", "approve", "--id", "TASK-0179", "--summary", "Looks good."],
    )

    assert result.exit_code == 0, result.output
    assert "review approve: ok" in result.output
    text = (packet_dir / "results.md").read_text(encoding="utf-8")
    assert "## User Review\n- **State:** approved\n- **Summary:** Looks good." in text
    # default resolution for approve
    assert "- **Resolution Mode:** close_task" in text
    # everything else preserved byte-for-byte
    assert "## Summary\nImplemented the demo." in text
    assert "## Verification Review\n- **State:** waived" in text
    assert "## Closure Decision\n- **Decision:** pending" in text


def test_review_approve_enables_task_close_round_trip(tmp_path):
    """The point of the task: approve then task close succeeds."""
    _base_repo(tmp_path)
    runner = CliRunner()

    approve = runner.invoke(
        main,
        ["--repo", str(tmp_path), "review", "approve", "--id", "TASK-0179", "--summary", "Ship it."],
    )
    assert approve.exit_code == 0, approve.output

    check = runner.invoke(
        main,
        ["--repo", str(tmp_path), "review", "check", "--id", "TASK-0179"],
    )
    assert check.exit_code == 0, check.output
    assert "user_review_state approved" in check.output

    close = runner.invoke(
        main,
        ["--repo", str(tmp_path), "task", "close", "--id", "TASK-0179"],
    )
    assert close.exit_code == 0, close.output
    assert "task close: ok" in close.output


def test_review_reject_sets_rejected_state(tmp_path):
    packet_dir = _base_repo(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "review", "reject", "--id", "TASK-0179", "--summary", "Needs work."],
    )

    assert result.exit_code == 0, result.output
    text = (packet_dir / "results.md").read_text(encoding="utf-8")
    assert "- **State:** rejected" in text
    assert "- **Summary:** Needs work." in text
    assert "- **Resolution Mode:** revise_current_task" in text


def test_review_reject_blocks_task_close(tmp_path):
    _base_repo(tmp_path)
    runner = CliRunner()

    reject = runner.invoke(
        main,
        ["--repo", str(tmp_path), "review", "reject", "--id", "TASK-0179", "--summary", "No."],
    )
    assert reject.exit_code == 0, reject.output

    close = runner.invoke(
        main,
        ["--repo", str(tmp_path), "task", "close", "--id", "TASK-0179"],
    )
    assert close.exit_code != 0
    assert "approved" in close.output


def test_review_approve_custom_resolution(tmp_path):
    packet_dir = _base_repo(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "--repo",
            str(tmp_path),
            "review",
            "approve",
            "--id",
            "TASK-0179",
            "--summary",
            "Good, but follow up.",
            "--resolution",
            "create_followup_task",
        ],
    )

    assert result.exit_code == 0, result.output
    text = (packet_dir / "results.md").read_text(encoding="utf-8")
    assert "- **Resolution Mode:** create_followup_task" in text


def test_review_approve_refuses_missing_results(tmp_path):
    packet_dir = _base_repo(tmp_path)
    (packet_dir / "results.md").unlink()
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "review", "approve", "--id", "TASK-0179", "--summary", "x"],
    )

    assert result.exit_code != 0
    assert "results.md" in result.output


def test_review_approve_refuses_non_review_status(tmp_path):
    _base_repo(tmp_path, status="in_progress")
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "review", "approve", "--id", "TASK-0179", "--summary", "x"],
    )

    assert result.exit_code != 0
    assert "review" in result.output
    assert "in_progress" in result.output


def test_review_approve_missing_packet_exits_nonzero(tmp_path):
    _base_repo(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "review", "approve", "--id", "TASK-9999", "--summary", "x"],
    )

    assert result.exit_code != 0
    assert "not found" in result.output


def test_review_approve_json_output(tmp_path):
    _base_repo(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "--repo",
            str(tmp_path),
            "--format",
            "json",
            "review",
            "approve",
            "--id",
            "TASK-0179",
            "--summary",
            "Approved.",
        ],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["command"] == "review approve"
    assert data["task_id"] == "TASK-0179"
    assert data["review_decision"]["user_review_state"] == "approved"
    assert data["review_decision"]["summary"] == "Approved."
