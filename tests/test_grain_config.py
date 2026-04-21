"""Tests for the grain: config block in docs_manifest.yaml."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from grain.adapters.manifest import GrainConfig, load_grain_config


def _write_manifest(tmp_path: Path, grain_block: dict | None) -> None:
    manifest: dict = {"version": 1, "project": {"name": "test"}}
    if grain_block is not None:
        manifest["grain"] = grain_block
    manifest_path = tmp_path / "docs" / "runtime" / "docs_manifest.yaml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w") as f:
        yaml.dump(manifest, f)


def test_defaults_when_no_manifest(tmp_path: Path):
    cfg = load_grain_config(tmp_path)
    assert cfg == GrainConfig()


def test_defaults_when_grain_block_absent(tmp_path: Path):
    _write_manifest(tmp_path, grain_block=None)
    cfg = load_grain_config(tmp_path)
    assert cfg.default_supervision == "gated"
    assert cfg.default_format == "text"
    assert cfg.upgrade_check == "silent"
    assert cfg.embedding_provider == "none"
    assert cfg.ollama_embedding_model == "nomic-embed-text"
    assert cfg.local_embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
    assert cfg.openai_embedding_model == "text-embedding-3-small"


def test_reads_all_fields(tmp_path: Path):
    _write_manifest(tmp_path, {
        "default_supervision": "supervised",
        "default_format": "json",
        "upgrade_check": "warn",
        "embedding_provider": "ollama",
        "ollama_embedding_model": "mxbai-embed-large",
        "local_embedding_model": "custom-local-model",
        "openai_embedding_model": "text-embedding-3-large",
    })
    cfg = load_grain_config(tmp_path)
    assert cfg.default_supervision == "supervised"
    assert cfg.default_format == "json"
    assert cfg.upgrade_check == "warn"
    assert cfg.embedding_provider == "ollama"
    assert cfg.ollama_embedding_model == "mxbai-embed-large"
    assert cfg.local_embedding_model == "custom-local-model"
    assert cfg.openai_embedding_model == "text-embedding-3-large"


def test_invalid_value_falls_back_to_default(tmp_path: Path):
    _write_manifest(tmp_path, {
        "default_supervision": "banana",
        "upgrade_check": "always",
    })
    cfg = load_grain_config(tmp_path)
    assert cfg.default_supervision == "gated"
    assert cfg.upgrade_check == "silent"


def test_partial_block_uses_defaults_for_missing(tmp_path: Path):
    _write_manifest(tmp_path, {"upgrade_check": "warn"})
    cfg = load_grain_config(tmp_path)
    assert cfg.upgrade_check == "warn"
    assert cfg.default_format == "text"  # default


def test_blank_embedding_model_values_fall_back_to_defaults(tmp_path: Path):
    _write_manifest(
        tmp_path,
        {
            "embedding_provider": "openai",
            "ollama_embedding_model": "   ",
            "local_embedding_model": "",
            "openai_embedding_model": "   ",
        },
    )

    cfg = load_grain_config(tmp_path)

    assert cfg.embedding_provider == "openai"
    assert cfg.ollama_embedding_model == "nomic-embed-text"
    assert cfg.local_embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
    assert cfg.openai_embedding_model == "text-embedding-3-small"


def test_upgrade_check_warn_in_bundled_template():
    """The bundled docs_manifest.yaml template must default upgrade_check to warn."""
    from grain.services.upgrade_service import _SOURCE_ROOT
    template = _SOURCE_ROOT / "runtime" / "docs_manifest.yaml"
    if not template.exists():
        pytest.skip("bundled template not found")
    with template.open() as f:
        data = yaml.safe_load(f)
    grain_block = data.get("grain", {})
    assert grain_block.get("upgrade_check") == "warn"


def test_project_name_is_placeholder_in_bundled_template():
    """Bundled docs_manifest.yaml must not seed 'Grain' as the project name."""
    from grain.services.upgrade_service import _SOURCE_ROOT
    template = _SOURCE_ROOT / "runtime" / "docs_manifest.yaml"
    if not template.exists():
        pytest.skip("bundled template not found")
    with template.open() as f:
        data = yaml.safe_load(f)
    name = data.get("project", {}).get("name", "")
    assert name != "Grain", "bundled manifest must not seed 'Grain' as the project name"
    assert "[" in name, "bundled manifest project.name should be a placeholder"


def test_project_type_is_placeholder_in_bundled_template():
    """Bundled docs_manifest.yaml must not seed 'cli_toolkit' as the project type."""
    from grain.services.upgrade_service import _SOURCE_ROOT
    template = _SOURCE_ROOT / "runtime" / "docs_manifest.yaml"
    if not template.exists():
        pytest.skip("bundled template not found")
    with template.open() as f:
        data = yaml.safe_load(f)
    ptype = data.get("project", {}).get("type", "")
    assert ptype != "cli_toolkit", "bundled manifest must not seed 'cli_toolkit' as the project type"
