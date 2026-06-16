# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

import re
from dataclasses import dataclass
from pathlib import Path

TASK_ID_PATTERN = re.compile(r"TASK-(\d{4})")

VALID_STATUSES: frozenset[str] = frozenset(
    {"draft", "ready", "in_progress", "blocked", "review", "needs_fix", "done"}
)

ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    "draft": frozenset({"ready"}),
    "ready": frozenset({"in_progress"}),
    "in_progress": frozenset({"blocked", "review"}),
    "blocked": frozenset({"draft", "ready"}),
    "review": frozenset({"in_progress", "needs_fix", "done"}),
    "needs_fix": frozenset({"in_progress", "blocked"}),
    "done": frozenset(),
}

_METADATA_LINE = re.compile(r"-\s+\*\*(.+?):\*\*\s*(.*)")
_STATUS_LINE = re.compile(r"(-\s+\*\*Status:\*\*\s*)(\S+)")
_METADATA_KEY_ALIASES: dict[str, str] = {
    "primary adapter": "primary_adapter",
    "secondary adapters": "secondary_adapters",
}


@dataclass
class PacketRecord:
    id: str
    status: str
    phase: str
    path: Path


def next_task_id(tasks_root: Path) -> str:
    """Return the next available TASK-#### ID by scanning active and archived packet dirs."""
    if not tasks_root.exists():
        return "TASK-0001"

    numbers = []
    for entry in tasks_root.rglob("*"):
        if entry.is_dir():
            match = TASK_ID_PATTERN.search(entry.name)
            if match:
                numbers.append(int(match.group(1)))

    if not numbers:
        return "TASK-0001"

    return f"TASK-{max(numbers) + 1:04d}"


def parse_task_metadata(task_md_path: Path) -> dict[str, str]:
    """Parse the ## Metadata block from a task.md file.

    Returns a dict of lowercased field names to their string values.
    Returns an empty dict if no metadata block is found.
    Raises FileNotFoundError if the file does not exist.
    """
    text = task_md_path.read_text(encoding="utf-8")
    in_metadata = False
    metadata: dict[str, str] = {}

    for line in text.splitlines():
        if line.strip() == "## Metadata":
            in_metadata = True
            continue
        if in_metadata:
            if line.startswith("##"):
                break
            match = _METADATA_LINE.match(line)
            if match:
                key = match.group(1).strip().lower()
                key = _METADATA_KEY_ALIASES.get(key, key)
                value = match.group(2).strip()
                metadata[key] = value

    return metadata


def read_packet_record(packet_dir: Path) -> "PacketRecord":
    """Read and return a PacketRecord from a packet directory."""
    metadata = parse_task_metadata(packet_dir / "task.md")
    return PacketRecord(
        id=metadata.get("id", ""),
        status=metadata.get("status", ""),
        phase=metadata.get("phase", ""),
        path=packet_dir,
    )


def find_packet_dir(tasks_root: Path, task_id: str) -> "Path | None":
    """Return the packet directory whose name contains task_id, or None."""
    if not tasks_root.exists():
        return None
    for entry in tasks_root.iterdir():
        if entry.is_dir() and task_id in entry.name:
            return entry
    return None


def write_packet_status(packet_dir: Path, new_status: str) -> None:
    """Update the Status field in task.md for the given packet directory.

    Only the Status line in the ## Metadata block is modified.
    """
    task_md = packet_dir / "task.md"
    text = task_md.read_text(encoding="utf-8")
    updated = _STATUS_LINE.sub(lambda m: f"{m.group(1)}{new_status}", text, count=1)
    task_md.write_text(updated, encoding="utf-8")
