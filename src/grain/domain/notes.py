# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Domain model for tooling notes — the queryable friction inbox.

A note is one row in docs/working/tooling_notes.md. The canonical table schema
is::

    | ID | Date | Type | Command | Observation | Severity | Status |

Legacy rows written before IDs existed (six columns, no leading ``ID``) are
still parseable; they are assigned a synthesized ID on read so the inbox stays
backward-compatible without dropping data.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Canonical column headers for the structured notes table.
TABLE_HEADER = "| ID | Date | Type | Command | Observation | Severity | Status |"
TABLE_SEP = "|----|------|------|---------|-------------|----------|--------|"

# Allowed enums (the CLI mirrors these via click.Choice).
NOTE_TYPES: frozenset[str] = frozenset({"friction", "bug", "observation"})
NOTE_STATUSES: frozenset[str] = frozenset(
    {"open", "closed", "resolved", "reported", "published"}
)
NOTE_SEVERITIES: frozenset[str] = frozenset({"low", "medium", "high"})

# Open notes of these types surface as docs-audit findings.
ACTIONABLE_TYPES: frozenset[str] = frozenset({"bug", "friction"})

# A note is "open" (not yet triaged away) when its status is one of these.
OPEN_STATUSES: frozenset[str] = frozenset({"open"})

# Structured row with a leading numeric ID (7 cells).
_ROW_WITH_ID_RE = re.compile(
    r"^\|\s*(\d+)\s*\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|"
    r"\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|"
)
# Legacy row without an ID (6 cells), e.g. rows written by the old stub.
_ROW_LEGACY_RE = re.compile(
    r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*([^|]*)\|\s*([^|]*)\|"
    r"\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|"
)


@dataclass
class Note:
    """A single tooling-note row."""

    id: int
    created_at: str
    type: str
    command: str
    body: str
    severity: str
    status: str

    def to_row(self) -> str:
        """Render this note as a human-readable markdown table row."""
        return (
            f"| {self.id} | {self.created_at} | {self.type} | "
            f"{self.command or '—'} | {self.body} | {self.severity} | {self.status} |"
        )

    def to_dict(self) -> dict:
        """Return a JSON-serializable mapping for CLI output."""
        return {
            "id": self.id,
            "created_at": self.created_at,
            "type": self.type,
            "command": self.command,
            "body": self.body,
            "severity": self.severity,
            "status": self.status,
        }


def parse_note_line(line: str, fallback_id: int) -> Note | None:
    """Parse a single table line into a Note, or None if it is not a data row.

    ``fallback_id`` is used for legacy (un-IDed) rows so they remain
    addressable. Header/separator lines return None.
    """
    stripped = line.strip()
    if not stripped.startswith("|"):
        return None

    m = _ROW_WITH_ID_RE.match(line)
    if m:
        cells = [c.strip() for c in m.groups()]
        # Skip the header row (its first cell is the literal "ID").
        if cells[0].lower() == "id":
            return None
        return Note(
            id=int(cells[0]),
            created_at=cells[1],
            type=cells[2].lower(),
            command="" if cells[3] in ("", "—") else cells[3],
            body=cells[4],
            severity=cells[5].lower(),
            status=cells[6].lower(),
        )

    m = _ROW_LEGACY_RE.match(line)
    if m:
        cells = [c.strip() for c in m.groups()]
        return Note(
            id=fallback_id,
            created_at=cells[0],
            type=cells[1].lower(),
            command="" if cells[2] in ("", "—") else cells[2],
            body=cells[3],
            severity=cells[4].lower(),
            status=cells[5].lower(),
        )

    return None
