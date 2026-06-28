# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""Domain models for grain suggest — file-backed, proposal-only suggestions."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Proposal id format: SUG-YYYYMMDD-NNN (date of generation + 3-digit daily seq).
PROPOSAL_ID_PATTERN = re.compile(r"^SUG-(\d{8})-(\d{3})$")

# Suggestion kinds enumerated by suggest_spec section 2.
KIND_PICK_UP = "pick-up"
KIND_NEW_TASK = "new-task"
VALID_KINDS: frozenset[str] = frozenset({KIND_PICK_UP, KIND_NEW_TASK})

# Proposal lifecycle statuses (suggest_spec section 6 lifecycle).
STATUS_PENDING = "pending"
STATUS_ACCEPTED = "accepted"
STATUS_DISMISSED = "dismissed"
STATUS_EXPIRED = "expired"
VALID_STATUSES: frozenset[str] = frozenset(
    {STATUS_PENDING, STATUS_ACCEPTED, STATUS_DISMISSED, STATUS_EXPIRED}
)


@dataclass
class SuggestionProposal:
    """A single file-backed suggestion proposal.

    Persisted as docs/working/proposals/SUG-YYYYMMDD-NNN.md. Generation is
    deterministic; nothing is acted on without an explicit accept/dismiss.
    """

    id: str
    kind: str                       # "pick-up" | "new-task"
    title: str                      # short human label (task title or objective)
    rationale: str = ""
    signal: str = ""                # one-line signal label (e.g. "Ready task in active phase")
    signal_ref: str = ""            # traceable key: task_ref / OQ id / tooling row / commit sha
    status: str = STATUS_PENDING
    created_at: str = ""            # YYYY-MM-DD
    source_signals: list[str] = field(default_factory=list)
    # pick-up payload
    task_ref: str = ""              # P<N>-T<NN>
    task_id: str = ""               # TASK-####
    phase: str = ""
    # new-task payload
    objective: str = ""
    suggested_phase: str = ""


def parse_proposal_id(value: str) -> tuple[str, int] | None:
    """Return (YYYYMMDD, seq) for a valid SUG id, else None."""
    m = PROPOSAL_ID_PATTERN.match(value.strip())
    if not m:
        return None
    return m.group(1), int(m.group(2))
