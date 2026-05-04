from click.testing import CliRunner

from grain.cli import main
from grain.tui.app import (
    BacklogTaskSnapshot,
    CandidateTaskSnapshot,
    GrainShellSnapshot,
    PacketArtifactSnapshot,
    build_shell_snapshot,
    _render_backlog_panel,
    _render_packet_panel,
    _render_prompt_panel,
    _render_queue_panel,
    _render_status_panel,
    _render_task_panel,
)


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
        (
            "## 24. Phase 22 — TUI Foundation and Workflow Surfaces\n\n"
            "### P22-T02 — Workflow dashboard and status summary\n"
            "- **Status:** ready\n\n"
            "### P22-T03 — Backlog, task, and packet inspector views\n"
            "- **Status:** draft\n"
        ),
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
    _write(
        tmp_path / "prompts" / "task.execute.md",
        "# Execute\n\nMetadata:\n- scope: task\n- stage: execute\n- recommended_model_class: open_model\n",
    )

    snapshot = build_shell_snapshot(tmp_path)

    assert snapshot.active_phase == "22"
    assert snapshot.active_task_id == "none"
    assert snapshot.current_task_status == "unset"
    assert snapshot.next_action == ""
    assert snapshot.recommended_prompt == "prompts/task.execute.md"
    assert snapshot.prompt_stage == "execute"
    assert snapshot.prompt_scope == "task"
    assert snapshot.model_class == "open_model"
    assert snapshot.stop_reason == "previous_phase_not_closed"
    assert snapshot.blocking_reason_count == 1
    assert snapshot.backlog_tasks[0].task_ref == "P22-T02"
    assert snapshot.backlog_tasks[1].task_ref == "P22-T03"
    assert snapshot.packet_artifacts is None


def test_render_panels_surface_blocked_state():
    snapshot = GrainShellSnapshot(
        repo_root="/repo",
        active_phase="22",
        active_task_id="none",
        current_task_path="none",
        current_task_status="unset",
        next_action="",
        recommended_prompt="prompts/task.execute.md",
        prompt_stage="execute",
        prompt_scope="task",
        model_class="open_model",
        stop_reason="previous_phase_not_closed",
        blocking_reason_count=1,
        blocking_reasons=["Phase 21 was not sealed"],
        candidate_tasks=[],
    )

    assert "Workflow Status" in _render_status_panel(snapshot)
    assert "previous_phase_not_closed" in _render_status_panel(snapshot)
    assert "Current Task Pointer" in _render_task_panel(snapshot)
    assert "Prompt Status" in _render_prompt_panel(snapshot)
    queue = _render_queue_panel(snapshot)
    assert "Workflow Blockers" in queue
    assert "Phase 21 was not sealed" in queue


def test_render_queue_panel_surfaces_candidate_tasks_when_not_blocked():
    snapshot = GrainShellSnapshot(
        repo_root="/repo",
        active_phase="22",
        active_task_id="none",
        current_task_path="none",
        current_task_status="idle",
        next_action="task_execute",
        recommended_prompt="prompts/task.execute.md",
        prompt_stage="execute",
        prompt_scope="task",
        model_class="open_model",
        stop_reason="",
        blocking_reason_count=0,
        blocking_reasons=[],
        candidate_tasks=[
            CandidateTaskSnapshot("P22-T02", "ready", "backlog"),
            CandidateTaskSnapshot("P22-T03", "draft", "backlog"),
        ],
    )
    queue = _render_queue_panel(snapshot)
    assert "Candidate Tasks" in queue
    assert "P22-T02 [ready] via backlog" in queue


def test_render_backlog_and_packet_panels_surface_inspector_content():
    snapshot = GrainShellSnapshot(
        repo_root="/repo",
        active_phase="22",
        active_task_id="TASK-0148",
        current_task_path="tasks/P22-T03-TASK-0148/",
        current_task_status="in_progress",
        next_action="task_execute",
        recommended_prompt="prompts/task.execute.md",
        prompt_stage="execute",
        prompt_scope="task",
        model_class="open_model",
        stop_reason="",
        blocking_reason_count=0,
        blocking_reasons=[],
        candidate_tasks=[],
        backlog_tasks=[
            BacklogTaskSnapshot("P22-T03", "Backlog, task, and packet inspector views", "in_progress"),
            BacklogTaskSnapshot("P22-T04", "Action launcher wiring for execute/review/close flows", "draft"),
        ],
        packet_artifacts=PacketArtifactSnapshot(
            packet_dir="tasks/P22-T03-TASK-0148/",
            packet_status="in_progress",
            files_present=["task.md", "context.md", "plan.md"],
            files_missing=["results.md", "handoff.md"],
        ),
    )

    backlog = _render_backlog_panel(snapshot)
    packet = _render_packet_panel(snapshot)
    assert "Phase Backlog" in backlog
    assert "P22-T03 [in_progress]" in backlog
    assert "Packet Inspector" in packet
    assert "packet_dir: tasks/P22-T03-TASK-0148/" in packet
    assert "missing: results.md, handoff.md" in packet
