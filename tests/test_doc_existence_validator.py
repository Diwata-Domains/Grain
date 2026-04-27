"""Tests for the document existence validator."""

from pathlib import Path

from grain.domain.documents import build_registry
from grain.validators.doc_existence_validator import validate_doc_existence


def _make_registry(entries: list[dict], layer: str = "canonical"):
    return build_registry({layer: entries})


def test_all_paths_present_returns_empty_list(tmp_path):
    (tmp_path / "docs" / "canonical").mkdir(parents=True)
    (tmp_path / "docs" / "canonical" / "architecture.md").write_text("")
    registry = _make_registry([
        {"id": "architecture", "path": "docs/canonical/architecture.md",
         "purpose": "x", "authority": "highest", "editable_by_agents": False, "read_when": ["always"]},
    ])
    assert validate_doc_existence(registry, tmp_path) == []


def test_missing_file_returns_error_with_id(tmp_path):
    registry = _make_registry([
        {"id": "architecture", "path": "docs/canonical/architecture.md",
         "purpose": "x", "authority": "highest", "editable_by_agents": False, "read_when": ["always"]},
    ])
    errors = validate_doc_existence(registry, tmp_path)
    assert len(errors) == 1
    assert "architecture" in errors[0]
    assert "docs/canonical/architecture.md" in errors[0]


def test_existing_directory_passes(tmp_path):
    (tmp_path / "docs" / "runtime").mkdir(parents=True)
    registry = _make_registry([
        {"id": "runtime_docs", "path": "docs/runtime",
         "purpose": "x", "authority": "high_runtime", "editable_by_agents": False, "read_when": ["always"]},
    ])
    assert validate_doc_existence(registry, tmp_path) == []


def test_missing_directory_returns_error(tmp_path):
    registry = _make_registry([
        {"id": "missing_dir", "path": "docs/canonical/missing_dir",
         "purpose": "x", "authority": "high", "editable_by_agents": False, "read_when": ["always"]},
    ])
    errors = validate_doc_existence(registry, tmp_path)
    assert len(errors) == 1
    assert "missing_dir" in errors[0]


def test_empty_path_string_returns_error(tmp_path):
    registry = _make_registry([
        {"id": "broken", "path": "",
         "purpose": "x", "authority": "highest", "editable_by_agents": False, "read_when": ["always"]},
    ])
    errors = validate_doc_existence(registry, tmp_path)
    assert len(errors) == 1
    assert "broken" in errors[0]


def test_empty_registry_returns_empty_list(tmp_path):
    registry = build_registry({})
    assert validate_doc_existence(registry, tmp_path) == []


def test_multiple_missing_returns_one_error_per_missing(tmp_path):
    registry = _make_registry([
        {"id": "doc_a", "path": "docs/a.md",
         "purpose": "x", "authority": "highest", "editable_by_agents": False, "read_when": ["always"]},
        {"id": "doc_b", "path": "docs/b.md",
         "purpose": "x", "authority": "highest", "editable_by_agents": False, "read_when": ["always"]},
    ])
    errors = validate_doc_existence(registry, tmp_path)
    assert len(errors) == 2
    assert any("doc_a" in e for e in errors)
    assert any("doc_b" in e for e in errors)


def test_mixed_present_and_missing(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "present.md").write_text("")
    registry = _make_registry([
        {"id": "present", "path": "docs/present.md",
         "purpose": "x", "authority": "highest", "editable_by_agents": False, "read_when": ["always"]},
        {"id": "missing", "path": "docs/missing.md",
         "purpose": "x", "authority": "highest", "editable_by_agents": False, "read_when": ["always"]},
    ])
    errors = validate_doc_existence(registry, tmp_path)
    assert len(errors) == 1
    assert "missing" in errors[0]
