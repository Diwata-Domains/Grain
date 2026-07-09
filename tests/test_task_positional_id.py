# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Tests for positional packet-id resolution across the `grain task` group.

The packet directory name printed by `grain task list` (e.g. P1-T01-TASK-0001)
must be accepted directly, as must a bare TASK-#### id, on the show / validate /
status / prepare / close subcommands — not only via --id.
"""

from click.testing import CliRunner

from grain.cli import main
from grain.services.task_service import resolve_task_identifier


def _create_packet(packet_repo, phase=1, task_num=1, title="Test Task"):
    runner = CliRunner()
    runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "create",
         "--phase", str(phase), "--task-num", str(task_num), "--title", title],
    )


# ── resolve_task_identifier unit behavior ────────────────────────────────────

def test_resolve_bare_id():
    assert resolve_task_identifier("TASK-0001", None) == "TASK-0001"


def test_resolve_packet_dir_name():
    assert resolve_task_identifier("P1-T01-TASK-0001", None) == "TASK-0001"


def test_resolve_option_only():
    assert resolve_task_identifier(None, "TASK-0007") == "TASK-0007"


def test_resolve_neither_returns_none():
    assert resolve_task_identifier(None, None) is None


def test_resolve_matching_positional_and_option():
    assert resolve_task_identifier("P1-T01-TASK-0001", "TASK-0001") == "TASK-0001"


def test_resolve_disagreement_raises():
    import pytest

    with pytest.raises(ValueError):
        resolve_task_identifier("P1-T01-TASK-0001", "TASK-0002")


# ── task show ────────────────────────────────────────────────────────────────

def test_show_accepts_packet_dir_name(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "show", "P1-T01-TASK-0001"]
    )
    assert result.exit_code == 0, result.output
    assert "TASK-0001" in result.output


def test_show_accepts_bare_id_positional(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "show", "TASK-0001"]
    )
    assert result.exit_code == 0, result.output


def test_show_id_flag_still_works(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "show", "--id", "TASK-0001"]
    )
    assert result.exit_code == 0, result.output


def test_show_no_selector_errors(packet_repo):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(packet_repo), "task", "show"])
    assert result.exit_code == 2


def test_show_disagreeing_selectors_error(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "show",
         "P1-T01-TASK-0001", "--id", "TASK-0002"],
    )
    assert result.exit_code == 2
    assert "different tasks" in result.output


# ── task validate ────────────────────────────────────────────────────────────

def test_validate_accepts_packet_dir_name(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "validate", "P1-T01-TASK-0001"]
    )
    assert result.exit_code == 0, result.output


def test_validate_no_args_still_validates_all(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(packet_repo), "task", "validate"])
    assert result.exit_code == 0, result.output


def test_validate_positional_and_all_conflict(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "validate", "TASK-0001", "--all"],
    )
    assert result.exit_code == 2


# ── task status ──────────────────────────────────────────────────────────────

def test_status_accepts_packet_dir_name(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "status",
         "P1-T01-TASK-0001", "--status", "ready"],
    )
    assert result.exit_code == 0, result.output


# ── task prepare ─────────────────────────────────────────────────────────────

def test_prepare_accepts_packet_dir_name(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(packet_repo), "task", "prepare", "P1-T01-TASK-0001"]
    )
    # prepare may report missing_inputs, but must resolve the packet (exit 0).
    assert result.exit_code == 0, result.output
    assert "TASK-0001" in result.output


# ── task close ───────────────────────────────────────────────────────────────

def test_close_accepts_packet_dir_name_positional(packet_repo):
    _create_packet(packet_repo)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "task", "close",
         "P1-T01-TASK-0001", "--quick", "--summary", "done"],
    )
    assert result.exit_code == 0, result.output
    assert "done" in result.output
