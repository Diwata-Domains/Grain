from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from grain.domain.packets import parse_task_metadata
from grain.services.prompt_service import show_prompt
from grain.services.workflow_service import evaluate_workflow_state

_TASK_HEADING = re.compile(r"^###\s+(P(\d+)-T(\d+))\s+—\s+(.+)$")
_PHASE_HEADING = re.compile(r"^##\s+\d+\.\s+Phase\s+(\d+)\s+—")
_BACKLOG_STATUS = re.compile(r"^- \*\*Status:\*\*\s*(\S+)")


@dataclass(frozen=True)
class CandidateTaskSnapshot:
    task_ref: str
    status: str
    source: str


@dataclass(frozen=True)
class BacklogTaskSnapshot:
    task_ref: str
    title: str
    status: str


@dataclass(frozen=True)
class PacketArtifactSnapshot:
    packet_dir: str
    packet_status: str
    files_present: list[str] = field(default_factory=list)
    files_missing: list[str] = field(default_factory=list)


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
    backlog_tasks: list[BacklogTaskSnapshot] = field(default_factory=list)
    packet_artifacts: PacketArtifactSnapshot | None = None


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


def _read_phase_backlog_tasks(root: Path, active_phase: str) -> list[BacklogTaskSnapshot]:
    backlog = root / "docs" / "working" / "backlog.md"
    if not backlog.exists() or not active_phase or active_phase == "unknown":
        return []

    tasks: list[BacklogTaskSnapshot] = []
    in_phase = False
    current_ref = ""
    current_title = ""

    for line in backlog.read_text(encoding="utf-8").splitlines():
        phase_match = _PHASE_HEADING.match(line)
        if phase_match:
            in_phase = phase_match.group(1) == active_phase
            current_ref = ""
            current_title = ""
            continue

        if not in_phase:
            continue

        heading_match = _TASK_HEADING.match(line)
        if heading_match:
            current_ref = heading_match.group(1)
            current_title = heading_match.group(4).strip()
            continue

        if current_ref:
            status_match = _BACKLOG_STATUS.match(line)
            if status_match:
                tasks.append(
                    BacklogTaskSnapshot(
                        task_ref=current_ref,
                        title=current_title,
                        status=status_match.group(1),
                    )
                )
                current_ref = ""
                current_title = ""

    return tasks


def _inspect_packet(root: Path, task_path: str) -> PacketArtifactSnapshot | None:
    if not task_path or task_path == "none":
        return None

    packet_dir = root / task_path.rstrip("/")
    if not packet_dir.exists() or not packet_dir.is_dir():
        return PacketArtifactSnapshot(
            packet_dir=task_path,
            packet_status="missing",
            files_present=[],
            files_missing=["task.md"],
        )

    expected = ["task.md", "context.md", "plan.md", "deliverable_spec.md", "results.md", "handoff.md"]
    files_present = [name for name in expected if (packet_dir / name).exists()]
    files_missing = [name for name in expected if not (packet_dir / name).exists()]
    status = parse_task_metadata(packet_dir / "task.md").get("status", "") if (packet_dir / "task.md").exists() else "missing"
    return PacketArtifactSnapshot(
        packet_dir=task_path,
        packet_status=status or "unknown",
        files_present=files_present,
        files_missing=files_missing,
    )


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

    active_phase = evaluation.active_phase or "unknown"
    return GrainShellSnapshot(
        repo_root=str(root),
        active_phase=active_phase,
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
        backlog_tasks=_read_phase_backlog_tasks(root, active_phase),
        packet_artifacts=_inspect_packet(root, task_path),
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


def _render_backlog_panel(snapshot: GrainShellSnapshot) -> str:
    if not snapshot.backlog_tasks:
        return "\n".join(
            [
                "Phase Backlog",
                "- no tasks parsed for the active phase",
            ]
        )

    lines = ["Phase Backlog"]
    lines.extend(
        f"- {task.task_ref} [{task.status}] {task.title}"
        for task in snapshot.backlog_tasks[:6]
    )
    return "\n".join(lines)


def _render_packet_panel(snapshot: GrainShellSnapshot) -> str:
    packet = snapshot.packet_artifacts
    if packet is None:
        return "\n".join(
            [
                "Packet Inspector",
                "- no active packet pointer",
            ]
        )

    lines = [
        "Packet Inspector",
        f"packet_dir: {packet.packet_dir}",
        f"packet_status: {packet.packet_status or 'unknown'}",
    ]
    if packet.files_present:
        lines.append("present: " + ", ".join(packet.files_present))
    if packet.files_missing:
        lines.append("missing: " + ", ".join(packet.files_missing))
    return "\n".join(lines)


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

        #left-column {
            width: 3fr;
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
                    with Container(id="left-column", classes="stack"):
                        yield Static(
                            _render_status_panel(snapshot),
                            id="summary",
                            classes="panel",
                        )
                        yield Static(_render_backlog_panel(snapshot), classes="panel")
                    with Container(id="right-column", classes="stack"):
                        yield Static(_render_task_panel(snapshot), classes="panel")
                        yield Static(_render_packet_panel(snapshot), classes="panel")
                        yield Static(_render_prompt_panel(snapshot), classes="panel")
                        yield Static(_render_queue_panel(snapshot), classes="panel")
            yield Footer()

    return GrainApp()


def launch_tui(root: Path) -> None:
    app = create_app(root)
    app.run()
