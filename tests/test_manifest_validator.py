"""Tests for the manifest schema validator (validators/manifest_validator.py)."""

import copy

import pytest

from forge.validators.manifest_validator import validate_manifest_schema


def _minimal_valid_manifest() -> dict:
    return {
        "version": 1,
        "project": {"name": "test", "type": "cli", "mode": "single", "storage": "fs", "authority_model": "explicit"},
        "canonical": [
            {
                "id": "product_scope",
                "path": "docs/canonical/product_scope.md",
                "purpose": "Defines scope",
                "authority": "highest",
                "editable_by_agents": False,
                "read_when": ["planning"],
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
        "tasks": {
            "root": "tasks/",
            "packet_files": [{"name": "task", "filename": "task.md", "required": True}],
            "patch_dir": "patches/",
            "status_values": ["draft", "ready", "done"],
            "id_format": "TASK-####",
        },
        "rules": {
            "authority_order": ["docs/runtime/PROJECT_RULES.md"],
            "canonical_change_policy": {
                "direct_agent_edits_allowed": False,
                "require_human_approval": True,
                "proposal_location": "docs/working/change_proposals.md",
            },
            "context_policy": {
                "load_minimum_required_docs": True,
                "prefer_task_packet_context": True,
                "avoid_full_repo_context": True,
            },
            "execution_policy": {
                "use_task_packets": True,
                "one_task_one_packet": True,
                "patch_over_rewrite": True,
                "preserve_doc_separation": True,
            },
            "completion_policy": {
                "require_defined_deliverable": True,
                "require_results_recorded": True,
                "require_rule_check": True,
            },
        },
    }


def test_valid_manifest_returns_empty_list():
    assert validate_manifest_schema(_minimal_valid_manifest()) == []


@pytest.mark.parametrize("missing_key", ["version", "project", "canonical", "working", "runtime", "tasks", "rules"])
def test_missing_top_level_section_returns_error(missing_key):
    manifest = _minimal_valid_manifest()
    del manifest[missing_key]
    errors = validate_manifest_schema(manifest)
    assert any(missing_key in e for e in errors)


@pytest.mark.parametrize("missing_field", ["id", "path", "purpose", "authority", "editable_by_agents", "read_when"])
def test_missing_doc_entry_field_returns_error(missing_field):
    manifest = _minimal_valid_manifest()
    del manifest["canonical"][0][missing_field]
    errors = validate_manifest_schema(manifest)
    assert any(missing_field in e for e in errors)


def test_editable_by_agents_non_boolean_returns_error():
    manifest = _minimal_valid_manifest()
    manifest["canonical"][0]["editable_by_agents"] = "yes"
    errors = validate_manifest_schema(manifest)
    assert any("editable_by_agents" in e for e in errors)


def test_read_when_empty_list_returns_error():
    manifest = _minimal_valid_manifest()
    manifest["canonical"][0]["read_when"] = []
    errors = validate_manifest_schema(manifest)
    assert any("read_when" in e for e in errors)


@pytest.mark.parametrize("missing_field", ["root", "packet_files", "patch_dir", "status_values", "id_format"])
def test_missing_tasks_field_returns_error(missing_field):
    manifest = _minimal_valid_manifest()
    del manifest["tasks"][missing_field]
    errors = validate_manifest_schema(manifest)
    assert any(missing_field in e for e in errors)


@pytest.mark.parametrize(
    "missing_subkey",
    ["authority_order", "canonical_change_policy", "context_policy", "execution_policy", "completion_policy"],
)
def test_missing_rules_subkey_returns_error(missing_subkey):
    manifest = _minimal_valid_manifest()
    del manifest["rules"][missing_subkey]
    errors = validate_manifest_schema(manifest)
    assert any(missing_subkey in e for e in errors)


def test_missing_canonical_change_policy_field_returns_error():
    manifest = _minimal_valid_manifest()
    del manifest["rules"]["canonical_change_policy"]["proposal_location"]
    errors = validate_manifest_schema(manifest)
    assert any("proposal_location" in e for e in errors)


def test_missing_completion_policy_field_returns_error():
    manifest = _minimal_valid_manifest()
    del manifest["rules"]["completion_policy"]["require_results_recorded"]
    errors = validate_manifest_schema(manifest)
    assert any("require_results_recorded" in e for e in errors)


def test_validate_does_not_raise_on_empty_dict():
    errors = validate_manifest_schema({})
    assert isinstance(errors, list)
    assert len(errors) > 0


def test_working_layer_doc_entry_validated():
    manifest = _minimal_valid_manifest()
    del manifest["working"][0]["purpose"]
    errors = validate_manifest_schema(manifest)
    assert any("purpose" in e for e in errors)
