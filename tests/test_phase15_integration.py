"""Integration tests for Phase 15 deliverables.

Covers cross-command state transitions and the full lifecycle gate chain:
  grain workflow run (auto-bootstrap) → task execution → grain phase close
  → workflow evaluator bypass-prevention → grain workflow reconcile --fix

Individual command behavior is covered by unit tests in:
  test_phase_close_cmd.py, test_workflow_reconcile_cmd.py,
  test_workflow_run_cmd.py
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path as _Path
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main


# ── Helpers ────────────────────────────────────────────────────────────────────


def _run(repo: Path, *args: str):
    runner = CliRunner()
    return runner.invoke(main, ["--repo", str(repo), *args])


def _run_json(repo: Path, *args: str):
    runner = CliRunner()
    return runner.invoke(main, ["--repo", str(repo), "--format", "json", *args])


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _seed_templates(repo: Path) -> None:
    """Copy bundled task templates so create_packet_directory works in tmp repos."""
    templates_src = _Path(__file__).resolve().parents[1] / "src" / "grain" / "data" / "templates" / "tasks"
    templates_dst = repo / "templates" / "tasks"
    templates_dst.mkdir(parents=True, exist_ok=True)
    for f in templates_src.iterdir():
        shutil.copy(f, templates_dst / f.name)


def _seed_repo(
    repo: Path,
    phase: str = "15",
    backlog_tasks: dict[str, str] | None = None,
    current_task_id: str = "none",
    current_task_path: str = "none",
    current_task_status: str = "idle",
) -> None:
    _write(
        repo / "docs" / "working" / "current_focus.md",
        f"# Current Focus\n\n## Current Phase\nPhase {phase} — Workflow Hardening\n",
    )
    _write(
        repo / "docs" / "working" / "current_task.md",
        f"# Current Task\n\nTask ID: {current_task_id}\n"
        f"Task Path: {current_task_path}\nStatus: {current_task_status}\n",
    )
    tasks_block = f"## 1. Phase {phase} — Workflow Hardening\n\n"
    for ref, status in (backlog_tasks or {}).items():
        tasks_block += f"### {ref} — Test task\n- **Status:** {status}\n\n"
    _write(repo / "docs" / "working" / "backlog.md", tasks_block)


def _seed_packet(repo: Path, task_ref: str, task_id: str, status: str) -> Path:
    packet_dir = repo / "tasks" / f"{task_ref}-{task_id}"
    packet_dir.mkdir(parents=True)
    _write(
        packet_dir / "task.md",
        f"# Task\n\n## Metadata\n- **ID:** {task_id}\n- **Status:** {status}\n",
    )
    return packet_dir


def _seed_results(packet_dir: Path) -> None:
    _write(packet_dir / "results.md", "# Results\n\nDelivery complete.\n")


# ── Test 1: workflow run auto-bootstraps and activates task ───────────────────


def test_workflow_run_bootstrap_then_close_full_lifecycle(tmp_path: Path):
    """Full lifecycle: workflow run auto-creates packet, task closes, reconcile clean."""
    _seed_templates(tmp_path)
    _seed_repo(tmp_path, backlog_tasks={"P15-T01": "ready"})

    # Step 1: workflow run auto-creates packet for P15-T01
    result = _run(tmp_path, "workflow", "run")
    assert result.exit_code == 0, result.output
    assert "create_and_activate_task" in result.output
    assert "packet_created    true" in result.output

    # Packet was created
    packets = list((tmp_path / "tasks").iterdir())
    assert len(packets) == 1
    packet_dir = packets[0]
    assert "P15-T01" in packet_dir.name

    # current_task.md updated
    current_task = (tmp_path / "docs" / "working" / "current_task.md").read_text(encoding="utf-8")
    assert "Status: in_progress" in current_task

    # Step 2: simulate task completion — write results.md + mark packet done
    _seed_results(packet_dir)
    task_md = packet_dir / "task.md"
    task_md.write_text(
        task_md.read_text(encoding="utf-8").replace("in_progress", "done").replace("draft", "done"),
        encoding="utf-8",
    )

    # Step 3: close task
    task_id = None
    for line in current_task.splitlines():
        if line.startswith("Task ID:"):
            task_id = line.split(":", 1)[1].strip()
    assert task_id and task_id != "none"

    close_result = _run(tmp_path, "task", "close", "--id", task_id, "--quick", "--summary", "done")
    assert close_result.exit_code == 0, close_result.output

    # Step 4: clear current_task, update backlog to done
    _write(
        tmp_path / "docs" / "working" / "current_task.md",
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: idle\n",
    )
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        "## 1. Phase 15 — Workflow Hardening\n\n"
        "### P15-T01 — Test task\n- **Status:** done\n\n",
    )

    # Step 5: reconcile should be clean
    reconcile_result = _run(tmp_path, "workflow", "reconcile")
    assert reconcile_result.exit_code == 0, reconcile_result.output
    assert "issues            0" in reconcile_result.output


# ── Test 2: phase close happy path after all tasks done ───────────────────────


def test_phase_close_after_all_tasks_done(tmp_path: Path):
    """phase close succeeds when all backlog tasks are done and no active task."""
    _seed_repo(
        tmp_path,
        phase="15",
        backlog_tasks={"P15-T01": "done", "P15-T02": "done", "P15-T03": "done"},
    )
    result = _run(tmp_path, "phase", "close")
    assert result.exit_code == 0, result.output
    assert "phase close: ok" in result.output
    assert "tasks_done      3" in result.output

    focus = (tmp_path / "docs" / "working" / "current_focus.md").read_text(encoding="utf-8")
    assert "Phase 15 closed:" in focus
    assert "grain-verified" in focus


# ── Test 3: bypass-prevention — workflow blocked without phase 14 marker ──────


def test_workflow_blocked_when_previous_phase_not_sealed(tmp_path: Path):
    """For phase > 15, workflow evaluator blocks if previous phase not sealed."""
    _seed_repo(
        tmp_path,
        phase="16",
        backlog_tasks={"P16-T01": "ready"},
    )
    # No Phase 15 closed marker in current_focus.md
    result = _run(tmp_path, "workflow", "next")
    assert result.exit_code == 0  # command succeeds but reports stop
    assert "previous_phase_not_closed" in result.output


def test_workflow_unblocked_when_previous_phase_sealed(tmp_path: Path):
    """Workflow evaluator proceeds normally when Phase N-1 marker is present."""
    _write(
        tmp_path / "docs" / "working" / "current_focus.md",
        "# Current Focus\n\n## Current Phase\nPhase 16 — Semantic Enrichment\n\n"
        "Phase 15 closed: 2026-04-17 — 5 tasks done (grain-verified)\n",
    )
    _write(
        tmp_path / "docs" / "working" / "current_task.md",
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: idle\n",
    )
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        "## 1. Phase 16 — Semantic Enrichment\n\n"
        "### P16-T01 — Test task\n- **Status:** ready\n\n",
    )
    result = _run(tmp_path, "workflow", "next")
    assert "previous_phase_not_closed" not in result.output
    assert "packet_required" in result.output


# ── Test 4: reconcile --fix repairs stale state after task close ──────────────


def test_reconcile_fix_repairs_drift_after_task_close(tmp_path: Path):
    """After a task is closed, reconcile --fix syncs backlog and current_task.md."""
    packet_dir = _seed_packet(tmp_path, "P15-T01", "TASK-0103", "done")
    _seed_repo(
        tmp_path,
        backlog_tasks={"P15-T01": "in_progress"},  # backlog is behind
        current_task_id="TASK-0103",
        current_task_path=f"tasks/{packet_dir.name}/",
        current_task_status="in_progress",  # stale pointer
    )

    # First, reconcile without --fix shows errors
    result = _run(tmp_path, "workflow", "reconcile")
    assert result.exit_code == 1
    assert "[error]" in result.output

    # With --fix, both issues are repaired
    result = _run(tmp_path, "workflow", "reconcile", "--fix")
    assert result.exit_code == 0, result.output
    assert "fixed" in result.output

    # Verify repairs
    backlog = (tmp_path / "docs" / "working" / "backlog.md").read_text(encoding="utf-8")
    assert "**Status:** done" in backlog
    current_task = (tmp_path / "docs" / "working" / "current_task.md").read_text(encoding="utf-8")
    assert "Task ID: none" in current_task


# ── Test 5: phase close blocked when active task is in flight ─────────────────


def test_phase_close_blocked_when_active_task(tmp_path: Path):
    """phase close must fail when current_task.md shows an active task."""
    _seed_repo(
        tmp_path,
        phase="15",
        backlog_tasks={"P15-T01": "done"},
        current_task_id="TASK-0103",
        current_task_path="tasks/P15-T01-TASK-0103/",
        current_task_status="in_progress",
    )
    result = _run(tmp_path, "phase", "close")
    assert result.exit_code != 0
    assert "blocked" in result.output or "active task" in result.output.lower()


# ── Test 6: workflow run → JSON contract stable ───────────────────────────────


def test_workflow_run_json_contract_on_auto_bootstrap(tmp_path: Path):
    """JSON output from workflow run contains all required fields when auto-creating."""
    _seed_templates(tmp_path)
    _seed_repo(tmp_path, backlog_tasks={"P15-T01": "ready"})
    result = _run_json(tmp_path, "workflow", "run")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    wf = data.get("workflow_run", {})
    assert wf.get("action_taken") == "create_and_activate_task"
    assert wf.get("packet_created") is True
    assert wf.get("task_activated", "").startswith("TASK-")
    assert wf.get("active_phase") == "15"


# ── Test 7: reconcile --dry-run shows planned repairs without writing ─────────


def test_reconcile_dry_run_previews_without_writing(tmp_path: Path):
    """--dry-run shows what would be fixed but leaves files unchanged."""
    _seed_packet(tmp_path, "P15-T01", "TASK-0103", "done")
    _seed_repo(tmp_path, backlog_tasks={"P15-T01": "ready"})

    result = _run(tmp_path, "workflow", "reconcile", "--dry-run")
    assert "dry-run" in result.output
    assert "fixed" in result.output  # Shows it would fix

    # Backlog unchanged
    backlog = (tmp_path / "docs" / "working" / "backlog.md").read_text(encoding="utf-8")
    assert "**Status:** ready" in backlog


# ── Test 8: phase close JSON output ──────────────────────────────────────────


def test_phase_close_json_contract(tmp_path: Path):
    """JSON output from phase close contains all required fields."""
    _seed_repo(
        tmp_path,
        phase="15",
        backlog_tasks={"P15-T01": "done"},
    )
    result = _run_json(tmp_path, "phase", "close")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data.get("ok") is True
    assert data.get("closed_phase") == "15"
    assert data.get("tasks_done") == 1
    assert data.get("marker_written")  # path written, non-empty
    focus = (tmp_path / "docs" / "working" / "current_focus.md").read_text(encoding="utf-8")
    assert "grain-verified" in focus


# ── Test 9: full Phase 15 gate sequence ───────────────────────────────────────


def test_full_phase15_gate_sequence(tmp_path: Path):
    """
    End-to-end: workflow run → complete tasks → phase close → reconcile clean
    → next phase blocked without marker → unblocked with marker.
    """
    # Phase 15 with two ready tasks
    _seed_templates(tmp_path)
    _seed_repo(tmp_path, phase="15", backlog_tasks={"P15-T01": "ready", "P15-T02": "draft"})

    # Activate T01
    result = _run(tmp_path, "workflow", "run")
    assert result.exit_code == 0

    packet_dir = next((tmp_path / "tasks").iterdir())
    _seed_results(packet_dir)

    # Close T01
    current_task = (tmp_path / "docs" / "working" / "current_task.md").read_text(encoding="utf-8")
    task_id = next(
        line.split(":", 1)[1].strip()
        for line in current_task.splitlines()
        if line.startswith("Task ID:")
    )
    _run(tmp_path, "task", "close", "--id", task_id, "--quick", "--summary", "done")

    # Update docs to done state
    _write(
        tmp_path / "docs" / "working" / "current_task.md",
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: idle\n",
    )
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        "## 1. Phase 15 — Workflow Hardening\n\n"
        "### P15-T01 — Test task\n- **Status:** done\n\n"
        "### P15-T02 — Test task\n- **Status:** done\n\n",
    )

    # Phase close succeeds
    close_result = _run(tmp_path, "phase", "close")
    assert close_result.exit_code == 0, close_result.output

    # Advance to Phase 16
    _write(
        tmp_path / "docs" / "working" / "current_focus.md",
        (tmp_path / "docs" / "working" / "current_focus.md").read_text(encoding="utf-8").replace(
            "Phase 15 — Workflow Hardening", "Phase 16 — Semantic Enrichment"
        ),
    )
    _write(
        tmp_path / "docs" / "working" / "current_task.md",
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: idle\n",
    )
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        "## 1. Phase 16 — Semantic Enrichment\n\n"
        "### P16-T01 — Test task\n- **Status:** ready\n\n",
    )

    # Workflow next for Phase 16 should succeed (Phase 15 marker present)
    next_result = _run(tmp_path, "workflow", "next")
    assert "previous_phase_not_closed" not in next_result.output
    assert "packet_required" in next_result.output

    # Reconcile clean
    reconcile_result = _run(tmp_path, "workflow", "reconcile")
    assert reconcile_result.exit_code == 0
