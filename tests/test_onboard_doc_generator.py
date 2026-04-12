"""Tests for onboarding draft doc generation from scan signals."""

from __future__ import annotations

from pathlib import Path

from grain.domain.scan_result import ScanResult
from grain.services.onboard_doc_generator import OnboardDocGenerator


def _scan(root: Path) -> ScanResult:
    return ScanResult(
        root=str(root.resolve()),
        primary_languages=["Python", "TypeScript"],
        language_counts={"Python": 4, "TypeScript": 2},
        applicable_adapters=["code_adapter", "frontend_adapter", "docs_adapter"],
        key_files=["README.md", "pyproject.toml", "package.json"],
        ci_configs=[".github/workflows/ci.yml"],
        documentation_files=["README.md", "docs/architecture.md"],
    )


def test_generate_creates_expected_draft_files(tmp_path: Path):
    manifest = OnboardDocGenerator(tmp_path).generate(_scan(tmp_path))

    assert sorted(manifest.created) == [
        "docs/canonical/architecture.md",
        "docs/canonical/product_scope.md",
        "docs/working/backlog.md",
        "docs/working/open_questions.md",
    ]

    for rel in manifest.created:
        assert (tmp_path / rel).exists()


def test_generate_is_additive_and_skips_existing_files(tmp_path: Path):
    existing = tmp_path / "docs" / "canonical" / "product_scope.md"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("keep me", encoding="utf-8")

    manifest = OnboardDocGenerator(tmp_path).generate(_scan(tmp_path))

    assert "docs/canonical/product_scope.md" in manifest.skipped
    assert existing.read_text(encoding="utf-8") == "keep me"


def test_generate_dry_run_writes_nothing(tmp_path: Path):
    manifest = OnboardDocGenerator(tmp_path).generate(_scan(tmp_path), dry_run=True)

    assert len(manifest.created) == 4
    assert not (tmp_path / "docs").exists()


def test_generated_files_have_draft_marker(tmp_path: Path):
    OnboardDocGenerator(tmp_path).generate(_scan(tmp_path))

    for path in (tmp_path / "docs").rglob("*.md"):
        assert "# DRAFT" in path.read_text(encoding="utf-8")


def test_open_questions_include_gap_driven_entries_when_signals_missing(tmp_path: Path):
    sparse = ScanResult(
        root=str(tmp_path.resolve()),
        primary_languages=[],
        language_counts={},
        applicable_adapters=[],
        key_files=[],
        ci_configs=[],
        documentation_files=[],
    )
    OnboardDocGenerator(tmp_path).generate(sparse)

    content = (tmp_path / "docs" / "working" / "open_questions.md").read_text(encoding="utf-8")
    assert "No documentation detected" in content
    assert "No CI config detected" in content
    assert "No adapter signals detected" in content

