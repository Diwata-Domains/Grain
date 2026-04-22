"""Tests for the Phase 19 registry CI workflow and author guide."""

from pathlib import Path

import yaml


def test_phase19_registry_workflow_exists_and_targets_registry_tests():
    path = Path(".github/workflows/community-adapter-registry-validate.yml")

    payload = yaml.safe_load(path.read_text(encoding="utf-8"))

    assert payload["name"] == "Community Adapter Registry Validate"
    jobs = payload["jobs"]["validate-community-adapter-registry"]
    run_script = jobs["steps"][-1]["run"]
    assert "tests/test_adapter_package_service.py" in run_script
    assert "tests/test_adapter_install_service.py" in run_script
    assert "tests/test_phase19_registry_scaffold.py" in run_script
    assert "tests/test_phase19_registry_ci_docs.py" in run_script


def test_phase19_author_guide_mentions_validation_and_promotion_boundary():
    path = Path("docs/working/community_adapter_authoring.md")

    text = path.read_text(encoding="utf-8")

    assert "adapter_package.yaml" in text
    assert "adapter_profile.md" in text
    assert "review_metadata.yaml" in text
    assert "local reviewed-registry checkout plus handle" in text
    assert "promotion from Community to Official remains a separate maintainer decision" in text
