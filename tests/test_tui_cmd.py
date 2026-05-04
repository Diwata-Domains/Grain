from click.testing import CliRunner

from grain.cli import main
from grain.tui.app import build_shell_snapshot


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _base_repo(repo):
    _write(repo / "docs" / "runtime" / "PROJECT_RULES.md", "")
    _write(
        repo / "docs" / "working" / "current_focus.md",
        "# Current Focus\n\n## Current Phase\nPhase 22 — TUI Foundation and Workflow Surfaces\n",
    )
    _write(
        repo / "docs" / "working" / "current_task.md",
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: unset\n",
    )
    _write(
        repo / "docs" / "working" / "backlog.md",
        "## 24. Phase 22 — TUI Foundation and Workflow Surfaces\n\n### P22-T02 — Workflow dashboard and status summary\n- **Status:** ready\n",
    )


def test_tui_command_help_lists_shell_entrypoint():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0, result.output
    assert "tui" in result.output


def test_tui_command_launches_shell_with_repo_root(tmp_path, monkeypatch):
    _base_repo(tmp_path)
    captured = {}

    def fake_launch(root):
        captured["root"] = str(root)

    monkeypatch.setattr("grain.cli.tui.launch_tui", fake_launch)

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "tui"])
    assert result.exit_code == 0, result.output
    assert captured["root"] == str(tmp_path.resolve())


def test_tui_command_surfaces_missing_textual_as_click_error(tmp_path, monkeypatch):
    _base_repo(tmp_path)

    def fake_launch(_root):
        raise RuntimeError("Textual is not installed.")

    monkeypatch.setattr("grain.cli.tui.launch_tui", fake_launch)

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "tui"])
    assert result.exit_code == 1
    assert "Textual is not installed." in result.output


def test_build_shell_snapshot_reads_workflow_state(tmp_path):
    _base_repo(tmp_path)

    snapshot = build_shell_snapshot(tmp_path)

    assert snapshot.active_phase == "22"
    assert snapshot.active_task_id == "none"
    assert snapshot.next_action == ""
    assert snapshot.recommended_prompt == ""
    assert snapshot.stop_reason == "previous_phase_not_closed"
    assert snapshot.blocking_reason_count == 1
