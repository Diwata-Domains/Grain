# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Read-only phase inventory service.

Parses ``docs/working/backlog.md`` for every ``## Phase N — <title>`` heading,
its ``> **Status:**`` value and per-task status rollup, then annotates each
phase with the active-phase pointer and closed markers read from
``docs/working/current_focus.md``.  Nothing here mutates state.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Canonical backlog heading is `## Phase N — Title`; older scaffolds number the
# heading as `## N. Phase N — Title`. Accept BOTH — the tolerant `(?:\d+\.\s+)?`
# prefix mirrors cli/status.py and services/workflow_service.py. Demanding the
# numbered form is the exact bug that made `grain status` report `0 total`.
_PHASE_HEADING = re.compile(r"^##\s+(?:\d+\.\s+)?Phase\s+(\d+)\s+—\s*(.*)$")
_SECTION_HEADING = re.compile(r"^##\s+")
_TASK_HEADING = re.compile(r"^###\s+(P\d+-T\d+)")
_TASK_STATUS = re.compile(r"^-\s+\*\*Status:\*\*\s*(\S+)")
_HEADING_STATUS = re.compile(r"^>\s*\*\*Status:\*\*\s*(.*)$")

_CURRENT_PHASE_LINE = re.compile(r"^Phase\s+(\d+)\s*[—–:-]")
_CURRENT_PHASE_COMPLETE_LINE = re.compile(r"^(Phase:\s*)?(complete|done)\s*$", re.IGNORECASE)
_PHASE_CLOSED_MARKER = re.compile(r"^Phase\s+(\d+)\s+closed:")

_DEFAULT_PHASE_DOC = "docs/working/current_focus.md"
_DEFAULT_BACKLOG_DOC = "docs/working/backlog.md"

_ROLLUP_KEYS = ("total", "done", "ready", "in_progress", "blocked")


@dataclass
class PhaseTask:
    task_ref: str
    status: str


@dataclass
class PhaseSummary:
    number: str
    title: str
    status: str = ""
    active: bool = False
    closed: bool = False
    tasks: list[PhaseTask] = field(default_factory=list)

    def rollup(self) -> dict[str, int]:
        counts = {key: 0 for key in _ROLLUP_KEYS}
        for task in self.tasks:
            counts["total"] += 1
            status = task.status.lower().rstrip(".,")
            if status in counts:
                counts[status] += 1
        return counts


@dataclass
class PhaseInventory:
    active_phase: str
    phases: list[PhaseSummary] = field(default_factory=list)

    def active(self) -> PhaseSummary | None:
        for phase in self.phases:
            if phase.number == self.active_phase:
                return phase
        return None


def query_phases(root: Path) -> PhaseInventory:
    """Return every backlog phase with its status, rollup, and markers."""
    backlog_path = root / _DEFAULT_BACKLOG_DOC
    focus_path = root / _DEFAULT_PHASE_DOC

    active_phase = _read_active_phase(focus_path)
    closed_phases = _read_closed_phases(focus_path)

    phases = _parse_backlog(backlog_path)
    for phase in phases:
        phase.active = phase.number == active_phase
        phase.closed = phase.number in closed_phases

    return PhaseInventory(active_phase=active_phase, phases=phases)


def _parse_backlog(backlog_path: Path) -> list[PhaseSummary]:
    if not backlog_path.exists():
        return []

    phases: list[PhaseSummary] = []
    current: PhaseSummary | None = None

    for line in backlog_path.read_text(encoding="utf-8").splitlines():
        phase_match = _PHASE_HEADING.match(line)
        if phase_match:
            current = PhaseSummary(
                number=phase_match.group(1),
                title=phase_match.group(2).strip(),
            )
            phases.append(current)
            continue

        if _SECTION_HEADING.match(line):
            # Any other level-2 heading (## Purpose, ## Backlog Maintenance
            # Rules, …) ends the current phase block.
            current = None
            continue

        if current is None:
            continue

        if not current.status:
            heading_status = _HEADING_STATUS.match(line)
            if heading_status:
                current.status = heading_status.group(1).strip()
                continue

        task_match = _TASK_HEADING.match(line)
        if task_match:
            current.tasks.append(PhaseTask(task_ref=task_match.group(1), status=""))
            continue

        if current.tasks and not current.tasks[-1].status:
            status_match = _TASK_STATUS.match(line)
            if status_match:
                current.tasks[-1].status = status_match.group(1)

    return phases


def _read_active_phase(focus_path: Path) -> str:
    if not focus_path.exists():
        return ""
    for line in focus_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if _CURRENT_PHASE_COMPLETE_LINE.match(stripped):
            return "complete"
        match = _CURRENT_PHASE_LINE.match(stripped)
        if match:
            return match.group(1)
    return ""


def _read_closed_phases(focus_path: Path) -> set[str]:
    if not focus_path.exists():
        return set()
    closed: set[str] = set()
    for line in focus_path.read_text(encoding="utf-8").splitlines():
        match = _PHASE_CLOSED_MARKER.match(line.strip())
        if match:
            closed.add(match.group(1))
    return closed


def phase_to_dict(phase: PhaseSummary) -> dict:
    data = asdict(phase)
    data["tasks_rollup"] = phase.rollup()
    return data
