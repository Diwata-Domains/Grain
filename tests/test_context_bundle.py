"""Tests for the context bundle domain model."""

from pathlib import Path

from grain.domain.context import ContextBundle, PacketFile
from grain.domain.documents import DocumentRecord


def test_context_bundle_required_fields():
    """ContextBundle stores packet files, canonical docs, working docs, and metadata."""
    base = Path("/fake/tasks/P4-T04-TASK-0035")
    packet_files = [
        PacketFile(name="task.md", path=base / "task.md", present=True),
        PacketFile(name="context.md", path=base / "context.md", present=True),
    ]
    canonical_docs = [
        DocumentRecord(
            id="architecture",
            path="docs/canonical/architecture.md",
            layer="canonical",
            purpose="Architecture",
            authority="highest",
            editable_by_agents=False,
            read_when=["designing_features"],
        )
    ]

    bundle = ContextBundle(
        task_id="TASK-0001",
        packet_dir=base,
        packet_files=packet_files,
        selected_canonical_docs=canonical_docs,
    )

    assert bundle.task_id == "TASK-0001"
    assert bundle.packet_dir == base
    assert bundle.packet_files == packet_files
    assert bundle.selected_canonical_docs == canonical_docs
    assert bundle.selected_working_docs == []
    assert bundle.export_metadata == {}


def test_context_bundle_can_store_working_docs_and_metadata():
    """ContextBundle accepts optional working docs and export metadata."""
    base = Path("/fake/tasks/P4-T04-TASK-0035")
    working_docs = [
        DocumentRecord(
            id="backlog",
            path="docs/working/backlog.md",
            layer="working",
            purpose="Backlog",
            authority="secondary",
            editable_by_agents=True,
            read_when=["selecting_tasks"],
        )
    ]

    bundle = ContextBundle(
        task_id="TASK-0001",
        packet_dir=base,
        packet_files=[],
        selected_canonical_docs=[],
        selected_working_docs=working_docs,
        export_metadata={"generated_at": "2026-04-04T12:00:00Z", "sources": []},
    )

    assert bundle.selected_working_docs == working_docs
    assert bundle.export_metadata["generated_at"] == "2026-04-04T12:00:00Z"
    assert bundle.export_metadata["sources"] == []
