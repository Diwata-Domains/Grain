# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from grain.domain.packets import parse_task_metadata
from grain.services import task_service
from grain.services.context_service import build_context_bundle, build_source_metadata
from grain.services.handoff_service import materialize_handoff_artifact
from grain.services.prompt_service import show_prompt
from grain.services.task_observability_service import read_task_observability
from grain.services.workflow_service import evaluate_workflow_state
from grain.services.workflow_run_service import run_workflow_step

_TASK_HEADING = re.compile(r"^###\s+(P(\d+)-T(\d+))\s+—\s+(.+)$")
_PHASE_HEADING = re.compile(r"^##\s+(?:\d+\.\s+)?Phase\s+(\d+)\s+—")
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
    results_summary: str = ""
    files_present: list[str] = field(default_factory=list)
    files_missing: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ActionLaunchResult:
    action_id: str
    ok: bool
    summary: str
    detail: str = ""
    snapshot: "GrainShellSnapshot | None" = None


@dataclass(frozen=True)
class ContextPreviewSnapshot:
    source_count: int
    packet_source_count: int
    canonical_doc_count: int
    working_doc_count: int
    primary_adapter: str
    estimated_tokens: int = 0
    token_warning: bool = False
    top_sources: list[str] = field(default_factory=list)
    trim_hints: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ObservabilityPreviewSnapshot:
    executor_identity: str
    model_class: str
    last_stage: str
    last_workflow_action: str
    updated_at: str


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
    prompt_preview_lines: list[str] = field(default_factory=list)
    stop_reason: str = ""
    blocking_reason_count: int = 0
    blocking_reasons: list[str] = field(default_factory=list)
    affected_artifacts: list[str] = field(default_factory=list)
    candidate_tasks: list[CandidateTaskSnapshot] = field(default_factory=list)
    backlog_tasks: list[BacklogTaskSnapshot] = field(default_factory=list)
    packet_artifacts: PacketArtifactSnapshot | None = None
    context_preview: ContextPreviewSnapshot | None = None
    observability_preview: ObservabilityPreviewSnapshot | None = None
    last_action_summary: str = ""


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
    results_summary = _read_results_summary(packet_dir / "results.md")
    return PacketArtifactSnapshot(
        packet_dir=task_path,
        packet_status=status or "unknown",
        results_summary=results_summary,
        files_present=files_present,
        files_missing=files_missing,
    )


def _read_prompt_preview(root: Path, recommended_prompt: str) -> list[str]:
    if not recommended_prompt:
        return []
    prompt_path = root / recommended_prompt
    if not prompt_path.exists():
        return []

    preview: list[str] = []
    for line in prompt_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        preview.append(stripped)
        if len(preview) >= 5:
            break
    return preview


def _build_context_preview(root: Path, task_id: str) -> ContextPreviewSnapshot | None:
    if not task_id or task_id == "none":
        return None

    result, bundle = build_context_bundle(root, task_id)
    if not result.ok or bundle is None:
        return None

    source_metadata = build_source_metadata(root, bundle)
    stats = bundle.export_metadata.get("context_stats", {})
    adapter_context = bundle.export_metadata.get("adapter_context", {})
    budget = bundle.export_metadata.get("context_budget", {})
    return ContextPreviewSnapshot(
        source_count=len(source_metadata),
        packet_source_count=int(stats.get("packet_sources", 0)),
        canonical_doc_count=int(stats.get("canonical_sources", 0)),
        working_doc_count=int(stats.get("working_sources", 0)),
        primary_adapter=str(adapter_context.get("primary_adapter", "none")),
        estimated_tokens=int(budget.get("estimated_tokens", 0)),
        token_warning=bool(budget.get("warning_active", False)),
        top_sources=[entry["path"] for entry in source_metadata[:5]],
        trim_hints=[
            f"{item['path']} ({item['estimated_tokens']} tokens)"
            for item in budget.get("trim_hints", [])[:3]
        ],
    )


def _build_observability_preview(root: Path, task_id: str) -> ObservabilityPreviewSnapshot | None:
    if not task_id or task_id == "none":
        return None
    record, _ = read_task_observability(root, task_id)
    if record is None:
        return None
    if not any(
        (
            record.executor_identity,
            record.model_class,
            record.last_stage,
            record.last_workflow_action,
            record.updated_at,
        )
    ):
        return None
    return ObservabilityPreviewSnapshot(
        executor_identity=record.executor_identity,
        model_class=record.model_class,
        last_stage=record.last_stage,
        last_workflow_action=record.last_workflow_action,
        updated_at=record.updated_at,
    )


def build_shell_snapshot(root: Path) -> GrainShellSnapshot:
    result, evaluation = evaluate_workflow_state(root)
    _, prompt_payload = show_prompt(root)
    task_id, task_path, task_status = _read_current_task_pointer(root)
    recommended_prompt = (prompt_payload or {}).get("recommended_prompt", "")

    if evaluation is None:
        return GrainShellSnapshot(
            repo_root=str(root),
            active_phase="unknown",
            active_task_id=task_id,
            current_task_path=task_path,
            current_task_status=task_status,
            next_action="",
            recommended_prompt=recommended_prompt,
            prompt_stage="",
            prompt_scope="",
            model_class="",
            prompt_preview_lines=_read_prompt_preview(root, recommended_prompt),
            stop_reason="workflow_evaluation_failed",
            blocking_reason_count=len(result.errors),
            blocking_reasons=list(result.errors),
            affected_artifacts=[],
            context_preview=_build_context_preview(root, task_id),
            observability_preview=_build_observability_preview(root, task_id),
        )

    active_phase = evaluation.active_phase or "unknown"
    recommended_prompt = (prompt_payload or {}).get("recommended_prompt", evaluation.recommended_prompt)
    return GrainShellSnapshot(
        repo_root=str(root),
        active_phase=active_phase,
        active_task_id=evaluation.active_task_id or task_id,
        current_task_path=task_path,
        current_task_status=task_status,
        next_action=evaluation.next_action,
        recommended_prompt=recommended_prompt,
        prompt_stage=(prompt_payload or {}).get("stage", ""),
        prompt_scope=(prompt_payload or {}).get("scope", ""),
        model_class=(prompt_payload or {}).get("model_class", ""),
        prompt_preview_lines=_read_prompt_preview(root, recommended_prompt),
        stop_reason=evaluation.stop_reason,
        blocking_reason_count=len(evaluation.blocking_reasons),
        blocking_reasons=list(evaluation.blocking_reasons),
        affected_artifacts=list(evaluation.affected_artifacts),
        candidate_tasks=[
            CandidateTaskSnapshot(task.task_ref, task.status, task.source)
            for task in evaluation.candidate_tasks
        ],
        backlog_tasks=_read_phase_backlog_tasks(root, active_phase),
        packet_artifacts=_inspect_packet(root, task_path),
        context_preview=_build_context_preview(root, evaluation.active_task_id or task_id),
        observability_preview=_build_observability_preview(root, evaluation.active_task_id or task_id),
    )


def launch_execute_flow(root: Path) -> ActionLaunchResult:
    result, payload = run_workflow_step(root, simple=False)
    snapshot = build_shell_snapshot(root)

    if payload is None:
        return ActionLaunchResult(
            action_id="execute",
            ok=False,
            summary="Execute failed",
            detail="; ".join(result.errors) or "workflow runner evaluation failed",
            snapshot=snapshot,
        )

    action_taken = payload.get("action_taken", "none")
    if action_taken == "none":
        return ActionLaunchResult(
            action_id="execute",
            ok=False,
            summary="Execute gated",
            detail=payload.get("gate_reason", "") or "workflow step is currently gated",
            snapshot=snapshot,
        )

    return ActionLaunchResult(
        action_id="execute",
        ok=True,
        summary=f"Execute ok: {action_taken}",
        detail=payload.get("recommended_prompt", ""),
        snapshot=snapshot,
    )


def launch_review_flow(root: Path, snapshot: GrainShellSnapshot) -> ActionLaunchResult:
    task_id = snapshot.active_task_id
    if not task_id or task_id == "none":
        return ActionLaunchResult(
            action_id="review",
            ok=False,
            summary="Review unavailable",
            detail="no active task is available for review handoff",
            snapshot=snapshot,
        )

    result, artifact, resolved_path = materialize_handoff_artifact(root, task_id)
    refreshed = build_shell_snapshot(root)
    if artifact is None:
        return ActionLaunchResult(
            action_id="review",
            ok=False,
            summary="Review handoff failed",
            detail="; ".join(result.errors) or "handoff generation failed",
            snapshot=refreshed,
        )

    return ActionLaunchResult(
        action_id="review",
        ok=True,
        summary="Review handoff ready",
        detail=str(resolved_path),
        snapshot=refreshed,
    )


def launch_close_flow(root: Path, snapshot: GrainShellSnapshot) -> ActionLaunchResult:
    task_id = snapshot.active_task_id
    if not task_id or task_id == "none":
        return ActionLaunchResult(
            action_id="close",
            ok=False,
            summary="Close unavailable",
            detail="no active task is available for closure",
            snapshot=snapshot,
        )

    result = task_service.close_packet(root, task_id)
    refreshed = build_shell_snapshot(root)
    if not result.ok:
        return ActionLaunchResult(
            action_id="close",
            ok=False,
            summary="Close blocked",
            detail="; ".join(result.errors) or "closure validation failed",
            snapshot=refreshed,
        )

    return ActionLaunchResult(
        action_id="close",
        ok=True,
        summary="Close ok",
        detail=task_id,
        snapshot=refreshed,
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
    lines = [
        "Prompt Status",
        f"recommended_prompt: {snapshot.recommended_prompt or 'none'}",
        f"scope: {snapshot.prompt_scope or 'none'}",
        f"stage: {snapshot.prompt_stage or 'none'}",
        f"model_class: {snapshot.model_class or 'none'}",
    ]
    if snapshot.prompt_preview_lines:
        lines.append("preview:")
        lines.extend(f"- {line}" for line in snapshot.prompt_preview_lines[:3])
    return "\n".join(lines)


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
    if packet.results_summary:
        lines.append(f"results_summary: {packet.results_summary}")
    return "\n".join(lines)


def _render_action_panel(snapshot: GrainShellSnapshot) -> str:
    lines = [
        "Actions",
        "[e] execute workflow step",
        "[r] review handoff",
        "[c] close task",
    ]
    if snapshot.last_action_summary:
        lines.extend(["", "Last Action", snapshot.last_action_summary])
    return "\n".join(lines)


def _render_context_panel(snapshot: GrainShellSnapshot) -> str:
    context = snapshot.context_preview
    if context is None:
        return "\n".join(
            [
                "Context Preview",
                "- no active task context available",
            ]
        )

    lines = [
        "Context Preview",
        f"primary_adapter: {context.primary_adapter}",
        f"sources: {context.source_count}",
        f"packet_sources: {context.packet_source_count}",
        f"canonical_docs: {context.canonical_doc_count}",
        f"working_docs: {context.working_doc_count}",
        f"estimated_tokens: {context.estimated_tokens}",
        f"token_warning: {'yes' if context.token_warning else 'no'}",
    ]
    if context.top_sources:
        lines.append("top_sources:")
        lines.extend(f"- {path}" for path in context.top_sources[:3])
    if context.trim_hints:
        lines.append("trim_hints:")
        lines.extend(f"- {item}" for item in context.trim_hints[:3])
    return "\n".join(lines)


def _render_observability_panel(snapshot: GrainShellSnapshot) -> str:
    observability = snapshot.observability_preview
    if observability is None:
        return "\n".join(
            [
                "Observability",
                "- no active task metadata recorded",
            ]
        )

    return "\n".join(
        [
            "Observability",
            f"executor_identity: {observability.executor_identity or 'unset'}",
            f"model_class: {observability.model_class or 'unset'}",
            f"last_stage: {observability.last_stage or 'unset'}",
            f"last_action: {observability.last_workflow_action or 'unset'}",
            f"updated_at: {observability.updated_at or 'unset'}",
        ]
    )


def _render_blocker_detail_panel(snapshot: GrainShellSnapshot) -> str:
    lines = ["Blocker Detail"]
    if snapshot.blocking_reasons:
        lines.extend(f"- {reason}" for reason in snapshot.blocking_reasons[:5])
    else:
        lines.append("- no active blocking reasons")

    if snapshot.affected_artifacts:
        lines.append("affected_artifacts:")
        lines.extend(f"- {artifact}" for artifact in snapshot.affected_artifacts[:5])
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
        BINDINGS = [
            ("e", "execute_flow", "Execute"),
            ("r", "review_flow", "Review"),
            ("c", "close_flow", "Close"),
        ]
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

        #center-column {
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
                    with Container(id="left-column", classes="stack"):
                        yield Static(
                            _render_status_panel(snapshot),
                            id="summary",
                            classes="panel",
                        )
                        yield Static(_render_backlog_panel(snapshot), classes="panel", id="backlog")
                        yield Static(_render_context_panel(snapshot), classes="panel", id="context")
                    with Container(id="center-column", classes="stack"):
                        yield Static(_render_task_panel(snapshot), classes="panel", id="task")
                        yield Static(_render_packet_panel(snapshot), classes="panel", id="packet")
                        yield Static(_render_prompt_panel(snapshot), classes="panel", id="prompt")
                    with Container(id="right-column", classes="stack"):
                        yield Static(_render_queue_panel(snapshot), classes="panel", id="queue")
                        yield Static(_render_observability_panel(snapshot), classes="panel", id="observability")
                        yield Static(_render_blocker_detail_panel(snapshot), classes="panel", id="blockers")
                        yield Static(_render_action_panel(snapshot), classes="panel", id="actions")
            yield Footer()

        def _apply_action_result(self, result: ActionLaunchResult) -> None:
            nonlocal snapshot
            next_snapshot = result.snapshot or snapshot
            summary = result.summary if not result.detail else f"{result.summary}: {result.detail}"
            snapshot = GrainShellSnapshot(
                **{
                    **next_snapshot.__dict__,
                    "last_action_summary": summary,
                }
            )
            self.query_one("#summary", Static).update(_render_status_panel(snapshot))
            self.query_one("#backlog", Static).update(_render_backlog_panel(snapshot))
            self.query_one("#context", Static).update(_render_context_panel(snapshot))
            self.query_one("#task", Static).update(_render_task_panel(snapshot))
            self.query_one("#packet", Static).update(_render_packet_panel(snapshot))
            self.query_one("#prompt", Static).update(_render_prompt_panel(snapshot))
            self.query_one("#queue", Static).update(_render_queue_panel(snapshot))
            self.query_one("#observability", Static).update(_render_observability_panel(snapshot))
            self.query_one("#blockers", Static).update(_render_blocker_detail_panel(snapshot))
            self.query_one("#actions", Static).update(_render_action_panel(snapshot))

        def action_execute_flow(self) -> None:
            self._apply_action_result(launch_execute_flow(root))

        def action_review_flow(self) -> None:
            self._apply_action_result(launch_review_flow(root, snapshot))

        def action_close_flow(self) -> None:
            self._apply_action_result(launch_close_flow(root, snapshot))

    return GrainApp()


def launch_tui(root: Path) -> None:
    app = create_app(root)
    app.run()


def _read_results_summary(results_path: Path) -> str:
    if not results_path.exists():
        return ""
    in_summary = False
    for line in results_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == "## Summary":
            in_summary = True
            continue
        if in_summary:
            if stripped.startswith("## "):
                break
            if stripped:
                return stripped
    return ""
