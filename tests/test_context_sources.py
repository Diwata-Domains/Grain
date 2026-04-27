"""Tests for packet context source discovery — domain and service layer.

Covers: PacketFile, PacketSourceSet, discover_packet_files, discover_packet_sources.
"""

from pathlib import Path

from grain.domain.context import (
    PACKET_FILENAMES,
    PacketFile,
    PacketSourceSet,
    discover_packet_files,
)
from grain.services.context_service import discover_packet_sources
from grain.services.task_service import create_packet_directory


# ---------------------------------------------------------------------------
# discover_packet_files — pure domain
# ---------------------------------------------------------------------------


def test_discover_packet_files_all_absent(tmp_path):
    """All 6 files are reported as absent for an empty directory."""
    packet_dir = tmp_path / "P4-T01-TASK-0001"
    packet_dir.mkdir()

    files = discover_packet_files(packet_dir)
    assert len(files) == 6
    assert all(isinstance(f, PacketFile) for f in files)
    assert all(not f.present for f in files)


def test_discover_packet_files_partial_presence(tmp_path):
    """Files that exist on disk are reported as present."""
    packet_dir = tmp_path / "P4-T01-TASK-0001"
    packet_dir.mkdir()
    (packet_dir / "task.md").write_text("# Task\n")
    (packet_dir / "results.md").write_text("# Results\n")

    files = discover_packet_files(packet_dir)
    by_name = {f.name: f for f in files}

    assert by_name["task.md"].present is True
    assert by_name["results.md"].present is True
    assert by_name["context.md"].present is False
    assert by_name["handoff.md"].present is False


def test_discover_packet_files_returns_all_known_filenames(tmp_path):
    """discover_packet_files returns entries for every name in PACKET_FILENAMES."""
    packet_dir = tmp_path / "P4-T01-TASK-0001"
    packet_dir.mkdir()

    files = discover_packet_files(packet_dir)
    returned_names = {f.name for f in files}
    assert returned_names == set(PACKET_FILENAMES)


# ---------------------------------------------------------------------------
# PacketSourceSet helpers
# ---------------------------------------------------------------------------


def test_packet_source_set_present_files():
    """present_files() returns only files where present=True."""
    base = Path("/fake/tasks/P4-T01-TASK-0001")
    files = [
        PacketFile(name="task.md", path=base / "task.md", present=True),
        PacketFile(name="context.md", path=base / "context.md", present=True),
        PacketFile(name="results.md", path=base / "results.md", present=False),
    ]
    source_set = PacketSourceSet(task_id="TASK-0001", packet_dir=base, files=files)
    present = source_set.present_files()
    assert len(present) == 2
    assert all(f.present for f in present)


def test_packet_source_set_required_files():
    """required_files() returns the 4 required packet files regardless of presence."""
    base = Path("/fake/tasks/P4-T01-TASK-0001")
    files = [
        PacketFile(name="task.md", path=base / "task.md", present=True),
        PacketFile(name="context.md", path=base / "context.md", present=False),
        PacketFile(name="plan.md", path=base / "plan.md", present=False),
        PacketFile(name="deliverable_spec.md", path=base / "deliverable_spec.md", present=False),
        PacketFile(name="results.md", path=base / "results.md", present=False),
        PacketFile(name="handoff.md", path=base / "handoff.md", present=False),
    ]
    source_set = PacketSourceSet(task_id="TASK-0001", packet_dir=base, files=files)
    required = source_set.required_files()
    required_names = {f.name for f in required}
    assert required_names == {"task.md", "context.md", "plan.md", "deliverable_spec.md"}


# ---------------------------------------------------------------------------
# discover_packet_sources — service layer
# ---------------------------------------------------------------------------


def test_discover_packet_sources_not_found(packet_repo):
    """Returns ok=False and None when packet does not exist."""
    result, source_set = discover_packet_sources(packet_repo, "TASK-9999")
    assert result.ok is False
    assert source_set is None
    assert any("not found" in e for e in result.errors)


def test_discover_packet_sources_new_packet(packet_repo):
    """Returns ok=True and a PacketSourceSet for a freshly created packet."""
    create_packet_directory(packet_repo, phase=4, task_num=1)

    result, source_set = discover_packet_sources(packet_repo, "TASK-0001")
    assert result.ok is True
    assert source_set is not None
    assert source_set.task_id == "TASK-0001"
    assert len(source_set.files) == 6


def test_discover_packet_sources_required_files_present(packet_repo):
    """The 4 required files are present after packet creation."""
    create_packet_directory(packet_repo, phase=4, task_num=1)

    _, source_set = discover_packet_sources(packet_repo, "TASK-0001")
    required = source_set.required_files()
    assert all(f.present for f in required)


def test_discover_packet_sources_optional_files_absent(packet_repo):
    """results.md and handoff.md are absent for a newly created packet."""
    create_packet_directory(packet_repo, phase=4, task_num=1)

    _, source_set = discover_packet_sources(packet_repo, "TASK-0001")
    by_name = {f.name: f for f in source_set.files}
    assert by_name["results.md"].present is False
    assert by_name["handoff.md"].present is False
