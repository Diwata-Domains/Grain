"""Tests for optional working doc selection — domain and service layer."""

import yaml

from grain.domain.context import select_working_docs
from grain.domain.documents import build_registry, DocumentRecord
from grain.services.context_service import select_working_docs_for_packet
from grain.services.task_service import create_packet_directory


def _make_registry(working_entries: list[dict], extra_entries: dict | None = None):
    """Build a DocumentRegistry from minimal manifest data."""
    manifest: dict = {"canonical": [], "working": working_entries, "runtime": []}
    if extra_entries:
        manifest.update(extra_entries)
    return build_registry(manifest)


def _write_manifest(repo_root, manifest_dict):
    manifest_path = repo_root / "docs" / "runtime" / "docs_manifest.yaml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(yaml.dump(manifest_dict))


def test_select_working_docs_default_excluded():
    """Working docs stay excluded unless opt-in is enabled."""
    registry = _make_registry(
        [
            {"id": "backlog", "path": "docs/working/backlog.md",
             "purpose": "", "authority": "secondary", "editable_by_agents": True,
             "read_when": ["selecting_tasks"]},
        ]
    )
    assert select_working_docs(registry, {"selecting_tasks"}) == []


def test_select_working_docs_opt_in_matches_tags():
    """Opt-in selection returns working docs whose read_when intersects tags."""
    registry = _make_registry(
        [
            {"id": "backlog", "path": "docs/working/backlog.md",
             "purpose": "", "authority": "secondary", "editable_by_agents": True,
             "read_when": ["selecting_tasks", "planning_next_packet"]},
            {"id": "current_focus", "path": "docs/working/current_focus.md",
             "purpose": "", "authority": "secondary", "editable_by_agents": True,
             "read_when": ["resuming_work"]},
        ]
    )
    result = select_working_docs(
        registry,
        {"planning_next_packet"},
        include_working_docs=True,
    )
    assert len(result) == 1
    assert result[0].id == "backlog"


def test_select_working_docs_returns_document_records():
    """Returned items are DocumentRecord instances."""
    registry = _make_registry(
        [
            {"id": "open_questions", "path": "docs/working/open_questions.md",
             "purpose": "", "authority": "informational", "editable_by_agents": True,
             "read_when": ["encountering_blockers"]},
        ]
    )
    result = select_working_docs(
        registry,
        {"encountering_blockers"},
        include_working_docs=True,
    )
    assert all(isinstance(r, DocumentRecord) for r in result)


def test_select_working_docs_no_matching_tag():
    """Opt-in selection still respects tag filtering."""
    registry = _make_registry(
        [
            {"id": "backlog", "path": "docs/working/backlog.md",
             "purpose": "", "authority": "secondary", "editable_by_agents": True,
             "read_when": ["selecting_tasks"]},
        ]
    )
    result = select_working_docs(
        registry,
        {"resuming_work"},
        include_working_docs=True,
    )
    assert result == []


def test_select_working_docs_for_packet_no_manifest(packet_repo):
    """Returns ok=False when manifest is absent."""
    create_packet_directory(packet_repo, phase=4, task_num=3)
    result, docs = select_working_docs_for_packet(
        packet_repo,
        "TASK-0001",
        {"selecting_tasks"},
        include_working_docs=True,
    )
    assert result.ok is False
    assert docs == []


def test_select_working_docs_for_packet_not_found(packet_repo):
    """Returns ok=False when packet does not exist."""
    _write_manifest(
        packet_repo,
        {
            "canonical": [],
            "working": [
                {"id": "backlog", "path": "docs/working/backlog.md",
                 "purpose": "", "authority": "secondary", "editable_by_agents": True,
                 "read_when": ["selecting_tasks"]},
            ],
            "runtime": [],
            "tasks": {},
            "rules": {},
        },
    )
    result, docs = select_working_docs_for_packet(
        packet_repo,
        "TASK-9999",
        {"selecting_tasks"},
        include_working_docs=True,
    )
    assert result.ok is False
    assert docs == []


def test_select_working_docs_for_packet_success(packet_repo):
    """Returns ok=True and matching working docs when opt-in is enabled."""
    _write_manifest(
        packet_repo,
        {
            "canonical": [],
            "working": [
                {"id": "backlog", "path": "docs/working/backlog.md",
                 "purpose": "Task inventory", "authority": "secondary",
                 "editable_by_agents": True, "read_when": ["selecting_tasks"]},
                {"id": "current_focus", "path": "docs/working/current_focus.md",
                 "purpose": "Active focus", "authority": "secondary",
                 "editable_by_agents": True, "read_when": ["resuming_work"]},
            ],
            "runtime": [],
            "tasks": {},
            "rules": {},
        },
    )
    create_packet_directory(packet_repo, phase=4, task_num=3)

    result, docs = select_working_docs_for_packet(
        packet_repo,
        "TASK-0001",
        {"selecting_tasks"},
        include_working_docs=True,
    )
    assert result.ok is True
    assert len(docs) == 1
    assert docs[0].id == "backlog"
