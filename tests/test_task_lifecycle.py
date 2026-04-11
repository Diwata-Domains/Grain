"""End-to-end lifecycle tests for the task packet system.

Tests full workflow sequences across create/status/validate/close commands.
Focuses on state machine integrity and cross-command integration rather than
individual command behavior (which is covered by dedicated command test files).
"""

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


def _invoke(packet_repo, *args):
    return CliRunner().invoke(main, ["--repo", str(packet_repo), *args])


def _status(packet_repo, task_id, new_status):
    return _invoke(packet_repo, "task", "status", "--id", task_id, "--status", new_status)


def _current_status(packet_repo, dir_name) -> str:
    task_md = packet_repo / "tasks" / dir_name / "task.md"
    return parse_task_metadata(task_md).get("status", "")


# ---------------------------------------------------------------------------
# Happy-path full lifecycle
# ---------------------------------------------------------------------------

def test_full_lifecycle_happy_path(packet_repo):
    """create → ready → in_progress → review → (add results) → close → done"""
    _invoke(packet_repo, "task", "create", "--phase", "3", "--task-num", "13")

    assert _current_status(packet_repo, "P3-T13-TASK-0001") == "draft"

    _status(packet_repo, "TASK-0001", "ready")
    assert _current_status(packet_repo, "P3-T13-TASK-0001") == "ready"

    _status(packet_repo, "TASK-0001", "in_progress")
    assert _current_status(packet_repo, "P3-T13-TASK-0001") == "in_progress"

    _status(packet_repo, "TASK-0001", "review")
    assert _current_status(packet_repo, "P3-T13-TASK-0001") == "review"

    (packet_repo / "tasks" / "P3-T13-TASK-0001" / "results.md").write_text(
        "# Results\n\nAll done.\n"
    )

    result = _invoke(packet_repo, "task", "close", "--id", "TASK-0001")
    assert result.exit_code == 0, result.output
    assert _current_status(packet_repo, "P3-T13-TASK-0001") == "done"


def test_full_lifecycle_list_reflects_done(packet_repo):
    """forge task list shows 'done' after closure."""
    _invoke(packet_repo, "task", "create", "--phase", "3", "--task-num", "13")
    for s in ("ready", "in_progress", "review"):
        _status(packet_repo, "TASK-0001", s)
    (packet_repo / "tasks" / "P3-T13-TASK-0001" / "results.md").write_text("# Results\nDone.\n")
    _invoke(packet_repo, "task", "close", "--id", "TASK-0001")

    result = _invoke(packet_repo, "task", "list")
    assert "done" in result.output


def test_full_lifecycle_show_reflects_status_changes(packet_repo):
    """forge task show tracks each status change through the lifecycle."""
    _invoke(packet_repo, "task", "create", "--phase", "3", "--task-num", "13")

    for expected_status, new_status in [
        ("draft", None),
        ("ready", "ready"),
        ("in_progress", "in_progress"),
        ("review", "review"),
    ]:
        if new_status:
            _status(packet_repo, "TASK-0001", new_status)
        result = _invoke(packet_repo, "task", "show", "--id", "TASK-0001")
        assert expected_status in result.output


# ---------------------------------------------------------------------------
# Blocked and recovered
# ---------------------------------------------------------------------------

def test_lifecycle_blocked_and_recovered(packet_repo):
    """in_progress → blocked → ready → in_progress → review → close"""
    _invoke(packet_repo, "task", "create", "--phase", "3", "--task-num", "13")
    _status(packet_repo, "TASK-0001", "ready")
    _status(packet_repo, "TASK-0001", "in_progress")
    _status(packet_repo, "TASK-0001", "blocked")
    assert _current_status(packet_repo, "P3-T13-TASK-0001") == "blocked"

    _status(packet_repo, "TASK-0001", "ready")
    _status(packet_repo, "TASK-0001", "in_progress")
    _status(packet_repo, "TASK-0001", "review")
    (packet_repo / "tasks" / "P3-T13-TASK-0001" / "results.md").write_text("# Results\nDone.\n")

    result = _invoke(packet_repo, "task", "close", "--id", "TASK-0001")
    assert result.exit_code == 0
    assert _current_status(packet_repo, "P3-T13-TASK-0001") == "done"


# ---------------------------------------------------------------------------
# Review rework
# ---------------------------------------------------------------------------

def test_lifecycle_review_rework(packet_repo):
    """review → in_progress (rework) → review → close"""
    _invoke(packet_repo, "task", "create", "--phase", "3", "--task-num", "13")
    for s in ("ready", "in_progress", "review"):
        _status(packet_repo, "TASK-0001", s)

    # Rework
    _status(packet_repo, "TASK-0001", "in_progress")
    assert _current_status(packet_repo, "P3-T13-TASK-0001") == "in_progress"

    _status(packet_repo, "TASK-0001", "review")
    (packet_repo / "tasks" / "P3-T13-TASK-0001" / "results.md").write_text("# Results\nDone.\n")

    result = _invoke(packet_repo, "task", "close", "--id", "TASK-0001")
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Disallowed transitions
# ---------------------------------------------------------------------------

DISALLOWED_TRANSITIONS = [
    ("draft", "in_progress"),
    ("draft", "blocked"),
    ("draft", "review"),
    ("draft", "done"),
    ("ready", "draft"),
    ("ready", "blocked"),
    ("ready", "review"),
    ("ready", "done"),
    ("blocked", "in_progress"),
    ("blocked", "review"),
    ("blocked", "done"),
    ("review", "ready"),
    ("review", "draft"),
    ("review", "blocked"),
    ("done", "draft"),
    ("done", "ready"),
    ("done", "in_progress"),
    ("done", "blocked"),
    ("done", "review"),
]


def test_disallowed_transitions_exit_five(tmp_path):
    """All disallowed transitions produce exit code 5."""
    repo = _setup_subprocess_repo(tmp_path)

    for from_status, to_status in DISALLOWED_TRANSITIONS:
        # Create a fresh packet for each transition attempt
        _run_forge("--repo", str(repo), "task", "create", "--phase", "3", "--task-num", "13")

        # Find the created packet dir
        task_dirs = sorted((repo / "tasks").iterdir())
        latest = task_dirs[-1]
        task_id_match = __import__("re").search(r"TASK-\d{4}", latest.name)
        task_id = task_id_match.group(0)

        # Advance to from_status via allowed transitions
        _advance_to(repo, task_id, from_status)

        result = _run_forge(
            "--repo", str(repo), "task", "status",
            "--id", task_id, "--status", to_status,
        )
        assert result.returncode == 5, (
            f"Expected exit 5 for {from_status} -> {to_status}, got {result.returncode}"
        )


def _advance_to(repo: Path, task_id: str, target: str) -> None:
    """Advance a packet from draft to target via allowed transitions."""
    routes: dict[str, list[str]] = {
        "draft": [],
        "ready": ["ready"],
        "in_progress": ["ready", "in_progress"],
        "blocked": ["ready", "in_progress", "blocked"],
        "review": ["ready", "in_progress", "review"],
        "done": ["ready", "in_progress", "review"],
    }
    for s in routes.get(target, []):
        _run_forge("--repo", str(repo), "task", "status", "--id", task_id, "--status", s)
    if target == "done":
        # Write results.md and close to reach done state
        import re
        dirs = sorted((repo / "tasks").iterdir())
        for d in dirs:
            m = re.search(r"TASK-\d{4}", d.name)
            if m and m.group(0) == task_id:
                (d / "results.md").write_text("# Results\nDone.\n")
                break
        _run_forge("--repo", str(repo), "task", "close", "--id", task_id)


# ---------------------------------------------------------------------------
# Validate integrates with close
# ---------------------------------------------------------------------------

def test_validate_passes_before_close(packet_repo):
    """validate exits 0 on a closure-ready packet."""
    _invoke(packet_repo, "task", "create", "--phase", "3", "--task-num", "13")
    for s in ("ready", "in_progress", "review"):
        _status(packet_repo, "TASK-0001", s)
    (packet_repo / "tasks" / "P3-T13-TASK-0001" / "results.md").write_text("# Results\nDone.\n")

    result = _invoke(packet_repo, "task", "validate", "--id", "TASK-0001")
    assert result.exit_code == 0


def test_validate_all_after_lifecycle(packet_repo):
    """validate --all passes when all packets are structurally valid."""
    for task_num in (1, 2, 3):
        _invoke(packet_repo, "task", "create", "--phase", "3", "--task-num", str(task_num))

    result = _invoke(packet_repo, "task", "validate", "--all")
    assert result.exit_code == 0


def test_close_without_results_md_fails_validation(packet_repo):
    """close exits non-zero when results.md is absent, even at review status."""
    _invoke(packet_repo, "task", "create", "--phase", "3", "--task-num", "13")
    for s in ("ready", "in_progress", "review"):
        _status(packet_repo, "TASK-0001", s)

    result = _invoke(packet_repo, "task", "close", "--id", "TASK-0001")
    assert result.exit_code != 0


# ---------------------------------------------------------------------------
# Multiple packets
# ---------------------------------------------------------------------------

def test_multiple_packets_independent_lifecycles(packet_repo):
    """Two packets can be in different states simultaneously."""
    _invoke(packet_repo, "task", "create", "--phase", "3", "--task-num", "1")
    _invoke(packet_repo, "task", "create", "--phase", "3", "--task-num", "2")

    _status(packet_repo, "TASK-0001", "ready")
    _status(packet_repo, "TASK-0001", "in_progress")

    # TASK-0001 is in_progress, TASK-0002 is still draft
    assert _current_status(packet_repo, "P3-T01-TASK-0001") == "in_progress"
    assert _current_status(packet_repo, "P3-T02-TASK-0002") == "draft"

    result = _invoke(packet_repo, "task", "list")
    assert "in_progress" in result.output
    assert "draft" in result.output
