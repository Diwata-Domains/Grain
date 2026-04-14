"""Integration tests for Phase 13 existing-project adoption flow."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main
from grain.domain.scan_result import ScanResult
from grain.services.codebase_scanner import CodebaseScanner
from grain.services.onboard_doc_generator import OnboardDocGenerator


def _run(repo_root: Path, *args: str):
    runner = CliRunner()
    return runner.invoke(main, ["--repo", str(repo_root), *args])


def _write(path: Path, content: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_phase13_onboard_existing_repo_additive_preserves_existing_file(tmp_path: Path):
    existing = tmp_path / "docs" / "canonical" / "architecture.md"
    _write(existing, "preserve me")

    result = _run(tmp_path, "onboard", str(tmp_path))
    assert result.exit_code == 0, result.output
    assert existing.read_text(encoding="utf-8") == "preserve me"
    assert (tmp_path / "docs" / "working").is_dir()
    assert (tmp_path / "prompts").is_dir()


def test_phase13_onboard_dry_run_writes_nothing(tmp_path: Path):
    result = _run(tmp_path, "onboard", str(tmp_path), "--dry-run")
    assert result.exit_code == 0, result.output
    assert not (tmp_path / "docs").exists()
    assert not (tmp_path / "tasks").exists()


def test_phase13_onboard_json_manifest_shape(tmp_path: Path):
    result = _run(tmp_path, "--format", "json", "onboard", str(tmp_path), "--dry-run")
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert set(payload.keys()) == {"created", "skipped", "root"}
    assert payload["root"] == str(tmp_path.resolve())


def test_phase13_onboard_second_run_skips_existing(tmp_path: Path):
    first = _run(tmp_path, "onboard", str(tmp_path))
    second = _run(tmp_path, "onboard", str(tmp_path))
    assert first.exit_code == 0, first.output
    assert second.exit_code == 0, second.output
    assert "Skipped:" in second.output
    assert "docs/canonical/product_scope.md" in second.output


def test_phase13_scanner_detects_languages(tmp_path: Path):
    _write(tmp_path / "src" / "app.py")
    _write(tmp_path / "src" / "worker.py")
    _write(tmp_path / "web" / "app.tsx")
    result = CodebaseScanner(tmp_path).scan()
    assert result.primary_languages == ["Python", "TypeScript"]


def test_phase13_scanner_detects_adapters(tmp_path: Path):
    _write(tmp_path / "src" / "app.py")
    _write(tmp_path / "web" / "app.tsx")
    _write(tmp_path / "docs" / "readme.md")
    _write(tmp_path / "data" / "sheet.csv")
    result = CodebaseScanner(tmp_path).scan()
    assert result.applicable_adapters == [
        "code_adapter",
        "frontend_adapter",
        "docs_adapter",
        "spreadsheet_adapter",
    ]


def test_phase13_scanner_detects_key_files(tmp_path: Path):
    _write(tmp_path / "README.md")
    _write(tmp_path / "pyproject.toml")
    _write(tmp_path / "package.json")
    _write(tmp_path / "Makefile")
    result = CodebaseScanner(tmp_path).scan()
    assert result.key_files == ["Makefile", "README.md", "package.json", "pyproject.toml"]


def test_phase13_scanner_detects_ci_configs(tmp_path: Path):
    _write(tmp_path / ".github" / "workflows" / "ci.yml")
    _write(tmp_path / ".gitlab-ci.yml")
    _write(tmp_path / ".circleci" / "config.yml")
    result = CodebaseScanner(tmp_path).scan()
    assert result.ci_configs == [
        ".circleci/config.yml",
        ".github/workflows/ci.yml",
        ".gitlab-ci.yml",
    ]


def test_phase13_scanner_ignores_generated_directories(tmp_path: Path):
    _write(tmp_path / ".git" / "config")
    _write(tmp_path / "node_modules" / "pkg" / "index.js")
    _write(tmp_path / ".venv" / "bin" / "activate")
    _write(tmp_path / "src" / "main.py")
    result = CodebaseScanner(tmp_path).scan()
    assert result.primary_languages == ["Python"]


def test_phase13_scanner_collects_docs_sorted(tmp_path: Path):
    _write(tmp_path / "docs" / "z.md")
    _write(tmp_path / "README.md")
    _write(tmp_path / "docs" / "a.md")
    result = CodebaseScanner(tmp_path).scan()
    assert result.documentation_files == ["README.md", "docs/a.md", "docs/z.md"]


def test_phase13_doc_generator_creates_expected_files(tmp_path: Path):
    scan = ScanResult(root=str(tmp_path), primary_languages=["Python"], applicable_adapters=["code_adapter"])
    manifest = OnboardDocGenerator(tmp_path).generate(scan)
    assert sorted(manifest.created) == [
        "docs/canonical/architecture.md",
        "docs/canonical/product_scope.md",
        "docs/working/backlog.md",
        "docs/working/open_questions.md",
    ]


def test_phase13_doc_generator_dry_run_writes_nothing(tmp_path: Path):
    scan = ScanResult(root=str(tmp_path), primary_languages=["Python"], applicable_adapters=["code_adapter"])
    manifest = OnboardDocGenerator(tmp_path).generate(scan, dry_run=True)
    assert len(manifest.created) == 4
    assert not (tmp_path / "docs").exists()


def test_phase13_doc_generator_additive_skip_behavior(tmp_path: Path):
    existing = tmp_path / "docs" / "working" / "backlog.md"
    _write(existing, "existing backlog")
    scan = ScanResult(root=str(tmp_path), primary_languages=["Python"], applicable_adapters=["code_adapter"])
    manifest = OnboardDocGenerator(tmp_path).generate(scan)
    assert "docs/working/backlog.md" in manifest.skipped
    assert existing.read_text(encoding="utf-8") == "existing backlog"


def test_phase13_doc_generator_outputs_have_draft_marker(tmp_path: Path):
    scan = ScanResult(root=str(tmp_path), primary_languages=["Python"], applicable_adapters=["code_adapter"])
    OnboardDocGenerator(tmp_path).generate(scan)
    for path in (tmp_path / "docs").rglob("*.md"):
        assert "DRAFT" in path.read_text(encoding="utf-8")


def test_phase13_doc_generator_sparse_scan_adds_gap_questions(tmp_path: Path):
    scan = ScanResult(root=str(tmp_path))
    OnboardDocGenerator(tmp_path).generate(scan)
    content = (tmp_path / "docs" / "working" / "open_questions.md").read_text(encoding="utf-8")
    assert "No documentation detected" in content
    assert "No CI config detected" in content
    assert "No adapter signals detected" in content


def test_phase13_end_to_end_onboard_then_scan_then_generate_additive(tmp_path: Path):
    onboard = _run(tmp_path, "onboard", str(tmp_path))
    assert onboard.exit_code == 0, onboard.output

    _write(tmp_path / "src" / "service.py")
    _write(tmp_path / "web" / "view.tsx")

    scan = CodebaseScanner(tmp_path).scan()
    manifest = OnboardDocGenerator(tmp_path).generate(scan)

    # onboard already seeded these paths; generator should remain additive.
    assert manifest.created == []
    assert sorted(manifest.skipped) == [
        "docs/canonical/architecture.md",
        "docs/canonical/product_scope.md",
        "docs/working/backlog.md",
        "docs/working/open_questions.md",
    ]

