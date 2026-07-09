# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Tests for `grain task start` and the transition-hint error on `task status`.

`task start` performs the full legal path to in_progress and syncs backlog.md
and current_task.md so reconcile reports no drift. The illegal-transition error
on `task status` must name the legal next state.
"""

from click.testing import CliRunner

from grain.cli import main
from grain.domain.packets import parse_task_metadata
from grain.services import task_service

_BACKLOG = """# Backlog

## Phase 1 — Foundation

### P1-T01 — First task
- **Status:** draft
- **Summary:** Do the first thing.
"""

_CURRENT_TASK = "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: idle\n"


def _seed_working_docs(packet_repo):
    working = packet_repo / "docs" / "working"
    working.mkdir(parents=True, exist_ok=True)
    (working / "backlog.md").write_text(_BACKLOG, encoding="utf-8")
    (working / "current_task.md").write_text(_CURRENT_TASK, encoding="utf-8")


def _create_packet(packet_repo, phase=1, task_num=1, title="First task"):
    runner = CliRunner()
    runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "create",
         "--phase", str(phase), "--task-num", str(task_num), "--title", title],
    )


# ── illegal transition hint ──────────────────────────────────────────────────

def test_status_illegal_transition_names_legal_next(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "status",
         "--id", "TASK-0001", "--status", "in_progress"],
    )
    assert result.exit_code != 0
    # The hint travels on the domain exception's detail (rendered by cli()).
    detail = getattr(result.exception, "detail", "") or ""
    combined = result.output + detail
    assert "ready" in combined
    assert "legal next state" in combined


def test_status_illegal_transition_hint_at_service_level(packet_repo):
    _create_packet(packet_repo)
    result = task_service.update_packet_status(packet_repo, "TASK-0001", "in_progress")
    assert not result.ok
    joined = "; ".join(result.errors)
    assert "legal next state(s) from 'draft': ready" in joined


# ── task start: status transition ────────────────────────────────────────────

def test_start_moves_draft_to_in_progress(packet_repo):
    _seed_working_docs(packet_repo)
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "start", "TASK-0001"]
    )
    assert result.exit_code == 0, result.output
    packet_dir = packet_repo / "tasks" / "P1-T01-TASK-0001"
    assert parse_task_metadata(packet_dir / "task.md")["status"] == "in_progress"


def test_start_accepts_packet_dir_name(packet_repo):
    _seed_working_docs(packet_repo)
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "start", "P1-T01-TASK-0001"]
    )
    assert result.exit_code == 0, result.output


def test_start_from_ready(packet_repo):
    _seed_working_docs(packet_repo)
    _create_packet(packet_repo)
    result = task_service.update_packet_status(packet_repo, "TASK-0001", "ready")
    assert result.ok
    started = task_service.start_task(packet_repo, "TASK-0001")
    assert started.ok
    assert started.status == "in_progress"


def test_start_already_in_progress_is_noop_ok(packet_repo):
    _seed_working_docs(packet_repo)
    _create_packet(packet_repo)
    task_service.start_task(packet_repo, "TASK-0001")
    again = task_service.start_task(packet_repo, "TASK-0001")
    assert again.ok
    assert again.status == "in_progress"


# ── task start: doc sync ──────────────────────────────────────────────────────

def test_start_syncs_backlog_status(packet_repo):
    _seed_working_docs(packet_repo)
    _create_packet(packet_repo)
    task_service.start_task(packet_repo, "TASK-0001")
    backlog = (packet_repo / "docs" / "working" / "backlog.md").read_text(encoding="utf-8")
    assert "- **Status:** in_progress" in backlog
    assert "- **Status:** draft" not in backlog


def test_start_syncs_current_task_pointer(packet_repo):
    _seed_working_docs(packet_repo)
    _create_packet(packet_repo)
    task_service.start_task(packet_repo, "TASK-0001")
    current = (packet_repo / "docs" / "working" / "current_task.md").read_text(encoding="utf-8")
    assert "Task ID: TASK-0001" in current
    assert "Task Path: tasks/P1-T01-TASK-0001/" in current
    assert "Status: in_progress" in current


def test_start_leaves_reconcile_clean(packet_repo):
    from grain.services.reconcile_service import reconcile

    _seed_working_docs(packet_repo)
    _create_packet(packet_repo)
    task_service.start_task(packet_repo, "TASK-0001")
    result = reconcile(packet_repo)
    mismatches = [i for i in result.issues if i.check == "packet_backlog_mismatch"]
    assert mismatches == [], [i.description for i in result.issues]
    assert result.ok


# ── task start: errors ────────────────────────────────────────────────────────

def test_start_unknown_packet_exits_two(packet_repo):
    _seed_working_docs(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "start", "TASK-9999"]
    )
    assert result.exit_code == 2


def test_start_done_packet_rejected(packet_repo):
    _seed_working_docs(packet_repo)
    _create_packet(packet_repo)
    packet_dir = packet_repo / "tasks" / "P1-T01-TASK-0001"
    from grain.domain.packets import write_packet_status
    write_packet_status(packet_dir, "done")
    result = task_service.start_task(packet_repo, "TASK-0001")
    assert not result.ok
    assert any("done" in e for e in result.errors)


def test_start_no_selector_errors(packet_repo):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(packet_repo), "task", "start"])
    assert result.exit_code == 2
