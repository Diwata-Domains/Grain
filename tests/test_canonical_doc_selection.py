"""Tests for canonical doc selection — domain and service layer.

Covers: select_canonical_docs, select_canonical_docs_for_packet.
"""

import yaml

from forge.domain.context import select_canonical_docs
from forge.domain.documents import build_registry, DocumentRecord
from forge.services.context_service import select_canonical_docs_for_packet
from forge.services.task_service import create_packet_directory


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_registry(canonical_entries: list[dict], extra_entries: dict | None = None):
    """Build a DocumentRegistry from minimal manifest data."""
    manifest: dict = {"canonical": canonical_entries, "working": [], "runtime": []}
    if extra_entries:
        manifest.update(extra_entries)
    return build_registry(manifest)


# ---------------------------------------------------------------------------
# select_canonical_docs — pure domain
# ---------------------------------------------------------------------------


def test_select_canonical_docs_empty_tags():
    """Empty context_tags always returns an empty list."""
    registry = _make_registry([
        {"id": "architecture", "path": "docs/canonical/architecture.md",
         "purpose": "", "authority": "highest", "editable_by_agents": False,
         "read_when": ["designing_features"]},
    ])
    assert select_canonical_docs(registry, set()) == []


def test_select_canonical_docs_matching_tag():
    """Returns doc whose read_when contains the given tag."""
    registry = _make_registry([
        {"id": "cli_spec", "path": "docs/canonical/cli_spec.md",
         "purpose": "", "authority": "highest", "editable_by_agents": False,
         "read_when": ["implementing_cli", "writing_tests_for_cli"]},
        {"id": "architecture", "path": "docs/canonical/architecture.md",
         "purpose": "", "authority": "highest", "editable_by_agents": False,
         "read_when": ["designing_features"]},
    ])
    result = select_canonical_docs(registry, {"implementing_cli"})
    assert len(result) == 1
    assert result[0].id == "cli_spec"


def test_select_canonical_docs_no_matching_tag():
    """Returns empty list when no doc matches the given tags."""
    registry = _make_registry([
        {"id": "architecture", "path": "docs/canonical/architecture.md",
         "purpose": "", "authority": "highest", "editable_by_agents": False,
         "read_when": ["designing_features"]},
    ])
    result = select_canonical_docs(registry, {"nonexistent_tag"})
    assert result == []


def test_select_canonical_docs_multiple_tags_match_multiple_docs():
    """Multiple tags can select multiple docs simultaneously."""
    registry = _make_registry([
        {"id": "cli_spec", "path": "docs/canonical/cli_spec.md",
         "purpose": "", "authority": "highest", "editable_by_agents": False,
         "read_when": ["implementing_cli"]},
        {"id": "workflow_spec", "path": "docs/canonical/workflow_spec.md",
         "purpose": "", "authority": "highest", "editable_by_agents": False,
         "read_when": ["creating_packets"]},
    ])
    result = select_canonical_docs(registry, {"implementing_cli", "creating_packets"})
    ids = {r.id for r in result}
    assert ids == {"cli_spec", "workflow_spec"}


def test_select_canonical_docs_only_canonical_layer():
    """Working and runtime docs are never returned."""
    manifest = {
        "canonical": [
            {"id": "architecture", "path": "docs/canonical/architecture.md",
             "purpose": "", "authority": "highest", "editable_by_agents": False,
             "read_when": ["always"]},
        ],
        "working": [
            {"id": "backlog", "path": "docs/working/backlog.md",
             "purpose": "", "authority": "secondary", "editable_by_agents": True,
             "read_when": ["always"]},
        ],
        "runtime": [
            {"id": "project_rules", "path": "docs/runtime/PROJECT_RULES.md",
             "purpose": "", "authority": "highest_runtime", "editable_by_agents": False,
             "read_when": ["always"]},
        ],
    }
    registry = build_registry(manifest)
    result = select_canonical_docs(registry, {"always"})
    assert len(result) == 1
    assert result[0].id == "architecture"


def test_select_canonical_docs_returns_document_records():
    """Returned items are DocumentRecord instances."""
    registry = _make_registry([
        {"id": "data_contracts", "path": "docs/canonical/data_contracts.md",
         "purpose": "schemas", "authority": "highest", "editable_by_agents": False,
         "read_when": ["implementing_validation"]},
    ])
    result = select_canonical_docs(registry, {"implementing_validation"})
    assert all(isinstance(r, DocumentRecord) for r in result)


# ---------------------------------------------------------------------------
# select_canonical_docs_for_packet — service layer
# ---------------------------------------------------------------------------


def _write_manifest(repo_root, manifest_dict):
    manifest_path = repo_root / "docs" / "runtime" / "docs_manifest.yaml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(yaml.dump(manifest_dict))


def test_select_canonical_docs_for_packet_no_manifest(packet_repo):
    """Returns ok=False when manifest is absent."""
    create_packet_directory(packet_repo, phase=4, task_num=2)
    result, docs = select_canonical_docs_for_packet(packet_repo, "TASK-0001", {"always"})
    assert result.ok is False
    assert docs == []


def test_select_canonical_docs_for_packet_not_found(packet_repo):
    """Returns ok=False when packet does not exist."""
    _write_manifest(packet_repo, {
        "canonical": [
            {"id": "architecture", "path": "docs/canonical/architecture.md",
             "purpose": "", "authority": "highest", "editable_by_agents": False,
             "read_when": ["designing_features"]},
        ],
        "working": [], "runtime": [], "tasks": {}, "rules": {},
    })
    result, docs = select_canonical_docs_for_packet(packet_repo, "TASK-9999", {"designing_features"})
    assert result.ok is False
    assert docs == []


def test_select_canonical_docs_for_packet_success(packet_repo):
    """Returns ok=True and matching canonical docs for an existing packet."""
    _write_manifest(packet_repo, {
        "canonical": [
            {"id": "cli_spec", "path": "docs/canonical/cli_spec.md",
             "purpose": "CLI contracts", "authority": "highest",
             "editable_by_agents": False, "read_when": ["implementing_cli"]},
            {"id": "architecture", "path": "docs/canonical/architecture.md",
             "purpose": "Architecture", "authority": "highest",
             "editable_by_agents": False, "read_when": ["designing_features"]},
        ],
        "working": [], "runtime": [], "tasks": {}, "rules": {},
    })
    create_packet_directory(packet_repo, phase=4, task_num=2)

    result, docs = select_canonical_docs_for_packet(
        packet_repo, "TASK-0001", {"implementing_cli"}
    )
    assert result.ok is True
    assert len(docs) == 1
    assert docs[0].id == "cli_spec"
