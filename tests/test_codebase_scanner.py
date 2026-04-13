"""Tests for existing-project CodebaseScanner service."""

from __future__ import annotations

from pathlib import Path

from grain.services.codebase_scanner import CodebaseScanner


def _write(path: Path, content: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_scanner_detects_primary_languages_with_frequency_order(tmp_path: Path):
    _write(tmp_path / "src" / "main.py")
    _write(tmp_path / "src" / "worker.py")
    _write(tmp_path / "ui" / "app.tsx")
    _write(tmp_path / "README.md", "# project")

    result = CodebaseScanner(tmp_path).scan()

    assert result.primary_languages == ["Python", "TypeScript"]
    assert result.language_counts == {"Python": 2, "TypeScript": 1}


def test_scanner_detects_applicable_adapters(tmp_path: Path):
    _write(tmp_path / "src" / "main.py")
    _write(tmp_path / "web" / "app.tsx")
    _write(tmp_path / "docs" / "guide.md")
    _write(tmp_path / "data" / "report.csv")

    result = CodebaseScanner(tmp_path).scan()

    assert result.applicable_adapters == [
        "code_adapter",
        "frontend_adapter",
        "docs_adapter",
        "spreadsheet_adapter",
    ]


def test_scanner_detects_key_files(tmp_path: Path):
    _write(tmp_path / "README.md")
    _write(tmp_path / "pyproject.toml")
    _write(tmp_path / "package.json")
    _write(tmp_path / "Makefile")

    result = CodebaseScanner(tmp_path).scan()

    assert result.key_files == [
        "Makefile",
        "README.md",
        "package.json",
        "pyproject.toml",
    ]


def test_scanner_detects_ci_configs(tmp_path: Path):
    _write(tmp_path / ".github" / "workflows" / "ci.yml")
    _write(tmp_path / ".gitlab-ci.yml")
    _write(tmp_path / ".circleci" / "config.yml")

    result = CodebaseScanner(tmp_path).scan()

    assert result.ci_configs == [
        ".circleci/config.yml",
        ".github/workflows/ci.yml",
        ".gitlab-ci.yml",
    ]


def test_scanner_collects_existing_documentation(tmp_path: Path):
    _write(tmp_path / "README.md")
    _write(tmp_path / "docs" / "architecture.md")
    _write(tmp_path / "notes" / "migration.rst")

    result = CodebaseScanner(tmp_path).scan()

    assert result.documentation_files == [
        "README.md",
        "docs/architecture.md",
        "notes/migration.rst",
    ]


def test_scanner_ignores_common_generated_or_dependency_dirs(tmp_path: Path):
    _write(tmp_path / ".git" / "config")
    _write(tmp_path / "node_modules" / "pkg" / "index.js")
    _write(tmp_path / ".venv" / "bin" / "activate")
    _write(tmp_path / "src" / "app.py")

    result = CodebaseScanner(tmp_path).scan()

    assert result.language_counts == {"Python": 1}
    assert result.primary_languages == ["Python"]


def test_scanner_handles_missing_or_non_directory_root(tmp_path: Path):
    missing_root = tmp_path / "missing"
    result = CodebaseScanner(missing_root).scan()
    assert result.root == str(missing_root.resolve())
    assert result.primary_languages == []
    assert result.applicable_adapters == []
    assert result.key_files == []


def test_scanner_emits_devops_hint_for_dockerfile(tmp_path: Path):
    _write(tmp_path / "Dockerfile")
    _write(tmp_path / "src" / "main.py")

    result = CodebaseScanner(tmp_path).scan()

    assert any("devops_adapter" in hint for hint in result.custom_adapter_hints)


def test_scanner_emits_devops_hint_for_terraform(tmp_path: Path):
    _write(tmp_path / "infra" / "main.tf")
    _write(tmp_path / "src" / "app.py")

    result = CodebaseScanner(tmp_path).scan()

    assert any("devops_adapter" in hint for hint in result.custom_adapter_hints)


def test_scanner_emits_data_hint_for_notebooks(tmp_path: Path):
    _write(tmp_path / "analysis.ipynb", '{"cells":[],"metadata":{},"nbformat":4,"nbformat_minor":5}')

    result = CodebaseScanner(tmp_path).scan()

    assert any("data_adapter" in hint for hint in result.custom_adapter_hints)


def test_scanner_emits_data_hint_for_parquet(tmp_path: Path):
    _write(tmp_path / "data" / "dataset.parquet")

    result = CodebaseScanner(tmp_path).scan()

    assert any("data_adapter" in hint for hint in result.custom_adapter_hints)


def test_scanner_emits_mobile_hint_for_swift(tmp_path: Path):
    _write(tmp_path / "App" / "ContentView.swift")

    result = CodebaseScanner(tmp_path).scan()

    assert any("ios_adapter" in hint for hint in result.custom_adapter_hints)


def test_scanner_emits_mobile_hint_for_kotlin(tmp_path: Path):
    _write(tmp_path / "app" / "MainActivity.kt")

    result = CodebaseScanner(tmp_path).scan()

    assert any("android_adapter" in hint for hint in result.custom_adapter_hints)


def test_scanner_no_custom_hints_for_standard_project(tmp_path: Path):
    _write(tmp_path / "src" / "main.py")
    _write(tmp_path / "tests" / "test_main.py")
    _write(tmp_path / "README.md", "# project")

    result = CodebaseScanner(tmp_path).scan()

    assert result.custom_adapter_hints == []

