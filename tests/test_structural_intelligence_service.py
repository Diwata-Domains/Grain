"""Tests for deterministic structural entity extraction service."""

from pathlib import Path

from grain.services.structural_intelligence_service import (
    extract_structural_entities,
    extract_structural_entities_for_files,
)


def test_extract_python_entities_includes_functions_classes_imports_and_calls(tmp_path: Path):
    path = tmp_path / "module.py"
    path.write_text(
        """import os
from pathlib import Path

class Worker:
    def run(self):
        print("ok")

def build():
    worker = Worker()
    worker.run()
""",
        encoding="utf-8",
    )

    extraction = extract_structural_entities(path)
    names_by_type = {(entity.entity_type, entity.name) for entity in extraction.entities}

    assert extraction.language == "python"
    assert extraction.parser == "tree-sitter"
    assert ("class", "Worker") in names_by_type
    assert ("function", "run") in names_by_type
    assert ("function", "build") in names_by_type
    assert ("import", "os") in names_by_type
    assert ("import", "pathlib.Path") in names_by_type
    assert any(item[0] == "call_site" for item in names_by_type)


def test_extract_frontend_entities_includes_imports_and_calls(tmp_path: Path):
    path = tmp_path / "app.tsx"
    path.write_text(
        """import React from "react";

function renderApp() {
  console.log("render");
}
""",
        encoding="utf-8",
    )

    extraction = extract_structural_entities(path)
    names_by_type = {(entity.entity_type, entity.name) for entity in extraction.entities}

    assert extraction.language in {"typescript", "tsx"}
    assert extraction.parser == "tree-sitter"
    assert ("import", "react") in names_by_type
    assert ("function", "renderApp") in names_by_type
    assert any(item[0] == "call_site" and item[1].endswith("log") for item in names_by_type)


def test_extract_markdown_entities_includes_headings_and_links(tmp_path: Path):
    path = tmp_path / "README.md"
    path.write_text(
        """# Title
See [Architecture](docs/canonical/architecture.md).
""",
        encoding="utf-8",
    )

    extraction = extract_structural_entities(path)
    names_by_type = {(entity.entity_type, entity.name) for entity in extraction.entities}

    assert extraction.language == "markdown"
    assert extraction.parser == "tree-sitter"
    assert ("heading", "Title") in names_by_type
    assert ("link", "docs/canonical/architecture.md") in names_by_type


def test_extract_devops_entities_includes_dependency_declarations(tmp_path: Path):
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text(
        """FROM python:3.12-slim
RUN pip install -r requirements.txt
""",
        encoding="utf-8",
    )
    yaml_file = tmp_path / "compose.yaml"
    yaml_file.write_text(
        """services:
  api:
    depends_on:
      - db
      - redis
""",
        encoding="utf-8",
    )

    docker_extraction = extract_structural_entities(dockerfile)
    yaml_extraction = extract_structural_entities(yaml_file)

    docker_deps = [entity.name for entity in docker_extraction.entities if entity.entity_type == "dependency"]
    yaml_deps = [entity.name for entity in yaml_extraction.entities if entity.entity_type == "dependency"]

    assert docker_extraction.language == "dockerfile"
    assert docker_extraction.parser == "tree-sitter"
    assert "python:3.12-slim" in docker_deps
    assert yaml_extraction.language == "yaml"
    assert yaml_extraction.parser == "tree-sitter"
    assert yaml_deps == ["db", "redis"]


def test_extract_structural_entities_for_files_skips_missing_paths(tmp_path: Path):
    (tmp_path / "src").mkdir()
    file_path = tmp_path / "src" / "mod.py"
    file_path.write_text("def fn():\n    return 1\n", encoding="utf-8")

    results = extract_structural_entities_for_files(
        tmp_path,
        ["src/mod.py", "src/missing.py"],
    )

    assert len(results) == 1
    assert results[0].file_path.endswith("src/mod.py")
