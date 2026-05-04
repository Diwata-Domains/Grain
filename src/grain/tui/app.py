from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from grain.services.prompt_service import show_prompt
from grain.services.workflow_service import evaluate_workflow_state


@dataclass(frozen=True)
class CandidateTaskSnapshot:
    task_ref: str
    status: str
    source: str


@dataclass(frozen=True)
class GrainShellSnapshot:
    repo_root: str
    active_phase: str
    active_task_id: str
    current_task_path: str
    current_task_status: str
    next_action: str
    recommended_prompt: str
    prompt_stage: str
    prompt_scope: str
    model_class: str
    stop_reason: str
    blocking_reason_count: int
    blocking_reasons: list[str] = field(default_factory=list)
    candidate_tasks: list[CandidateTaskSnapshot] = field(default_factory=list)


def _read_current_task_pointer(root: Path) -> tuple[str, str, str]:
    current_task = root / "docs" / "working" / "current_task.md"
    if not current_task.exists():
        return "none", "none", "unset"

    task_id = "none"
    task_path = "none"
    status = "unset"
    for line in current_task.read_text(encoding="utf-8").splitlines():
        if line.startswith("Task ID:"):
            task_id = line.split(":", 1)[1].strip() or "none"
        elif line.startswith("Task Path:"):
            task_path = line.split(":", 1)[1].strip() or "none"
        elif line.startswith("Status:"):
            status = line.split(":", 1)[1].strip() or "unset"
    return task_id, task_path, status


def build_shell_snapshot(root: Path) -> GrainShellSnapshot:
    result, evaluation = evaluate_workflow_state(root)
    _, prompt_payload = show_prompt(root)
    task_id, task_path, task_status = _read_current_task_pointer(root)

    if evaluation is None:
        return GrainShellSnapshot(
            repo_root=str(root),
            active_phase="unknown",
            active_task_id=task_id,
            current_task_path=task_path,
            current_task_status=task_status,
            next_action="",
            recommended_prompt="",
            prompt_stage="",
            prompt_scope="",
            model_class="",
            stop_reason="workflow_evaluation_failed",
            blocking_reason_count=len(result.errors),
            blocking_reasons=list(result.errors),
        )

    return GrainShellSnapshot(
        repo_root=str(root),
        active_phase=evaluation.active_phase or "unknown",
        active_task_id=evaluation.active_task_id or task_id,
        current_task_path=task_path,
        current_task_status=task_status,
        next_action=evaluation.next_action,
        recommended_prompt=(prompt_payload or {}).get("recommended_prompt", evaluation.recommended_prompt),
        prompt_stage=(prompt_payload or {}).get("stage", ""),
        prompt_scope=(prompt_payload or {}).get("scope", ""),
        model_class=(prompt_payload or {}).get("model_class", ""),
        stop_reason=evaluation.stop_reason,
        blocking_reason_count=len(evaluation.blocking_reasons),
        blocking_reasons=list(evaluation.blocking_reasons),
        candidate_tasks=[
            CandidateTaskSnapshot(task.task_ref, task.status, task.source)
            for task in evaluation.candidate_tasks
        ],
    )


def _render_status_panel(snapshot: GrainShellSnapshot) -> str:
    return "\n".join(
        [
            "Workflow Status",
            f"repo: {snapshot.repo_root}",
            f"phase: {snapshot.active_phase}",
            f"task: {snapshot.active_task_id}",
            f"current_status: {snapshot.current_task_status}",
            f"next_action: {snapshot.next_action or 'none'}",
            f"stop_reason: {snapshot.stop_reason or 'none'}",
        ]
    )


def _render_task_panel(snapshot: GrainShellSnapshot) -> str:
    return "\n".join(
        [
            "Current Task Pointer",
            f"task_id: {snapshot.active_task_id}",
            f"task_path: {snapshot.current_task_path}",
            f"status: {snapshot.current_task_status}",
            "",
            "This panel reflects docs/working/current_task.md and workflow evaluation.",
        ]
    )


def _render_prompt_panel(snapshot: GrainShellSnapshot) -> str:
    return "\n".join(
        [
            "Prompt Status",
            f"recommended_prompt: {snapshot.recommended_prompt or 'none'}",
            f"scope: {snapshot.prompt_scope or 'none'}",
            f"stage: {snapshot.prompt_stage or 'none'}",
            f"model_class: {snapshot.model_class or 'none'}",
        ]
    )


def _render_queue_panel(snapshot: GrainShellSnapshot) -> str:
    if snapshot.blocking_reasons:
        lines = ["Workflow Blockers"]
        lines.extend(f"- {reason}" for reason in snapshot.blocking_reasons)
        return "\n".join(lines)

    if snapshot.candidate_tasks:
        lines = ["Candidate Tasks"]
        lines.extend(
            f"- {task.task_ref} [{task.status}] via {task.source}"
            for task in snapshot.candidate_tasks[:5]
        )
        return "\n".join(lines)

    return "\n".join(
        [
            "Candidate Tasks",
            "- none surfaced by workflow evaluation",
        ]
    )


def _import_textual():
    try:
        from textual.app import App, ComposeResult
        from textual.containers import Container, Horizontal
        from textual.widgets import Footer, Header, Static
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Textual is not installed. Reinstall Grain with the v0.3.0 TUI dependency surface enabled."
        ) from exc

    return App, ComposeResult, Container, Horizontal, Header, Footer, Static


def create_app(root: Path):
    App, ComposeResult, Container, Horizontal, Header, Footer, Static = _import_textual()
    snapshot = build_shell_snapshot(root)

    class GrainApp(App):
        TITLE = "Grain"
        SUB_TITLE = "TUI foundation"
        CSS = """
        Screen {
            layout: vertical;
        }

        #shell {
            height: 1fr;
            padding: 1 2;
        }

        .panel {
            width: 1fr;
            height: 1fr;
            border: round $accent;
            padding: 1;
        }

        #summary {
            width: 3fr;
        }

        #right-column {
            width: 2fr;
            height: 1fr;
        }

        .stack {
            height: 1fr;
        }
        """

        def compose(self) -> ComposeResult:
            yield Header(show_clock=True)
            with Container(id="shell"):
                with Horizontal():
                    yield Static(
                        _render_status_panel(snapshot),
                        id="summary",
                        classes="panel",
                    )
                    with Container(id="right-column", classes="stack"):
                        yield Static(_render_task_panel(snapshot), classes="panel")
                        yield Static(_render_prompt_panel(snapshot), classes="panel")
                        yield Static(_render_queue_panel(snapshot), classes="panel")
            yield Footer()

    return GrainApp()


def launch_tui(root: Path) -> None:
    app = create_app(root)
    app.run()
