"""Tests for `grain adapter list/show` commands."""

import json
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main


def _write_adapter_profiles(repo_root):
    path = repo_root / "docs" / "runtime" / "adapter_profiles.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """# Adapter Profiles

## 5. Adapter Profiles

### code_adapter
- `adapter_id`: `code_adapter`
- `domain_type`: `code`
- `applies_to`:
  - Python
- `relevant_file_patterns`:
  - `src/**`
- `test_or_validation_hints`:
  - run focused tests

### frontend_adapter
- `adapter_id`: `frontend_adapter`
- `domain_type`: `frontend`
- `applies_to`:
  - React
- `context_priority_rules`:
  - prioritize changed UI modules
""",
        encoding="utf-8",
    )


def _write_adapter_package(root: Path, package_id="community-docs-adapter", adapter_id="community_docs_adapter"):
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
        f"""# Adapter Package

## 5. Adapter Profiles

### {adapter_id}
- `adapter_id`: `{adapter_id}`
- `domain_type`: `docs`
- `applies_to`:
  - Markdown
- `context_priority_rules`:
  - prioritize docs changes
""",
        encoding="utf-8",
    )


def test_adapter_list_text_output(tmp_path):
    _write_adapter_profiles(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "adapter", "list"])

    assert result.exit_code == 0, result.output
    assert "adapter list: ok" in result.output
    assert "code_adapter" in result.output
    assert "frontend_adapter" in result.output


def test_adapter_list_json_output(tmp_path):
    _write_adapter_profiles(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "--format", "json", "adapter", "list"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["command"] == "adapter list"
    assert data["count"] == 2
    assert [item["adapter_id"] for item in data["profiles"]] == [
        "code_adapter",
        "frontend_adapter",
    ]


def test_adapter_show_text_output(tmp_path):
    _write_adapter_profiles(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "adapter", "show", "--id", "code_adapter"],
    )

    assert result.exit_code == 0, result.output
    assert "adapter show: ok" in result.output
    assert "adapter_id        code_adapter" in result.output
    assert "domain_type       code" in result.output


def test_adapter_show_json_output(tmp_path):
    _write_adapter_profiles(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "--format", "json", "adapter", "show", "--id", "frontend_adapter"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["command"] == "adapter show"
    assert data["adapter"]["adapter_id"] == "frontend_adapter"
    assert data["adapter"]["domain_type"] == "frontend"


def test_adapter_show_unknown_id_exits_two(tmp_path):
    _write_adapter_profiles(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "adapter", "show", "--id", "missing_adapter"],
    )
    assert result.exit_code == 2


def test_adapter_install_text_output_from_source(tmp_path):
    _write_adapter_profiles(tmp_path)
    package_dir = tmp_path / "community-package"
    _write_adapter_package(package_dir)
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "adapter", "install", "--source", str(package_dir)],
    )

    assert result.exit_code == 0, result.output
    assert "adapter install: ok" in result.output
    assert "package_id        community-docs-adapter" in result.output
    assert "adapter_id        community_docs_adapter" in result.output


def test_adapter_install_json_output_from_handle(tmp_path):
    _write_adapter_profiles(tmp_path)
    registry_root = tmp_path / "registry"
    _write_adapter_package(registry_root / "community" / "docs")
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "--repo",
            str(tmp_path),
            "--format",
            "json",
            "adapter",
            "install",
            "--handle",
            "community-docs-adapter",
            "--registry-root",
            str(registry_root),
        ],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["command"] == "adapter install"
    assert data["source_kind"] == "registry_handle"
    assert data["adapter_id"] == "community_docs_adapter"


def test_adapter_install_invalid_selector_exits_one(tmp_path):
    _write_adapter_profiles(tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, ["--repo", str(tmp_path), "adapter", "install"])

    assert result.exit_code == 1
