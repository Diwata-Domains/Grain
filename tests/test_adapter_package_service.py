"""Tests for community adapter package validation."""

from pathlib import Path

from grain.services.adapter_package_service import validate_adapter_package


VALID_PROFILE = """# Adapter Package

## 5. Adapter Profiles

### docs_adapter
- `adapter_id`: `docs_adapter`
- `domain_type`: `docs`
- `applies_to`:
  - Markdown
- `relevant_file_patterns`:
  - `docs/**`
- `test_or_validation_hints`:
  - run doc validation
"""


def test_validate_adapter_package_accepts_valid_package(tmp_path: Path):
    package_dir = _write_package(tmp_path)

    result, validation = validate_adapter_package(package_dir)

    assert result.ok is True
    assert result.command == "adapter package validate"
    assert validation.valid is True
    assert validation.package_id == "community-docs-adapter"
    assert validation.adapter_id == "docs_adapter"
    assert validation.version == "1.0.0"
    assert validation.profile_path == "adapter_profile.md"
    assert [profile.adapter_id for profile in validation.profiles] == ["docs_adapter"]
    assert validation.errors == []


def test_validate_adapter_package_reports_missing_metadata_file(tmp_path: Path):
    package_dir = tmp_path / "community-docs-adapter"
    package_dir.mkdir()

    result, validation = validate_adapter_package(package_dir)

    assert result.ok is False
    assert validation.valid is False
    assert "missing required file: adapter_package.yaml" in validation.errors
    assert "missing required metadata field: package_id" in validation.errors
    assert "missing adapter profile file: adapter_profile.md" in validation.errors


def test_validate_adapter_package_reports_invalid_metadata_yaml(tmp_path: Path):
    package_dir = tmp_path / "community-docs-adapter"
    package_dir.mkdir()
    (package_dir / "adapter_package.yaml").write_text("package_id: [broken\n", encoding="utf-8")

    _, validation = validate_adapter_package(package_dir)

    assert validation.valid is False
    assert len(validation.errors) == 5
    assert validation.errors[0].startswith("could not read adapter_package.yaml:")


def test_validate_adapter_package_reports_missing_required_metadata_field(tmp_path: Path):
    package_dir = _write_package(
        tmp_path,
        metadata="""package_id: community-docs-adapter
version: 1.0.0
profile_path: adapter_profile.md
""",
    )

    _, validation = validate_adapter_package(package_dir)

    assert validation.valid is False
    assert "missing required metadata field: adapter_id" in validation.errors


def test_validate_adapter_package_reports_missing_profile_file(tmp_path: Path):
    package_dir = _write_package(tmp_path)
    (package_dir / "adapter_profile.md").unlink()

    _, validation = validate_adapter_package(package_dir)

    assert validation.valid is False
    assert validation.errors == ["missing adapter profile file: adapter_profile.md"]


def test_validate_adapter_package_reports_invalid_profile_markdown(tmp_path: Path):
    package_dir = _write_package(
        tmp_path,
        profile="""# Adapter Package

## 5. Adapter Profiles

### docs_adapter
- `adapter_id`: `docs_adapter`
- `domain_type`: `docs`
- `applies_to`:
  - Markdown
""",
    )

    _, validation = validate_adapter_package(package_dir)

    assert validation.valid is False
    assert len(validation.errors) == 1
    assert "must include at least one hint section" in validation.errors[0]


def test_validate_adapter_package_rejects_multiple_profiles(tmp_path: Path):
    package_dir = _write_package(
        tmp_path,
        profile=VALID_PROFILE
        + """
### docs_adapter_v2
- `adapter_id`: `docs_adapter_v2`
- `domain_type`: `docs`
- `applies_to`:
  - Markdown
- `context_priority_rules`:
  - prioritize docs
""",
    )

    _, validation = validate_adapter_package(package_dir)

    assert validation.valid is False
    assert (
        "adapter package must contain exactly one adapter profile, found 2"
        in validation.errors
    )


def test_validate_adapter_package_rejects_metadata_profile_id_mismatch(tmp_path: Path):
    package_dir = _write_package(
        tmp_path,
        metadata="""package_id: community-docs-adapter
adapter_id: frontend_adapter
version: 1.0.0
profile_path: adapter_profile.md
""",
    )

    _, validation = validate_adapter_package(package_dir)

    assert validation.valid is False
    assert (
        "metadata adapter_id does not match adapter profile adapter_id: "
        "frontend_adapter != docs_adapter"
    ) in validation.errors


def test_validate_adapter_package_reports_missing_directory(tmp_path: Path):
    package_dir = tmp_path / "missing-package"

    result, validation = validate_adapter_package(package_dir)

    assert result.ok is False
    assert validation.valid is False
    assert validation.errors == [f"package directory not found: {package_dir}"]


def _write_package(
    root: Path,
    metadata: str | None = None,
    profile: str | None = None,
) -> Path:
    package_dir = root / "community-docs-adapter"
    package_dir.mkdir()
    (package_dir / "adapter_package.yaml").write_text(
        metadata
        or """package_id: community-docs-adapter
adapter_id: docs_adapter
version: 1.0.0
profile_path: adapter_profile.md
""",
        encoding="utf-8",
    )
    (package_dir / "adapter_profile.md").write_text(profile or VALID_PROFILE, encoding="utf-8")
    return package_dir
