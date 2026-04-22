"""Tests for the Phase 19 community adapter registry scaffold."""

from pathlib import Path

import yaml

from grain.adapters.adapter_config import parse_adapter_profiles_markdown


def test_phase19_registry_scaffold_files_exist():
    root = Path("contrib/community_adapter_registry")

    assert (root / "README.md").exists()
    assert (root / "review_checklist.md").exists()
    assert (root / "templates" / "adapter_package.yaml").exists()
    assert (root / "templates" / "adapter_profile.md").exists()
    assert (root / "templates" / "review_metadata.yaml").exists()


def test_adapter_package_template_contains_required_fields():
    path = Path("contrib/community_adapter_registry/templates/adapter_package.yaml")

    payload = yaml.safe_load(path.read_text(encoding="utf-8"))

    assert payload["package_id"] == "sample-community-adapter"
    assert payload["adapter_id"] == "sample_adapter"
    assert payload["version"] == "0.1.0"
    assert payload["profile_path"] == "adapter_profile.md"


def test_adapter_profile_template_parses_as_valid_profile():
    path = Path("contrib/community_adapter_registry/templates/adapter_profile.md")

    profiles = parse_adapter_profiles_markdown(path.read_text(encoding="utf-8"))

    assert len(profiles) == 1
    assert profiles[0].adapter_id == "sample_adapter"
    assert profiles[0].domain_type == "docs"


def test_review_metadata_template_is_pending_by_default():
    path = Path("contrib/community_adapter_registry/templates/review_metadata.yaml")

    payload = yaml.safe_load(path.read_text(encoding="utf-8"))

    assert payload["review_state"] == "pending"
    assert payload["promotion_candidate"] is False
