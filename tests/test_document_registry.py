"""Tests for the document registry model (domain/documents.py)."""

import pytest

from forge.domain.documents import DocumentRecord, DocumentRegistry, build_registry


def _manifest_with_entries() -> dict:
    return {
        "canonical": [
            {
                "id": "architecture",
                "path": "docs/canonical/architecture.md",
                "purpose": "Defines system structure",
                "authority": "highest",
                "editable_by_agents": False,
                "read_when": ["designing_features"],
            }
        ],
        "working": [
            {
                "id": "backlog",
                "path": "docs/working/backlog.md",
                "purpose": "Task inventory",
                "authority": "secondary",
                "editable_by_agents": True,
                "read_when": ["selecting_tasks"],
            }
        ],
        "runtime": [
            {
                "id": "project_rules",
                "path": "docs/runtime/PROJECT_RULES.md",
                "purpose": "Global rules",
                "authority": "highest_runtime",
                "editable_by_agents": False,
                "read_when": ["always"],
            }
        ],
    }


def test_build_registry_returns_registry():
    registry = build_registry(_manifest_with_entries())
    assert isinstance(registry, DocumentRegistry)


def test_all_returns_all_records():
    registry = build_registry(_manifest_with_entries())
    assert len(registry.all()) == 3


def test_by_id_returns_correct_record():
    registry = build_registry(_manifest_with_entries())
    record = registry.by_id("backlog")
    assert record is not None
    assert record.id == "backlog"
    assert record.path == "docs/working/backlog.md"


def test_by_id_returns_none_for_unknown_id():
    registry = build_registry(_manifest_with_entries())
    assert registry.by_id("does_not_exist") is None


def test_by_layer_returns_only_that_layer():
    registry = build_registry(_manifest_with_entries())
    canonical = registry.by_layer("canonical")
    assert len(canonical) == 1
    assert canonical[0].id == "architecture"


def test_by_layer_working():
    registry = build_registry(_manifest_with_entries())
    working = registry.by_layer("working")
    assert len(working) == 1
    assert working[0].id == "backlog"


def test_by_layer_runtime():
    registry = build_registry(_manifest_with_entries())
    runtime = registry.by_layer("runtime")
    assert len(runtime) == 1
    assert runtime[0].id == "project_rules"


def test_by_layer_unknown_returns_empty_list():
    registry = build_registry(_manifest_with_entries())
    assert registry.by_layer("nonexistent") == []


def test_record_layer_matches_source_section():
    registry = build_registry(_manifest_with_entries())
    for record in registry.all():
        assert record.layer in ("canonical", "working", "runtime")
    assert registry.by_id("architecture").layer == "canonical"
    assert registry.by_id("backlog").layer == "working"
    assert registry.by_id("project_rules").layer == "runtime"


def test_build_registry_empty_manifest_returns_empty_registry():
    registry = build_registry({})
    assert registry.all() == []


def test_build_registry_missing_sections_does_not_raise():
    registry = build_registry({"canonical": []})
    assert registry.all() == []


def test_build_registry_non_list_section_skipped():
    registry = build_registry({"canonical": "not a list", "working": [], "runtime": []})
    assert registry.all() == []


def test_document_record_fields():
    registry = build_registry(_manifest_with_entries())
    record = registry.by_id("architecture")
    assert record.id == "architecture"
    assert record.path == "docs/canonical/architecture.md"
    assert record.layer == "canonical"
    assert record.purpose == "Defines system structure"
    assert record.authority == "highest"
    assert record.editable_by_agents is False
    assert record.read_when == ["designing_features"]
