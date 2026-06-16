# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Context domain model for Phase 4 context assembly.

Provides PacketFile, PacketSourceSet, discover_packet_files(), and
select_canonical_docs() as the foundational layer for context selection
and bundle assembly.
"""

from __future__ import annotations

from dataclasses import dataclass, field  # noqa: F401 (field used by ContextBundle)
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grain.domain.documents import DocumentRecord, DocumentRegistry

@dataclass
class SourceStats:
    """Line count and selection metadata for one source file."""

    path: str
    lines: int
    selection_method: str  # packet | graph_traced | glob_only | canonical | working
    graph_depth: int  # hops from packet files via graph; -1 when not applicable


@dataclass
class ContextStats:
    """Aggregate statistics for one context bundle build."""

    total_sources: int
    total_lines: int
    packet_sources: int
    graph_traced_sources: int
    glob_only_sources: int
    canonical_sources: int
    working_sources: int
    per_file: list[SourceStats]


PACKET_FILENAMES: tuple[str, ...] = (
    "task.md",
    "context.md",
    "plan.md",
    "deliverable_spec.md",
    "results.md",
    "handoff.md",
)

_REQUIRED_FILENAMES: frozenset[str] = frozenset(
    {"task.md", "context.md", "plan.md", "deliverable_spec.md"}
)


@dataclass
class PacketFile:
    """Represents one packet-local file and its presence on disk."""

    name: str
    path: Path
    present: bool


@dataclass
class PacketSourceSet:
    """The set of packet-local file sources discovered for one task."""

    task_id: str
    packet_dir: Path
    files: list[PacketFile]

    def present_files(self) -> list[PacketFile]:
        """Return only files that exist on disk."""
        return [f for f in self.files if f.present]

    def required_files(self) -> list[PacketFile]:
        """Return the four required packet files (present or absent)."""
        return [f for f in self.files if f.name in _REQUIRED_FILENAMES]


@dataclass
class ContextBundle:
    """Structured context output assembled for one task packet.

    The bundle keeps packet-local files alongside selected canonical and
    optional working documents, plus export metadata for later serialization.
    """

    task_id: str
    packet_dir: Path
    packet_files: list[PacketFile]
    selected_canonical_docs: list["DocumentRecord"]
    selected_working_docs: list["DocumentRecord"] = field(default_factory=list)
    export_metadata: dict[str, object] = field(default_factory=dict)


def select_canonical_docs(
    registry: "DocumentRegistry",
    context_tags: set[str],
) -> "list[DocumentRecord]":
    """Return canonical-layer docs whose read_when list intersects context_tags.

    Empty context_tags returns an empty list — callers must opt in explicitly.
    Only canonical-layer records are returned; working and runtime docs are excluded.
    """
    if not context_tags:
        return []
    return [
        record
        for record in registry.by_layer("canonical")
        if set(record.read_when) & context_tags
    ]


def select_working_docs(
    registry: "DocumentRegistry",
    context_tags: set[str],
    include_working_docs: bool = False,
) -> "list[DocumentRecord]":
    """Return working-layer docs only when explicitly opted in.

    Default behavior keeps working docs out of packet context. When opt-in is
    enabled, selection uses the same read_when intersection rule as canonical
    docs.
    """
    if not include_working_docs or not context_tags:
        return []
    return [
        record
        for record in registry.by_layer("working")
        if set(record.read_when) & context_tags
    ]


def discover_packet_files(packet_dir: Path) -> list[PacketFile]:
    """Return a PacketFile entry for each known packet filename under packet_dir.

    Reports presence without raising — callers decide how to handle absent files.
    """
    return [
        PacketFile(
            name=name,
            path=packet_dir / name,
            present=(packet_dir / name).exists(),
        )
        for name in PACKET_FILENAMES
    ]
