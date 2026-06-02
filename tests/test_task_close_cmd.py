"""Tests for `grain task close` command."""

import shutil
import subprocess
import sys
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main
from grain.domain.packets import parse_task_metadata

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


_APPROVED_RESULTS = """# Results: TASK-0001

## Summary
Work completed.

## User Review
- **State:** approved
- **Summary:** Ready to close.
- **Resolution Mode:** close_task

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
- **State:** not_run
- **Summary:** No verifier configured.

### Findings
- None

## Closure Decision
- **Decision:** pending
- **Reason:** Awaiting close command.

### Closure Blockers
- None
"""


def _make_closure_ready(packet_repo) -> None:
    """Create a packet and advance it to review with a results.md."""
    runner = CliRunner()
    runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "create",
         "--phase", "3", "--task-num", "12"],
    )
    # draft -> ready -> in_progress -> review
    for status in ("ready", "in_progress", "review"):
        runner.invoke(
            main,
            ["--repo", str(packet_repo), "task", "status",
             "--id", "TASK-0001", "--status", status],
        )
    # Write results.md
    packet_dir = packet_repo / "tasks" / "P3-T12-TASK-0001"
    (packet_dir / "results.md").write_text(_APPROVED_RESULTS)


def test_task_close_exits_zero(packet_repo):
    _make_closure_ready(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "close", "--id", "TASK-0001"]
    )
    assert result.exit_code == 0, result.output


def test_task_close_sets_status_done(packet_repo):
    _make_closure_ready(packet_repo)
    runner = CliRunner()
    runner.invoke(
        main, ["--repo", str(packet_repo), "task", "close", "--id", "TASK-0001"]
    )
    packet_dir = packet_repo / "tasks" / "P3-T12-TASK-0001"
    metadata = parse_task_metadata(packet_dir / "task.md")
    assert metadata["status"] == "done"


def test_task_close_output_shows_done(packet_repo):
    _make_closure_ready(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "close", "--id", "TASK-0001"]
    )
    assert "done" in result.output


def test_task_close_updates_results_closure_decision(packet_repo):
    _make_closure_ready(packet_repo)
    runner = CliRunner()
    runner.invoke(
        main, ["--repo", str(packet_repo), "task", "close", "--id", "TASK-0001"]
    )
    packet_dir = packet_repo / "tasks" / "P3-T12-TASK-0001"
    results = (packet_dir / "results.md").read_text(encoding="utf-8")
    assert "- **Decision:** closed" in results
    assert "Closed via grain task close." in results


def test_task_close_unknown_packet_exits_two(packet_repo):
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "close", "--id", "TASK-9999"]
    )
    assert result.exit_code == 2


def test_task_close_missing_id_exits_two(packet_repo):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(packet_repo), "task", "close"])
    assert result.exit_code == 2


def test_task_close_not_in_review_exits_three(tmp_path):
    repo = _setup_subprocess_repo(tmp_path)
    _run_forge("--repo", str(repo), "task", "create", "--phase", "3", "--task-num", "12")
    packet_dir = repo / "tasks" / "P3-T12-TASK-0001"
    (packet_dir / "results.md").write_text(_APPROVED_RESULTS)
    # Status is still 'draft' — closure should fail
    result = _run_forge("--repo", str(repo), "task", "close", "--id", "TASK-0001")
    assert result.returncode == 3


def test_task_close_missing_results_md_exits_three(tmp_path):
    repo = _setup_subprocess_repo(tmp_path)
    _run_forge("--repo", str(repo), "task", "create", "--phase", "3", "--task-num", "12")
    # Advance to review without adding results.md
    for status in ("ready", "in_progress", "review"):
        _run_forge("--repo", str(repo), "task", "status",
                 "--id", "TASK-0001", "--status", status)
    result = _run_forge("--repo", str(repo), "task", "close", "--id", "TASK-0001")
    assert result.returncode == 3


def test_task_close_pending_verification_exits_three(packet_repo):
    _make_closure_ready(packet_repo)
    packet_dir = packet_repo / "tasks" / "P3-T12-TASK-0001"
    (packet_dir / "results.md").write_text(
        _APPROVED_RESULTS.replace("- **State:** not_run", "- **State:** pending"),
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "close", "--id", "TASK-0001"]
    )
    assert result.exit_code != 0
    assert "verification state is 'pending'" in result.output


def test_task_close_failed_verification_exits_three(packet_repo):
    _make_closure_ready(packet_repo)
    packet_dir = packet_repo / "tasks" / "P3-T12-TASK-0001"
    (packet_dir / "results.md").write_text(
        _APPROVED_RESULTS.replace("- **State:** not_run", "- **State:** failed"),
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "close", "--id", "TASK-0001"]
    )
    assert result.exit_code != 0
    assert "verification state is 'failed'" in result.output


def test_task_close_quick_exits_zero(packet_repo):
    runner = CliRunner()
    runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "create", "--phase", "3", "--task-num", "12"],
    )
    result = runner.invoke(
        main,
        [
            "--repo", str(packet_repo),
            "task", "close",
            "--id", "TASK-0001",
            "--quick",
            "--summary", "Implemented the feature",
        ],
    )
    assert result.exit_code == 0, result.output


def test_task_close_quick_sets_status_done(packet_repo):
    runner = CliRunner()
    runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "create", "--phase", "3", "--task-num", "12"],
    )
    runner.invoke(
        main,
        [
            "--repo", str(packet_repo),
            "task", "close",
            "--id", "TASK-0001",
            "--quick",
            "--summary", "Feature done",
        ],
    )
    from grain.domain.packets import parse_task_metadata
    packet_dir = packet_repo / "tasks" / "P3-T12-TASK-0001"
    metadata = parse_task_metadata(packet_dir / "task.md")
    assert metadata["status"] == "done"


def test_task_close_quick_writes_results_md(packet_repo):
    runner = CliRunner()
    runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "create", "--phase", "3", "--task-num", "12"],
    )
    runner.invoke(
        main,
        [
            "--repo", str(packet_repo),
            "task", "close",
            "--id", "TASK-0001",
            "--quick",
            "--summary", "All done",
            "--files", "src/foo.py",
            "--files", "src/bar.py",
        ],
    )
    packet_dir = packet_repo / "tasks" / "P3-T12-TASK-0001"
    results = (packet_dir / "results.md").read_text(encoding="utf-8")
    assert "All done" in results
    assert "src/foo.py" in results
    assert "src/bar.py" in results


def test_task_close_quick_requires_summary(packet_repo):
    runner = CliRunner()
    runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "create", "--phase", "3", "--task-num", "12"],
    )
    result = runner.invoke(
        main,
        [
            "--repo", str(packet_repo),
            "task", "close",
            "--id", "TASK-0001",
            "--quick",
        ],
    )
    assert result.exit_code != 0
    assert "summary" in result.output.lower() or "summary" in str(result.exception).lower()


def test_task_close_idempotent_fail_after_done(tmp_path):
    # Once done, trying to close again should fail (done->done not in transition map)
    repo = _setup_subprocess_repo(tmp_path)
    _run_forge("--repo", str(repo), "task", "create", "--phase", "3", "--task-num", "12")
    packet_dir = repo / "tasks" / "P3-T12-TASK-0001"
    (packet_dir / "results.md").write_text(_APPROVED_RESULTS)
    for status in ("ready", "in_progress", "review"):
        _run_forge("--repo", str(repo), "task", "status",
                 "--id", "TASK-0001", "--status", status)
    _run_forge("--repo", str(repo), "task", "close", "--id", "TASK-0001")
    # Second close attempt: status is now 'done', not 'review'
    result = _run_forge("--repo", str(repo), "task", "close", "--id", "TASK-0001")
    assert result.returncode == 3
