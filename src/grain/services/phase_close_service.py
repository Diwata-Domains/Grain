# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Phase close service — validates and seals a completed phase."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

# Package-internal parsers reused from workflow_service.
from grain.services.workflow_service import (
    _is_phase_properly_closed,
    _read_current_phase,
    _read_current_task,
    _read_phase_backlog_tasks,
)

_DEFAULT_PHASE_DOC = "docs/working/current_focus.md"
_DEFAULT_BACKLOG_DOC = "docs/working/backlog.md"
_DEFAULT_CURRENT_TASK_DOC = "docs/working/current_task.md"
_DEFAULT_METRICS_DOC = "docs/working/workflow_metrics.md"


@dataclass
class PhaseCloseResult:
    ok: bool
    closed_phase: str = ""
    tasks_done: int = 0
    errors: list[str] = field(default_factory=list)
    dry_run: bool = False
    marker_written: str = ""
    archive_path: str = ""
    packets_archived: list[str] = field(default_factory=list)
    packets_archive_path: str = ""


def close_phase(
    root: Path,
    dry_run: bool = False,
    phase_override: str | None = None,
    *,
    keep_tasks: bool = False,
) -> PhaseCloseResult:
    """Validate and seal the current phase.

    Writes a ``Phase N closed:`` marker to ``current_focus.md`` that the
    workflow evaluator checks before allowing next-phase routing.  Does not
    advance the current-phase line — the operator/agent updates
    ``## Current Phase`` explicitly after this command succeeds.

    If ``phase_override`` is given it must match the active phase exactly —
    this guards against accidentally closing the wrong phase.
    """
    current_focus_path = root / _DEFAULT_PHASE_DOC
    backlog_path = root / _DEFAULT_BACKLOG_DOC
    current_task_path = root / _DEFAULT_CURRENT_TASK_DOC

    for p in (current_focus_path, backlog_path, current_task_path):
        if not p.exists():
            return PhaseCloseResult(
                ok=False,
                errors=[f"missing required doc: {p.relative_to(root)}"],
            )

    current_phase = _read_current_phase(current_focus_path)
    if not current_phase:
        return PhaseCloseResult(
            ok=False,
            errors=["unable to parse current phase from current_focus.md"],
        )

    if phase_override is not None and phase_override != current_phase:
        return PhaseCloseResult(
            ok=False,
            closed_phase=current_phase,
            errors=[
                f"--phase {phase_override} does not match the active phase ({current_phase}) — "
                "grain phase close only seals the currently active phase"
            ],
        )

    if current_phase == "0":
        return PhaseCloseResult(
            ok=False,
            closed_phase=current_phase,
            errors=["cannot close bootstrap phase — run the onboarding prompt first"],
        )

    if _is_phase_properly_closed(current_focus_path, current_phase):
        return PhaseCloseResult(
            ok=False,
            closed_phase=current_phase,
            errors=[
                f"Phase {current_phase} is already sealed — "
                f"update '## Current Phase' in current_focus.md to begin the next phase"
            ],
        )

    current_task = _read_current_task(current_task_path)
    if current_task is None:
        return PhaseCloseResult(
            ok=False,
            errors=["current_task.md is missing required fields"],
        )
    if current_task["task_id"] != "none":
        return PhaseCloseResult(
            ok=False,
            closed_phase=current_phase,
            errors=[
                f"active task in flight: {current_task['task_id']} — "
                "close it before sealing the phase"
            ],
        )

    tasks = _read_phase_backlog_tasks(backlog_path, current_phase)
    if not tasks:
        return PhaseCloseResult(
            ok=False,
            closed_phase=current_phase,
            errors=[
                f"no tasks found for Phase {current_phase} in backlog — "
                "cannot verify completion"
            ],
        )

    open_tasks = [t for t in tasks if t.status != "done"]
    if open_tasks:
        return PhaseCloseResult(
            ok=False,
            closed_phase=current_phase,
            errors=[
                f"Phase {current_phase} has {len(open_tasks)} open task(s) — "
                "all tasks must be 'done' before sealing:",
                *[f"  {t.task_ref}: {t.status}" for t in open_tasks],
            ],
        )

    metrics_path = root / _DEFAULT_METRICS_DOC
    if metrics_path.exists():
        metrics_text = metrics_path.read_text(encoding="utf-8")
        heading = f"### Phase {current_phase}"
        if heading not in metrics_text:
            return PhaseCloseResult(
                ok=False,
                closed_phase=current_phase,
                errors=[
                    f"workflow_metrics.md has no entry for Phase {current_phase} — "
                    f"add a '### Phase {current_phase}' section before sealing"
                ],
            )

    done_count = len(tasks)

    if dry_run:
        from grain.services.archive_service import move_phase_packets
        packets_result = move_phase_packets(
            root, current_phase, keep_tasks=keep_tasks, dry_run=True
        )
        return PhaseCloseResult(
            ok=True,
            closed_phase=current_phase,
            tasks_done=done_count,
            dry_run=True,
            packets_archived=packets_result.moved,
            packets_archive_path=packets_result.archive_path if not keep_tasks else "",
        )

    today = date.today().isoformat()
    marker_line = (
        f"Phase {current_phase} closed: {today} — "
        f"{done_count} tasks done (grain-verified)"
    )
    text = current_focus_path.read_text(encoding="utf-8")
    text = text.rstrip("\n") + f"\n\n{marker_line}\n"
    current_focus_path.write_text(text, encoding="utf-8")

    from grain.services.archive_service import archive_phase_docs, move_phase_packets
    archive_result = archive_phase_docs(root, current_phase, done_count, dry_run=False)
    archive_path = archive_result.archive_path if archive_result.ok else ""

    # Archive task packets after the doc snapshot so metadata.json is updated
    # in place with tasks_archive + packets_archived_count.
    packets_result = move_phase_packets(root, current_phase, keep_tasks=keep_tasks)

    # Side-band telemetry (opt-in, never raises, never alters control flow or
    # timing). emit_built guards builder construction too.
    from grain.services.telemetry_service import emit_built, make_phase_close_event
    emit_built(root, make_phase_close_event, current_phase, done_count)

    # Surface (never swallow) a packet-move failure: on an archive collision the
    # move can be partially applied (earlier packets archived, later ones left in
    # tasks/, metadata's tasks_archive unwritten). The marker + doc snapshot are
    # already on disk, so report the close as failed and propagate the errors so
    # the operator knows the packet archive did not complete cleanly.
    packets_failed = not keep_tasks and not packets_result.ok
    return PhaseCloseResult(
        ok=not packets_failed,
        closed_phase=current_phase,
        tasks_done=done_count,
        dry_run=False,
        marker_written=_DEFAULT_PHASE_DOC,
        archive_path=archive_path,
        packets_archived=packets_result.moved,
        packets_archive_path=(
            packets_result.archive_path if not keep_tasks else ""
        ),
        errors=list(packets_result.errors),
    )
