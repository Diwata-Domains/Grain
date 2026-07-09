# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Phase archive service — move closed phase packets to tasks/archive/phase-N/."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

_PHASE_CLOSED_MARKER_RE = re.compile(r"^Phase\s+(\d+)\s+closed:")
_BACKLOG_PHASE_HEADING = re.compile(r"^(##\s+(?:\d+\.\s+)?Phase\s+(\d+)\s+—\s+.*?)(\s*✓?\s*CLOSED.*)?$")
_TASK_DIR_RE = re.compile(r"^P(\d+)-T\d+")


@dataclass
class PhaseArchiveResult:
    ok: bool
    phase: str = ""
    packets_moved: list[str] = field(default_factory=list)
    archive_path: str = ""
    errors: list[str] = field(default_factory=list)
    dry_run: bool = False


def archive_phase(root: Path, phase_number: str, dry_run: bool = False) -> PhaseArchiveResult:
    """Move closed phase packets to tasks/archive/phase-N/.

    Validates:
    1. phase_number is a valid integer.
    2. current_focus.md contains a grain-verified closed marker for this phase.
    3. At least one packet directory for this phase exists in tasks/.
    4. tasks/archive/phase-N/ does not already exist.

    Moves all P<N>-T* directories from tasks/ to tasks/archive/phase-N/.
    Updates the phase section header in backlog.md to mark it as archived.
    """
    # ── Validate phase number ────────────────────────────────────────────────
    try:
        phase_int = int(phase_number)
    except ValueError:
        return PhaseArchiveResult(
            ok=False,
            phase=phase_number,
            errors=[f"invalid phase number: {phase_number!r}"],
        )

    current_focus_path = root / "docs" / "working" / "current_focus.md"
    tasks_dir = root / "tasks"
    archive_dir = tasks_dir / "archive" / f"phase-{phase_int}"
    backlog_path = root / "docs" / "working" / "backlog.md"

    # ── Check current_focus.md exists ───────────────────────────────────────
    if not current_focus_path.exists():
        return PhaseArchiveResult(
            ok=False,
            phase=phase_number,
            errors=["docs/working/current_focus.md not found"],
        )

    # ── Validate phase is sealed ─────────────────────────────────────────────
    if not _is_phase_closed(current_focus_path, str(phase_int)):
        return PhaseArchiveResult(
            ok=False,
            phase=phase_number,
            errors=[
                f"Phase {phase_int} does not have a grain-verified closed marker in "
                "current_focus.md — run `grain phase close` first"
            ],
        )

    # ── Find packets for this phase ──────────────────────────────────────────
    if not tasks_dir.exists():
        return PhaseArchiveResult(
            ok=False,
            phase=phase_number,
            errors=["tasks/ directory not found"],
        )

    packets = _find_phase_packets(tasks_dir, str(phase_int))
    if not packets:
        return PhaseArchiveResult(
            ok=False,
            phase=phase_number,
            errors=[
                f"no packet directories found for Phase {phase_int} in tasks/ "
                "(already archived or no packets were created)"
            ],
        )

    # ── Check archive destination doesn't already exist ──────────────────────
    if archive_dir.exists():
        return PhaseArchiveResult(
            ok=False,
            phase=phase_number,
            errors=[
                f"archive destination already exists: {archive_dir.relative_to(root)} "
                "— phase may already be archived"
            ],
        )

    # ── Execute moves ────────────────────────────────────────────────────────
    moved: list[str] = []
    rel_archive = str(archive_dir.relative_to(root))

    if not dry_run:
        archive_dir.mkdir(parents=True, exist_ok=True)

    for packet_dir in sorted(packets):
        dest = archive_dir / packet_dir.name
        moved.append(str(packet_dir.relative_to(root)))
        if not dry_run:
            shutil.move(str(packet_dir), str(dest))

    # ── Update backlog.md section header ────────────────────────────────────
    if not dry_run and backlog_path.exists():
        _mark_backlog_phase_archived(backlog_path, str(phase_int))

    return PhaseArchiveResult(
        ok=True,
        phase=str(phase_int),
        packets_moved=moved,
        archive_path=rel_archive,
        dry_run=dry_run,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────


def _is_phase_closed(current_focus_path: Path, phase_number: str) -> bool:
    for line in current_focus_path.read_text(encoding="utf-8").splitlines():
        m = _PHASE_CLOSED_MARKER_RE.match(line.strip())
        if m and m.group(1) == phase_number:
            return True
    return False


def _find_phase_packets(tasks_dir: Path, phase_number: str) -> list[Path]:
    prefix = f"P{phase_number}-T"
    return [
        p for p in tasks_dir.iterdir()
        if p.is_dir() and p.name.startswith(prefix)
    ]


def _mark_backlog_phase_archived(backlog_path: Path, phase_number: str) -> None:
    """Append '— archived' to the phase heading in backlog.md if not already present."""
    lines = backlog_path.read_text(encoding="utf-8").splitlines(keepends=True)
    result = []
    for line in lines:
        m = _BACKLOG_PHASE_HEADING.match(line.rstrip())
        if m and m.group(2) == phase_number and "archived" not in line.lower():
            line = line.rstrip().rstrip() + " — archived\n"
        result.append(line)
    backlog_path.write_text("".join(result), encoding="utf-8")
