"""Tests for the authority-order validator."""

import pytest

from grain.domain.documents import build_registry
from grain.validators.authority_validator import (
    ALLOWED_AUTHORITY_VALUES,
    validate_authority,
)


def _manifest_with_authority_order():
    return {"rules": {"authority_order": ["docs/runtime/PROJECT_RULES.md"]}}


def _entry(id, authority, editable, layer="canonical"):
    return {
        "id": id,
        "path": f"docs/{layer}/{id}.md",
        "purpose": "x",
        "authority": authority,
        "editable_by_agents": editable,
        "read_when": ["always"],
    }


def _registry_from(entries, layer="canonical"):
    return build_registry({layer: entries})


def test_valid_registry_and_manifest_returns_empty_list():
    registry = _registry_from([_entry("arch", "highest", False)])
    errors = validate_authority(registry, _manifest_with_authority_order())
    assert errors == []


@pytest.mark.parametrize("valid_value", sorted(ALLOWED_AUTHORITY_VALUES))
def test_all_allowed_authority_values_pass(valid_value):
    registry = _registry_from([_entry("doc", valid_value, False)], layer="working")
    errors = validate_authority(registry, _manifest_with_authority_order())
    assert errors == []


def test_invalid_authority_value_returns_error():
    registry = _registry_from([_entry("doc", "super_high", False)])
    errors = validate_authority(registry, _manifest_with_authority_order())
    assert len(errors) == 1
    assert "doc" in errors[0]
    assert "super_high" in errors[0]


def test_canonical_editable_by_agents_true_returns_error():
    registry = _registry_from([_entry("arch", "highest", True, layer="canonical")])
    errors = validate_authority(registry, _manifest_with_authority_order())
    assert any("arch" in e and "editable_by_agents" in e for e in errors)


def test_working_editable_by_agents_true_does_not_error():
    registry = _registry_from([_entry("backlog", "secondary", True, layer="working")], layer="working")
    errors = validate_authority(registry, _manifest_with_authority_order())
    assert errors == []


def test_runtime_editable_by_agents_true_does_not_error():
    registry = _registry_from([_entry("docs_index", "high_runtime", True, layer="runtime")], layer="runtime")
    errors = validate_authority(registry, _manifest_with_authority_order())
    assert errors == []


def test_missing_authority_order_returns_error():
    registry = _registry_from([_entry("arch", "highest", False)])
    manifest = {"rules": {}}
    errors = validate_authority(registry, manifest)
    assert any("authority_order" in e for e in errors)


def test_empty_authority_order_returns_error():
    registry = _registry_from([_entry("arch", "highest", False)])
    manifest = {"rules": {"authority_order": []}}
    errors = validate_authority(registry, manifest)
    assert any("authority_order" in e for e in errors)


def test_missing_rules_section_returns_error():
    registry = _registry_from([_entry("arch", "highest", False)])
    errors = validate_authority(registry, {})
    assert any("rules" in e for e in errors)


def test_multiple_violations_return_one_error_each():
    registry = build_registry({
        "canonical": [
            _entry("arch", "bad_value", True),
        ]
    })
    errors = validate_authority(registry, {"rules": {"authority_order": []}})
    # invalid authority, editable canonical, empty authority_order = 3 errors
    assert len(errors) == 3


def test_empty_registry_with_valid_manifest_returns_empty_list():
    registry = build_registry({})
    errors = validate_authority(registry, _manifest_with_authority_order())
    assert errors == []
