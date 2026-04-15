"""Shared pytest fixtures for Forge tests."""

from pathlib import Path

import pytest
import yaml

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

_FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> dict:
    with (_FIXTURES_DIR / name).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture
def valid_manifest_dict() -> dict:
    """Return the valid_manifest.yaml fixture as a parsed dict."""
    return _load_fixture("valid_manifest.yaml")


@pytest.fixture
def valid_repo(tmp_path: Path) -> Path:
    """Set up a minimal valid repository under tmp_path.

    Writes valid_manifest.yaml to docs/runtime/docs_manifest.yaml and
    creates all files declared in the manifest so existence validation passes.

    Returns:
        The tmp_path root with a fully valid repo structure.
    """
    manifest = _load_fixture("valid_manifest.yaml")

    # Create all declared doc paths
    for layer in ("canonical", "working", "runtime"):
        for entry in manifest.get(layer) or []:
            path = tmp_path / entry["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()

    # Write the manifest itself
    manifest_path = tmp_path / "docs" / "runtime" / "docs_manifest.yaml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(yaml.dump(manifest))

    return tmp_path


@pytest.fixture
def packet_repo(tmp_path: Path) -> Path:
    """Set up a minimal repository with templates and a tasks directory.

    Provides the minimum structure needed to test packet creation:
    - docs/runtime/PROJECT_RULES.md (repo marker)
    - templates/tasks/*.md (the four required packet file templates)
    - tasks/ directory

    Returns:
        tmp_path root usable as a repo root for task service tests.
    """
    # Repo marker
    rules = tmp_path / "docs" / "runtime" / "PROJECT_RULES.md"
    rules.parent.mkdir(parents=True)
    rules.touch()

    # Copy packet templates from the real templates directory
    dest_templates = tmp_path / "templates" / "tasks"
    dest_templates.mkdir(parents=True)
    for name in ("task.md", "context.md", "plan.md", "deliverable_spec.md", "results.md"):
        src = _TEMPLATES_DIR / "tasks" / name
        (dest_templates / name).write_text(src.read_text(encoding="utf-8"))

    # Tasks directory
    (tmp_path / "tasks").mkdir()

    return tmp_path
