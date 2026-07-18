# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""grain capture — a lightweight feature-request / quick-edit inbox.

Captures land in ``docs/working/inbox.md`` (a markdown table) as ``CAP-####`` rows at status
``new`` — pre-backlog, unphased, zero-friction. ``promote`` turns one into a backlog ``draft``
entry plus a task packet (via the same ``create_packet_directory`` that ``task create`` uses);
``drop`` shelves it. No Grain packet state is involved — the inbox is the front door, not the
lifecycle.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from grain.services import task_service
from grain.services.intake_service import _next_task_num

_INBOX_REL = Path("docs/working/inbox.md")
_BACKLOG_REL = Path("docs/working/backlog.md")
_CAP_RE = re.compile(r"CAP-(\d+)")
VALID_KINDS = ("feature", "edit", "chore", "bug", "refactor")
_SIMPLE_KINDS = frozenset({"edit", "chore", "bug"})
VALID_STATUSES = ("new", "promoted", "dropped")

_HEADER = """# Inbox

Captured feature-requests and quick-edits awaiting triage. `grain capture promote <id> --phase N`
turns one into a backlog draft entry + a task packet. Pre-backlog and unphased — not a lifecycle.

| ID | Status | Kind | Title | Note | Captured | Task |
|----|--------|------|-------|------|----------|------|
"""


class CaptureError(Exception):
    """A capture operation failed (bad id, bad kind, already promoted, …)."""


@dataclass(frozen=True)
class Capture:
    id: str
    status: str
    kind: str
    title: str
    note: str
    captured: str
    task: str


@dataclass(frozen=True)
class PromoteResult:
    cap_id: str
    task_id: str
    packet_dir: str
    phase: int
    task_num: int
    simple: bool


def _inbox_path(root: Path) -> Path:
    return root / _INBOX_REL


def _cell(value: str) -> str:
    """Keep a table cell single-line and pipe-safe (a raw pipe would break the table)."""
    return value.replace("|", "/").replace("\n", " ").strip()


def _read_rows(root: Path) -> list[Capture]:
    path = _inbox_path(root)
    if not path.exists():
        return []
    rows: list[Capture] = []
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped.startswith("| CAP-"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 7:
            continue
        rows.append(Capture(cells[0], cells[1], cells[2], cells[3], cells[4], cells[5], cells[6]))
    return rows


def next_cap_id(root: Path) -> str:
    path = _inbox_path(root)
    max_n = 0
    if path.exists():
        for match in _CAP_RE.finditer(path.read_text()):
            max_n = max(max_n, int(match.group(1)))
    return f"CAP-{max_n + 1:04d}"


def capture(
    root: Path, title: str, note: str = "", kind: str = "feature", today: str | None = None
) -> str:
    """Append a capture and return its ``CAP-####`` id."""
    title = title.strip()
    if not title:
        raise CaptureError("capture requires a non-empty title")
    if kind not in VALID_KINDS:
        raise CaptureError(f"invalid kind {kind!r}; expected one of {', '.join(VALID_KINDS)}")
    cap_id = next_cap_id(root)
    when = today or date.today().isoformat()
    path = _inbox_path(root)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_HEADER)
    row = f"| {cap_id} | new | {kind} | {_cell(title)} | {_cell(note)} | {when} |  |\n"
    with path.open("a") as handle:
        handle.write(row)
    return cap_id


def list_captures(root: Path, status: str | None = None) -> list[Capture]:
    rows = _read_rows(root)
    return [r for r in rows if r.status == status] if status else rows


def _get(root: Path, cap_id: str) -> Capture:
    for row in _read_rows(root):
        if row.id == cap_id:
            return row
    raise CaptureError(f"capture {cap_id} not found")


def _rewrite_row(root: Path, cap_id: str, *, status: str, task: str | None = None) -> None:
    path = _inbox_path(root)
    out: list[str] = []
    for line in path.read_text().splitlines(keepends=True):
        if line.strip().startswith(f"| {cap_id} "):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            cells[1] = status
            if task is not None:
                cells[6] = task
            out.append("| " + " | ".join(cells) + " |\n")
        else:
            out.append(line)
    path.write_text("".join(out))


def drop(root: Path, cap_id: str) -> None:
    cap = _get(root, cap_id)
    if cap.status == "promoted":
        raise CaptureError(f"{cap_id} is already promoted; cannot drop")
    _rewrite_row(root, cap_id, status="dropped")


def _insert_backlog_entry(
    root: Path, phase: int, task_num: int, title: str, task_id: str, depends_on: str | None
) -> None:
    """Add a `### PN-TNN — Title` draft entry under `## Phase N` (append a phase if absent)."""
    path = root / _BACKLOG_REL
    ref = f"P{phase}-T{task_num:02d}"
    entry_lines = [
        f"\n### {ref} — {title} · {task_id}\n",
        "- **Status:** draft\n",
        f"- **Description:** Promoted from the capture inbox. {title}\n",
    ]
    if depends_on:
        entry_lines.append(f"- **Dependencies:** {depends_on}\n")
    entry = "".join(entry_lines)
    if not path.exists():
        return  # no backlog to update; the packet still exists
    text = path.read_text()
    heading = re.compile(rf"^##\s+(?:\d+\.\s+)?Phase\s+{phase}\b.*$", re.MULTILINE)
    match = heading.search(text)
    if match is None:
        path.write_text(text.rstrip() + f"\n\n## Phase {phase} — (opened by capture)\n{entry}")
        return
    next_heading = re.compile(r"^##\s", re.MULTILINE).search(text, match.end())
    insert_at = next_heading.start() if next_heading else len(text)
    path.write_text(text[:insert_at].rstrip() + "\n" + entry + "\n\n" + text[insert_at:])


def promote(
    root: Path,
    cap_id: str,
    phase: int,
    task_num: int | None = None,
    simple: bool | None = None,
    depends_on: str | None = None,
) -> PromoteResult:
    """Promote a capture: scaffold a packet + a backlog draft entry; mark it promoted."""
    cap = _get(root, cap_id)
    if cap.status == "promoted":
        raise CaptureError(f"{cap_id} is already promoted (→ {cap.task or '?'})")
    if cap.status == "dropped":
        raise CaptureError(f"{cap_id} was dropped; re-capture it to promote")
    tier = simple if simple is not None else (cap.kind in _SIMPLE_KINDS)
    num = task_num if task_num is not None else _next_task_num(root, phase)
    result = task_service.create_packet_directory(root, phase, num, title=cap.title, simple=tier)
    if not result.ok:
        raise CaptureError(f"packet scaffold failed: {'; '.join(result.errors) or 'unknown error'}")
    task_id = result.task_id or ""
    _insert_backlog_entry(root, phase, num, cap.title, task_id, depends_on)
    _rewrite_row(root, cap_id, status="promoted", task=task_id)
    packet_dir = result.files_created[0] if result.files_created else ""
    return PromoteResult(cap_id, task_id, packet_dir, phase, num, tier)
