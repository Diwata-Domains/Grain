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



# --- existing doc content extraction ---

def test_scanner_reads_readme_content(tmp_path: Path):
    (tmp_path / "README.md").write_text("# My App\n\nDoes great things.", encoding="utf-8")

    result = CodebaseScanner(tmp_path).scan()

    assert "README.md" in result.existing_doc_content
    assert "Does great things." in result.existing_doc_content["README.md"]


def test_scanner_reads_package_json_fields(tmp_path: Path):
    import json
    (tmp_path / "package.json").write_text(
        json.dumps({"name": "my-app", "description": "A cool app", "version": "1.2.3",
                    "dependencies": {"react": "^18", "axios": "^1"}}),
        encoding="utf-8",
    )

    result = CodebaseScanner(tmp_path).scan()

    assert "package.json" in result.existing_doc_content
    pkg = result.existing_doc_content["package.json"]
    assert "my-app" in pkg
    assert "A cool app" in pkg
    assert "react" in pkg


def test_scanner_reads_pyproject_toml_fields(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "grain-kit"\ndescription = "A workflow toolkit"\nversion = "0.1.7"\n'
        'dependencies = ["click>=8.1", "PyYAML>=6.0"]\n',
        encoding="utf-8",
    )

    result = CodebaseScanner(tmp_path).scan()

    assert "pyproject.toml" in result.existing_doc_content
    assert "grain-kit" in result.existing_doc_content["pyproject.toml"]
    assert "A workflow toolkit" in result.existing_doc_content["pyproject.toml"]


def test_scanner_caps_readme_content_at_limit(tmp_path: Path):
    (tmp_path / "README.md").write_text("x" * 5000, encoding="utf-8")

    result = CodebaseScanner(tmp_path).scan()

    assert len(result.existing_doc_content["README.md"]) < 2200  # cap + truncation marker


def test_scanner_reads_architecture_doc(tmp_path: Path):
    arch_dir = tmp_path / "docs"
    arch_dir.mkdir()
    (arch_dir / "architecture.md").write_text("## Subsystems\n\n- API\n- DB", encoding="utf-8")

    result = CodebaseScanner(tmp_path).scan()

    assert "docs/architecture.md" in result.existing_doc_content
    assert "API" in result.existing_doc_content["docs/architecture.md"]


def test_scanner_returns_empty_content_when_no_known_docs(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('hello')", encoding="utf-8")

    result = CodebaseScanner(tmp_path).scan()

    assert result.existing_doc_content == {}


def test_scanner_detects_modules_in_src_directory(tmp_path: Path):
    _write(tmp_path / "src" / "myapp" / "__init__.py")
    _write(tmp_path / "src" / "myapp" / "core.py")

    result = CodebaseScanner(tmp_path).scan()

    assert any("myapp" in m for m in result.detected_modules)


def test_scanner_detects_modules_at_repo_root(tmp_path: Path):
    _write(tmp_path / "grain" / "__init__.py")
    _write(tmp_path / "grain" / "cli.py")

    result = CodebaseScanner(tmp_path).scan()

    assert any("grain" in m for m in result.detected_modules)


def test_scanner_detected_modules_empty_when_no_code_dirs(tmp_path: Path):
    _write(tmp_path / "README.md", "# Project")

    result = CodebaseScanner(tmp_path).scan()

    assert result.detected_modules == []
