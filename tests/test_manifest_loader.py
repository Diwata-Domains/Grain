"""Tests for the manifest file loader (adapters/manifest.py)."""

from pathlib import Path

import pytest

from forge.adapters.manifest import MANIFEST_PATH, load_manifest
from forge.domain.errors import ConfigError, MissingPathError


def test_load_manifest_returns_dict(tmp_path):
    manifest_file = tmp_path / "docs" / "runtime" / "docs_manifest.yaml"
    manifest_file.parent.mkdir(parents=True)
    manifest_file.write_text("version: 1\nproject:\n  name: test\n")

    result = load_manifest(tmp_path)

    assert isinstance(result, dict)
    assert result["version"] == 1
    assert result["project"]["name"] == "test"


def test_load_manifest_missing_raises_missing_path_error(tmp_path):
    with pytest.raises(MissingPathError) as exc_info:
        load_manifest(tmp_path)

    assert MANIFEST_PATH in exc_info.value.message


def test_load_manifest_malformed_yaml_raises_config_error(tmp_path):
    manifest_file = tmp_path / "docs" / "runtime" / "docs_manifest.yaml"
    manifest_file.parent.mkdir(parents=True)
    manifest_file.write_text("key: [\nunclosed bracket\n")

    with pytest.raises(ConfigError) as exc_info:
        load_manifest(tmp_path)

    assert MANIFEST_PATH in exc_info.value.message


def test_load_manifest_empty_file_returns_empty_dict(tmp_path):
    manifest_file = tmp_path / "docs" / "runtime" / "docs_manifest.yaml"
    manifest_file.parent.mkdir(parents=True)
    manifest_file.write_text("")

    result = load_manifest(tmp_path)

    assert result == {}


def test_load_manifest_contains_expected_top_level_keys(tmp_path):
    manifest_file = tmp_path / "docs" / "runtime" / "docs_manifest.yaml"
    manifest_file.parent.mkdir(parents=True)
    manifest_file.write_text(
        "version: 1\nproject:\n  name: Forge\ncanonical: []\n"
    )

    result = load_manifest(tmp_path)

    assert "version" in result
    assert "project" in result
    assert "canonical" in result
