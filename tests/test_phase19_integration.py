"""Phase 19 integration coverage for the community adapter registry contract."""

from pathlib import Path

import yaml
from click.testing import CliRunner

from grain.adapters.adapter_config import load_adapter_profiles
from grain.cli import main
from grain.services.adapter_package_service import validate_adapter_package


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


def test_phase19_reviewed_registry_submission_validates_and_installs(tmp_path: Path):
    _write_repo(tmp_path)
    registry_root = tmp_path / "community-registry"
    package_dir = registry_root / "submissions" / "sample-community-adapter"
    _write_scaffold_style_submission(package_dir)

    validation_result, validation = validate_adapter_package(package_dir)
    assert validation_result.ok is True
    assert validation.package_id == "sample-community-adapter"

    runner = CliRunner()
    cli_result = runner.invoke(
        main,
        [
            "--repo",
            str(tmp_path),
            "adapter",
            "install",
            "--handle",
            "sample-community-adapter",
            "--registry-root",
            str(registry_root),
        ],
    )

    assert cli_result.exit_code == 0, cli_result.output
    profiles = load_adapter_profiles(tmp_path)
    assert [profile.adapter_id for profile in profiles] == [
        "code_adapter",
        "sample_adapter",
    ]


def test_phase19_scaffold_and_ci_docs_reference_same_contract():
    scaffold_root = Path("contrib/community_adapter_registry")
    package_template = yaml.safe_load(
        (scaffold_root / "templates" / "adapter_package.yaml").read_text(encoding="utf-8")
    )
    workflow_text = Path(
        ".github/workflows/community-adapter-registry-validate.yml"
    ).read_text(encoding="utf-8")
    authoring_text = Path("docs/working/community_adapter_authoring.md").read_text(
        encoding="utf-8"
    )

    assert package_template["profile_path"] == "adapter_profile.md"
    assert "adapter_package.yaml" in authoring_text
    assert "adapter_profile.md" in authoring_text
    assert "review_metadata.yaml" in authoring_text
    assert "tests/test_adapter_package_service.py" in workflow_text
    assert "tests/test_adapter_install_service.py" in workflow_text
    assert "tests/test_phase19_registry_scaffold.py" in workflow_text
    assert "tests/test_phase19_registry_ci_docs.py" in workflow_text


def _write_repo(root: Path) -> None:
    profiles_path = root / "docs" / "runtime" / "adapter_profiles.md"
    profiles_path.parent.mkdir(parents=True, exist_ok=True)
    profiles_path.write_text(BASE_PROFILES, encoding="utf-8")


def _write_scaffold_style_submission(package_dir: Path) -> None:
    package_dir.mkdir(parents=True, exist_ok=True)
    (package_dir / "adapter_package.yaml").write_text(
        """package_id: sample-community-adapter
adapter_id: sample_adapter
version: 0.1.0
profile_path: adapter_profile.md
""",
        encoding="utf-8",
    )
    (package_dir / "adapter_profile.md").write_text(
        """# Community Adapter Profile

## 5. Adapter Profiles

### sample_adapter
- `adapter_id`: `sample_adapter`
- `domain_type`: `docs`
- `applies_to`:
  - Markdown
- `context_priority_rules`:
  - prioritize docs changes
""",
        encoding="utf-8",
    )
    (package_dir / "review_metadata.yaml").write_text(
        """package_id: sample-community-adapter
review_state: approved
reviewed_by: maintainer
review_notes:
  - sample submission
promotion_candidate: false
""",
        encoding="utf-8",
    )
