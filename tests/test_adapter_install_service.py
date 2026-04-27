"""Tests for explicit local adapter installs."""

from pathlib import Path

from grain.adapters.adapter_config import load_adapter_profiles
from grain.services.adapter_install_service import install_adapter


BASE_PROFILES = """# Adapter Profiles

## 5. Adapter Profiles

### code_adapter
- `adapter_id`: `code_adapter`
- `domain_type`: `code`
- `applies_to`:
  - Python
- `test_or_validation_hints`:
  - run focused tests
"""


PACKAGE_PROFILE = """# Adapter Package

## 5. Adapter Profiles

### community_docs_adapter
- `adapter_id`: `community_docs_adapter`
- `domain_type`: `docs`
- `applies_to`:
  - Markdown
- `context_priority_rules`:
  - prioritize docs changes
"""


def test_install_adapter_from_source_appends_profile(tmp_path: Path):
    _write_repo(tmp_path)
    package_dir = _write_package(tmp_path / "pkg")

    result, install = install_adapter(tmp_path, source=package_dir)

    assert result.ok is True
    assert install is not None
    assert install.adapter_id == "community_docs_adapter"
    assert install.package_id == "community-docs-adapter"
    assert install.installed_path == "docs/runtime/adapter_profiles.md"
    profiles = load_adapter_profiles(tmp_path)
    assert [profile.adapter_id for profile in profiles] == [
        "code_adapter",
        "community_docs_adapter",
    ]


def test_install_adapter_from_handle_resolves_local_registry_checkout(tmp_path: Path):
    _write_repo(tmp_path)
    registry_root = tmp_path / "registry"
    package_dir = _write_package(registry_root / "community" / "docs")

    result, install = install_adapter(
        tmp_path,
        handle="community-docs-adapter",
        registry_root=registry_root,
    )

    assert result.ok is True
    assert install is not None
    assert install.package_dir == package_dir
    profiles = load_adapter_profiles(tmp_path)
    assert profiles[-1].adapter_id == "community_docs_adapter"


def test_install_adapter_rejects_duplicate_adapter_id(tmp_path: Path):
    _write_repo(tmp_path)
    package_dir = _write_package(
        tmp_path / "pkg",
        adapter_id="code_adapter",
        package_id="community-code-adapter",
    )

    result, install = install_adapter(tmp_path, source=package_dir)

    assert result.ok is False
    assert install is not None
    assert install.errors == ["adapter 'code_adapter' is already installed"]


def test_install_adapter_rejects_unknown_handle(tmp_path: Path):
    _write_repo(tmp_path)
    registry_root = tmp_path / "registry"
    registry_root.mkdir()

    result, install = install_adapter(
        tmp_path,
        handle="missing-adapter",
        registry_root=registry_root,
    )

    assert result.ok is False
    assert install is not None
    assert install.errors == ["registry handle not found: missing-adapter"]


def test_install_adapter_rejects_ambiguous_handle(tmp_path: Path):
    _write_repo(tmp_path)
    registry_root = tmp_path / "registry"
    _write_package(registry_root / "community" / "docs-a", package_id="pkg-a")
    _write_package(registry_root / "community" / "docs-b", package_id="pkg-b")

    result, install = install_adapter(
        tmp_path,
        handle="community_docs_adapter",
        registry_root=registry_root,
    )

    assert result.ok is False
    assert install is not None
    assert install.errors == [
        "registry handle is ambiguous: community_docs_adapter (community/docs-a, community/docs-b)"
    ]


def test_install_adapter_requires_explicit_selector(tmp_path: Path):
    _write_repo(tmp_path)

    result, install = install_adapter(tmp_path)

    assert result.ok is False
    assert install is not None
    assert install.errors == ["either --source or --handle is required"]


def _write_repo(root: Path) -> None:
    profiles_path = root / "docs" / "runtime" / "adapter_profiles.md"
    profiles_path.parent.mkdir(parents=True, exist_ok=True)
    profiles_path.write_text(BASE_PROFILES, encoding="utf-8")


def _write_package(
    root: Path,
    *,
    package_id: str = "community-docs-adapter",
    adapter_id: str = "community_docs_adapter",
) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "adapter_package.yaml").write_text(
        f"""package_id: {package_id}
adapter_id: {adapter_id}
version: 1.0.0
profile_path: adapter_profile.md
""",
        encoding="utf-8",
    )
    (root / "adapter_profile.md").write_text(
        PACKAGE_PROFILE.replace("community_docs_adapter", adapter_id),
        encoding="utf-8",
    )
    return root
