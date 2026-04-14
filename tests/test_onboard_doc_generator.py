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
        content = path.read_text(encoding="utf-8")
        assert "DRAFT" in content, f"{path.name} missing DRAFT marker"


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


def test_product_scope_uses_readme_content_when_available(tmp_path: Path):
    scan = ScanResult(
        root=str(tmp_path.resolve()),
        primary_languages=["Python"],
        applicable_adapters=["code_adapter"],
        existing_doc_content={"README.md": "# My Project\n\nThis project does amazing things."},
    )
    OnboardDocGenerator(tmp_path).generate(scan)

    content = (tmp_path / "docs" / "canonical" / "product_scope.md").read_text(encoding="utf-8")
    assert "From README" in content
    assert "This project does amazing things." in content


def test_product_scope_uses_package_json_description(tmp_path: Path):
    scan = ScanResult(
        root=str(tmp_path.resolve()),
        existing_doc_content={"package.json": "name: my-app\ndescription: A great app\nversion: 1.0.0"},
    )
    OnboardDocGenerator(tmp_path).generate(scan)

    content = (tmp_path / "docs" / "canonical" / "product_scope.md").read_text(encoding="utf-8")
    assert "Project Identity" in content
    assert "my-app" in content


def test_product_scope_falls_back_to_placeholder_when_no_content(tmp_path: Path):
    scan = ScanResult(root=str(tmp_path.resolve()))
    OnboardDocGenerator(tmp_path).generate(scan)

    content = (tmp_path / "docs" / "canonical" / "product_scope.md").read_text(encoding="utf-8")
    assert "No README" in content


def test_architecture_uses_existing_arch_doc(tmp_path: Path):
    scan = ScanResult(
        root=str(tmp_path.resolve()),
        existing_doc_content={"architecture.md": "## Subsystems\n\n- API layer\n- Database layer"},
    )
    OnboardDocGenerator(tmp_path).generate(scan)

    content = (tmp_path / "docs" / "canonical" / "architecture.md").read_text(encoding="utf-8")
    assert "From Existing Architecture Doc" in content
    assert "API layer" in content


def test_architecture_falls_back_to_placeholder_when_no_arch_doc(tmp_path: Path):
    scan = ScanResult(root=str(tmp_path.resolve()))
    OnboardDocGenerator(tmp_path).generate(scan)

    content = (tmp_path / "docs" / "canonical" / "architecture.md").read_text(encoding="utf-8")
    assert "No architecture doc found" in content


def test_open_questions_surfaces_found_existing_docs(tmp_path: Path):
    scan = ScanResult(
        root=str(tmp_path.resolve()),
        existing_doc_content={"README.md": "some content", "architecture.md": "arch content"},
        ci_configs=[".github/workflows/ci.yml"],
        documentation_files=["README.md"],
        applicable_adapters=["code_adapter"],
    )
    OnboardDocGenerator(tmp_path).generate(scan)

    content = (tmp_path / "docs" / "working" / "open_questions.md").read_text(encoding="utf-8")
    assert "Existing docs found outside canonical layer" in content
    assert "README.md" in content
    assert "architecture.md" in content


def test_backlog_has_retrospective_review_when_modules_detected(tmp_path: Path):
    scan = ScanResult(
        root=str(tmp_path.resolve()),
        primary_languages=["Python"],
        applicable_adapters=["code_adapter"],
        detected_modules=["src/myapp", "src/myapp/core"],
    )
    OnboardDocGenerator(tmp_path).generate(scan)

    content = (tmp_path / "docs" / "working" / "backlog.md").read_text(encoding="utf-8")
    assert "Retrospective Review Required" in content
    assert "src/myapp" in content
    assert "Audit each module" in content


def test_open_questions_surfaces_code_ahead_of_backlog_when_modules_detected(tmp_path: Path):
    scan = ScanResult(
        root=str(tmp_path.resolve()),
        primary_languages=["Python"],
        applicable_adapters=["code_adapter"],
        detected_modules=["src/grain", "src/grain/cli"],
    )
    OnboardDocGenerator(tmp_path).generate(scan)

    content = (tmp_path / "docs" / "working" / "open_questions.md").read_text(encoding="utf-8")
    assert "Existing code detected" in content
    assert "src/grain" in content


def test_backlog_no_retrospective_when_no_modules(tmp_path: Path):
    scan = ScanResult(root=str(tmp_path.resolve()))
    OnboardDocGenerator(tmp_path).generate(scan)

    content = (tmp_path / "docs" / "working" / "backlog.md").read_text(encoding="utf-8")
    assert "Retrospective Review Required" not in content

