# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Reconcile service — detect and optionally repair drift across working docs."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

_TASK_HEADING = re.compile(r"^###\s+(P(\d+)-T(\d+))\s+—\s+")
_BACKLOG_STATUS = re.compile(r"^- \*\*Status:\*\*\s*(\S+)")
_PACKET_STATUS = re.compile(r"^\*\*Status:\*\*\s*(\S+)", re.IGNORECASE)
_PACKET_STATUS_ALT = re.compile(r"^-\s*\*\*Status:\*\*\s*(\S+)", re.IGNORECASE)
_TASK_ID_LINE = re.compile(r"^Task ID:\s*(\S+)", re.IGNORECASE)
# Packets store ID as "- **ID:** TASK-####"
_PACKET_ID_LINE = re.compile(r"^-\s*\*\*ID:\*\*\s*(\S+)", re.IGNORECASE)
_TASK_PATH_LINE = re.compile(r"^Task Path:\s*(\S+)", re.IGNORECASE)
_CURRENT_TASK_STATUS_LINE = re.compile(r"^Status:\s*(\S+)", re.IGNORECASE)
# Canonical backlog form is `## Phase N —`; older scaffolds number the heading.
_BACKLOG_PHASE_HEADING = re.compile(r"^##\s+(?:\d+\.\s+)?Phase\s+(\d+)\b")
# Kept identical to workflow_service._CURRENT_PHASE_LINE: accept em dash, en
# dash, hyphen, or colon so a hand-edited focus doc parses the same way here as
# in the evaluator.
_CURRENT_PHASE_LINE = re.compile(r"^Phase\s+(\d+)\s*[—–:-]")
_PHASE_CLOSED_MARKER = re.compile(r"^Phase\s+(\d+)\s+closed:")
# Canonical `## Current Phase` form is an em dash: `Phase N — Title`. Any phase
# line that carries a number but not an em-dash separator is normalizable.
_FOCUS_PHASE_NUM = re.compile(r"^Phase\s+(\d+)\b")
_FOCUS_PHASE_EMDASH = re.compile(r"^Phase\s+(\d+)\s*—")


@dataclass
class ReconcileIssue:
    severity: str  # "error" or "warning"
    check: str
    description: str
    fix_available: bool = False
    fix_description: str = ""


@dataclass
class ReconcileResult:
    ok: bool
    issues: list[ReconcileIssue] = field(default_factory=list)
    fixed: list[str] = field(default_factory=list)
    dry_run: bool = False


def reconcile(root: Path, fix: bool = False, dry_run: bool = False) -> ReconcileResult:
    """Detect drift across working docs and optionally repair it.

    Checks:
    1. Backlog task statuses vs existing packet task.md Status fields.
    2. current_task.md pointer vs active packet status.
    3. Packets with Status: needs_fix not visible in current_task.md.

    With ``fix=True`` (or ``dry_run=True``), auto-repairs safe drift:
    - Backlog status out of sync with a done packet → update backlog to done.
    - current_task.md pointing to a completed packet → reset to none/idle.
    """
    backlog_path = root / "docs" / "working" / "backlog.md"
    current_task_path = root / "docs" / "working" / "current_task.md"
    tasks_dir = root / "tasks"

    issues: list[ReconcileIssue] = []
    fixed: list[str] = []
    resolved_indices: set[int] = set()

    if not backlog_path.exists():
        return ReconcileResult(
            ok=False,
            issues=[
                ReconcileIssue(
                    severity="error",
                    check="required_docs",
                    description="docs/working/backlog.md not found",
                )
            ],
        )
    if not current_task_path.exists():
        return ReconcileResult(
            ok=False,
            issues=[
                ReconcileIssue(
                    severity="error",
                    check="required_docs",
                    description="docs/working/current_task.md not found",
                )
            ],
        )

    # ── Read current_task.md ─────────────────────────────────────────────────
    current_task_info = _read_current_task(current_task_path)
    active_task_id = current_task_info.get("task_id", "none")
    active_task_path = current_task_info.get("task_path", "none")
    current_task_info.get("status", "idle")

    # ── Check 1: backlog vs packet status sync ───────────────────────────────
    backlog_tasks = _read_all_backlog_tasks(backlog_path)
    backlog_text = backlog_path.read_text(encoding="utf-8")

    for task_ref, backlog_status in backlog_tasks.items():
        packet_dir = _find_packet_dir(tasks_dir, task_ref)
        if packet_dir is None:
            # A task the backlog considers done or in flight must have a packet
            # on disk. Its absence is drift — a deleted/orphaned packet, or a
            # status hand-advanced ahead of any packet — so surface it instead of
            # silently skipping. Ready/planned tasks legitimately have no packet
            # yet. Report-only: recreating a lost packet is an operator judgement,
            # never a safe auto-fix.
            if backlog_status in {"done", "in_progress"}:
                issues.append(
                    ReconcileIssue(
                        severity="warning",
                        check="missing_packet",
                        description=(
                            f"{task_ref}: backlog says '{backlog_status}' but no packet "
                            f"directory exists under tasks/ — orphaned status with no "
                            f"backing packet"
                        ),
                        fix_available=False,
                        fix_description=(
                            "manual: recreate the task packet with `grain task create` "
                            "or correct the backlog status"
                        ),
                    )
                )
            continue  # No packet to compare status against

        packet_status = _read_packet_status(packet_dir)
        if packet_status is None:
            continue  # Can't read packet status

        if packet_status == backlog_status:
            continue  # In sync

        # Determine if this is a safe auto-fix
        fix_available = packet_status == "done" and backlog_status != "done"
        fix_desc = f"update backlog {task_ref} status from '{backlog_status}' to 'done'" if fix_available else ""

        severity = "error" if packet_status == "done" and backlog_status not in {"done", "review"} else "warning"
        issues.append(
            ReconcileIssue(
                severity=severity,
                check="packet_backlog_mismatch",
                description=(
                    f"{task_ref}: backlog says '{backlog_status}' but packet task.md says '{packet_status}'"
                ),
                fix_available=fix_available,
                fix_description=fix_desc,
            )
        )

        if fix_available and (fix or dry_run):
            new_backlog_text = _update_backlog_task_status(backlog_text, task_ref, "done")
            if new_backlog_text != backlog_text:
                if not dry_run:
                    backlog_path.write_text(new_backlog_text, encoding="utf-8")
                    backlog_text = new_backlog_text
                fixed.append(f"backlog {task_ref}: '{backlog_status}' -> 'done'")
                resolved_indices.add(len(issues) - 1)

    # ── Check 2: current_task.md stale pointer ───────────────────────────────
    if active_task_id not in {"none", "", "none\n"}:
        # Try to find the packet by ID or path
        packet_dir = _find_packet_by_id_or_path(tasks_dir, root, active_task_id, active_task_path)
        if packet_dir is not None:
            packet_status = _read_packet_status(packet_dir)
            if packet_status == "done":
                issues.append(
                    ReconcileIssue(
                        severity="error",
                        check="current_task_stale",
                        description=(
                            f"current_task.md points to {active_task_id} "
                            f"but that packet has Status: done — stale pointer"
                        ),
                        fix_available=True,
                        fix_description="reset current_task.md to Task ID: none / Status: idle",
                    )
                )
                if fix or dry_run:
                    if not dry_run:
                        _clear_current_task(current_task_path)
                        active_task_id = "none"
                    fixed.append("current_task.md: reset to Task ID: none / Status: idle")
                    resolved_indices.add(len(issues) - 1)

    # ── Check 3: needs_fix packets not visible in current_task.md ───────────
    if tasks_dir.exists():
        for packet_dir in sorted(tasks_dir.iterdir()):
            if not packet_dir.is_dir():
                continue
            if packet_dir.name.startswith("archive"):
                continue
            packet_status = _read_packet_status(packet_dir)
            if packet_status != "needs_fix":
                continue
            task_id = _read_task_id_from_packet(packet_dir)
            if task_id and task_id == active_task_id:
                continue  # Visible in current_task.md
            issues.append(
                ReconcileIssue(
                    severity="warning",
                    check="needs_fix_invisible",
                    description=(
                        f"packet {packet_dir.name} has Status: needs_fix "
                        f"but is not referenced in current_task.md"
                    ),
                    fix_available=False,
                    fix_description="manual: update current_task.md to point to this task",
                )
            )

    # ── Check 4: current_focus.md '## Current Phase' separator is canonical ──
    focus_path = root / "docs" / "working" / "current_focus.md"
    focus_issue = _detect_unparseable_focus_phase(focus_path)
    if focus_issue is not None:
        issues.append(focus_issue)
        if focus_issue.fix_available and (fix or dry_run):
            focus_text = focus_path.read_text(encoding="utf-8")
            new_focus_text, changed = _normalize_focus_phase_separator(focus_text)
            if changed:
                if not dry_run:
                    focus_path.write_text(new_focus_text, encoding="utf-8")
                fixed.append(
                    "current_focus.md: normalized '## Current Phase' separator to em dash"
                )
                resolved_indices.add(len(issues) - 1)

    issues.extend(_check_phase_consistency(root))

    # ok reflects remaining (unresolved) errors only
    ok = not any(
        i.severity == "error"
        for idx, i in enumerate(issues)
        if idx not in resolved_indices
    )
    return ReconcileResult(ok=ok, issues=issues, fixed=fixed, dry_run=dry_run)


def _check_phase_consistency(root: Path) -> list[ReconcileIssue]:
    """Detect phase-level drift between current_focus.md and backlog.md.

    Packet-level checks above cannot see this, yet it is what stops
    `grain workflow next` with `workflow_state_drift` or
    `previous_phase_not_closed`. Reported, never auto-fixed: resolving it means
    deciding whether a phase is finished, which is an operator judgement.
    """
    focus_path = root / "docs" / "working" / "current_focus.md"
    backlog_path = root / "docs" / "working" / "backlog.md"
    if not focus_path.exists() or not backlog_path.exists():
        return []

    focus_text = focus_path.read_text(encoding="utf-8")
    active_phase = _active_phase(focus_text)
    if not active_phase:
        return []

    backlog_phases = {
        m.group(1)
        for line in backlog_path.read_text(encoding="utf-8").splitlines()
        if (m := _BACKLOG_PHASE_HEADING.match(line))
    }

    issues: list[ReconcileIssue] = []

    if active_phase not in backlog_phases:
        issues.append(
            ReconcileIssue(
                severity="error",
                check="phase_consistency",
                description=(
                    f"current_focus.md declares Phase {active_phase} but backlog.md has "
                    f"no '## Phase {active_phase}' block"
                ),
                fix_available=False,
                fix_description=(
                    "manual: add the phase block to backlog.md, or point "
                    "'## Current Phase' at a phase that exists"
                ),
            )
        )

    phase_int = int(active_phase)
    # Read the same per-repo threshold the evaluator uses so this check does not
    # demand a close marker the evaluator would not.
    from grain.services.workflow_service import phase_close_enforced_threshold

    if phase_int > phase_close_enforced_threshold(root):
        closed = {
            m.group(1)
            for line in focus_text.splitlines()
            if (m := _PHASE_CLOSED_MARKER.match(line.strip()))
        }
        prev = str(phase_int - 1)
        if prev not in closed:
            issues.append(
                ReconcileIssue(
                    severity="error",
                    check="phase_close_chain",
                    description=(
                        f"Phase {active_phase} is active but Phase {prev} carries no "
                        f"'Phase {prev} closed:' marker in current_focus.md — "
                        f"`grain workflow next` will refuse to route"
                    ),
                    fix_available=False,
                    fix_description=(
                        f"manual: seal it with `grain phase close -p {prev}` "
                        f"(add --allow-empty for a planning or deferred phase)"
                    ),
                )
            )

    return issues


def _detect_unparseable_focus_phase(focus_path: Path) -> ReconcileIssue | None:
    """Flag a '## Current Phase' line whose separator is not the canonical em dash.

    `grain workflow explain` routes agents here when the current phase is
    malformed. The evaluator tolerates a hand-edited hyphen/colon, but a
    non-canonical separator still drifts from the form every other doc uses, so
    reconcile reports it and offers a one-step repair (normalize to an em dash).
    Only the '## Current Phase' line is considered; a 'complete'/'done' marker or
    a missing focus doc is left alone.
    """
    if not focus_path.exists():
        return None

    phase_line = _current_phase_line(focus_path.read_text(encoding="utf-8"))
    if phase_line is None:
        return None
    if _FOCUS_PHASE_EMDASH.match(phase_line):
        return None  # already canonical
    if not _FOCUS_PHASE_NUM.match(phase_line):
        return None  # not a phase line (e.g. a 'complete' marker)

    return ReconcileIssue(
        severity="error",
        check="focus_phase_parseable",
        description=(
            f"current_focus.md '## Current Phase' line '{phase_line}' uses a "
            f"non-canonical separator — the canonical form is 'Phase N — Title' "
            f"with an em dash"
        ),
        fix_available=True,
        fix_description="normalize the '## Current Phase' separator to an em dash (—)",
    )


def _current_phase_line(focus_text: str) -> str | None:
    """Return the first non-empty line under '## Current Phase', or None."""
    lines = focus_text.splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == "## Current Phase":
            for candidate in lines[idx + 1:]:
                stripped = candidate.strip()
                if not stripped:
                    continue
                if stripped.startswith("##"):
                    return None
                return stripped
    return None


def _normalize_focus_phase_separator(text: str) -> tuple[str, bool]:
    """Rewrite the '## Current Phase' line to use a canonical em-dash separator."""
    lines = text.splitlines(keepends=True)
    in_section = False
    for i, raw in enumerate(lines):
        stripped = raw.strip()
        if stripped == "## Current Phase":
            in_section = True
            continue
        if not in_section:
            continue
        if not stripped:
            continue
        if stripped.startswith("##"):
            break
        if _FOCUS_PHASE_NUM.match(stripped) and not _FOCUS_PHASE_EMDASH.match(stripped):
            trailing = raw[len(raw.rstrip("\n")):]
            lines[i] = _normalize_phase_line(stripped) + trailing
            return "".join(lines), True
        break
    return text, False


def _normalize_phase_line(line: str) -> str:
    """`Phase 1 - Foundation` / `Phase 1: Foundation` → `Phase 1 — Foundation`."""
    m = _FOCUS_PHASE_NUM.match(line)
    assert m is not None  # caller guarantees a phase number
    number = m.group(1)
    rest = re.sub(r"^[—–:/\-]+\s*", "", line[m.end():].lstrip())
    return f"Phase {number} — {rest}" if rest else f"Phase {number} —"


def _active_phase(focus_text: str) -> str:
    """Return the phase number under '## Current Phase', or ""."""
    lines = focus_text.splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == "## Current Phase":
            for candidate in lines[idx + 1:]:
                candidate = candidate.strip()
                if not candidate:
                    continue
                m = _CURRENT_PHASE_LINE.match(candidate)
                return m.group(1) if m else ""
    return ""


# ── Helpers ──────────────────────────────────────────────────────────────────


def _read_current_task(current_task_path: Path) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in current_task_path.read_text(encoding="utf-8").splitlines():
        m = _TASK_ID_LINE.match(line.strip())
        if m:
            parsed["task_id"] = m.group(1)
            continue
        m = _TASK_PATH_LINE.match(line.strip())
        if m:
            parsed["task_path"] = m.group(1)
            continue
        m = _CURRENT_TASK_STATUS_LINE.match(line.strip())
        if m:
            parsed["status"] = m.group(1)
    return parsed


def _read_all_backlog_tasks(backlog_path: Path) -> dict[str, str]:
    """Return {task_ref: status} for all tasks across all phases."""
    tasks: dict[str, str] = {}
    current_task_ref = ""
    current_status = ""

    for line in backlog_path.read_text(encoding="utf-8").splitlines():
        heading_match = _TASK_HEADING.match(line)
        if heading_match:
            if current_task_ref and current_status:
                tasks[current_task_ref] = current_status
            current_task_ref = heading_match.group(1)
            current_status = ""
            continue

        if not current_task_ref:
            continue

        status_match = _BACKLOG_STATUS.match(line)
        if status_match:
            current_status = status_match.group(1)

    if current_task_ref and current_status:
        tasks[current_task_ref] = current_status

    return tasks


def _find_packet_dir(tasks_dir: Path, task_ref: str) -> Path | None:
    """Locate a task packet, active or archived.

    `grain phase close` moves a sealed phase's packets into
    `tasks/archive/phase-N/`. Those packets still exist, so a closed phase's done
    tasks must not be reported as orphans.
    """
    if not tasks_dir.exists():
        return None

    def _matches(candidate: Path) -> bool:
        # Packets are usually `P1-T01-TASK-0001`, but some carry no TASK suffix.
        return candidate.is_dir() and (
            candidate.name == task_ref or candidate.name.startswith(task_ref + "-")
        )

    for candidate in tasks_dir.iterdir():
        if _matches(candidate):
            return candidate

    archive_dir = tasks_dir / "archive"
    if not archive_dir.is_dir():
        return None
    for phase_dir in sorted(archive_dir.iterdir()):
        if not phase_dir.is_dir():
            continue
        for candidate in phase_dir.iterdir():
            if _matches(candidate):
                return candidate
    return None


def _find_packet_by_id_or_path(
    tasks_dir: Path, root: Path, task_id: str, task_path: str
) -> Path | None:
    # Try by path first
    if task_path not in {"", "none"}:
        candidate = root / task_path
        if candidate.exists() and candidate.is_dir():
            return candidate
    # Try by scanning for TASK-#### in directory names
    if not tasks_dir.exists():
        return None
    for candidate in tasks_dir.iterdir():
        if candidate.is_dir() and task_id in candidate.name:
            return candidate
    return None


def _read_packet_status(packet_dir: Path) -> str | None:
    task_md = packet_dir / "task.md"
    if not task_md.exists():
        return None
    for line in task_md.read_text(encoding="utf-8").splitlines():
        m = _PACKET_STATUS_ALT.match(line.strip())
        if m:
            return m.group(1).lower()
        m = _PACKET_STATUS.match(line.strip())
        if m:
            return m.group(1).lower()
    return None


def _read_task_id_from_packet(packet_dir: Path) -> str | None:
    task_md = packet_dir / "task.md"
    if not task_md.exists():
        return None
    for line in task_md.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        m = _TASK_ID_LINE.match(stripped)
        if m:
            return m.group(1)
        m = _PACKET_ID_LINE.match(stripped)
        if m:
            return m.group(1)
    return None


def _update_backlog_task_status(text: str, task_ref: str, new_status: str) -> str:
    """Replace the **Status:** line under the task_ref heading with new_status."""
    lines = text.splitlines(keepends=True)
    result = []
    in_target_task = False
    status_replaced = False

    for line in lines:
        heading_match = _TASK_HEADING.match(line)
        if heading_match:
            if heading_match.group(1) == task_ref:
                in_target_task = True
                status_replaced = False
            else:
                in_target_task = False

        if in_target_task and not status_replaced:
            status_match = _BACKLOG_STATUS.match(line)
            if status_match:
                line = line.replace(status_match.group(1), new_status, 1)
                status_replaced = True

        result.append(line)

    return "".join(result)


def _clear_current_task(current_task_path: Path) -> None:
    current_task_path.write_text(
        "# Current Task\n\nTask ID: none\nTask Path: none\nStatus: idle\n",
        encoding="utf-8",
    )
