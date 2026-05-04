from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from grain.services.workflow_service import evaluate_workflow_state


@dataclass(frozen=True)
class GrainShellSnapshot:
    repo_root: str
    active_phase: str
    active_task_id: str
    next_action: str
    recommended_prompt: str
    stop_reason: str
    blocking_reason_count: int


def build_shell_snapshot(root: Path) -> GrainShellSnapshot:
    result, evaluation = evaluate_workflow_state(root)

    if evaluation is None:
        return GrainShellSnapshot(
            repo_root=str(root),
            active_phase="unknown",
            active_task_id="none",
            next_action="",
            recommended_prompt="",
            stop_reason="workflow_evaluation_failed",
            blocking_reason_count=len(result.errors),
        )

    return GrainShellSnapshot(
        repo_root=str(root),
        active_phase=evaluation.active_phase or "unknown",
        active_task_id=evaluation.active_task_id or "none",
        next_action=evaluation.next_action,
        recommended_prompt=evaluation.recommended_prompt,
        stop_reason=evaluation.stop_reason,
        blocking_reason_count=len(evaluation.blocking_reasons),
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
            width: 2fr;
        }
        """

        def compose(self) -> ComposeResult:
            yield Header(show_clock=True)
            with Container(id="shell"):
                with Horizontal():
                    yield Static(
                        "\n".join(
                            [
                                "Workflow Summary",
                                f"repo: {snapshot.repo_root}",
                                f"phase: {snapshot.active_phase}",
                                f"task: {snapshot.active_task_id}",
                                f"next: {snapshot.next_action or 'none'}",
                                f"prompt: {snapshot.recommended_prompt or 'none'}",
                                f"stop: {snapshot.stop_reason or 'none'}",
                                f"blockers: {snapshot.blocking_reason_count}",
                            ]
                        ),
                        id="summary",
                        classes="panel",
                    )
                    yield Static(
                        "\n".join(
                            [
                                "Views Seeded",
                                "- workflow dashboard",
                                "- backlog and packet inspector",
                                "- prompt and context preview",
                                "",
                                "Phase 22 later tasks will replace these placeholders.",
                            ]
                        ),
                        classes="panel",
                    )
            yield Footer()

    return GrainApp()


def launch_tui(root: Path) -> None:
    app = create_app(root)
    app.run()
