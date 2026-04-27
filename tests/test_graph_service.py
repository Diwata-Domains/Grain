"""Tests for Phase 10 knowledge graph builder service."""

import json
from pathlib import Path

from grain.services.graph_service import (
    EDGE_CONFIDENCE_VALUES,
    build_and_persist_knowledge_graph,
    build_knowledge_graph,
    persist_knowledge_graph,
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _seed_repo(root: Path) -> None:
    _write(
        root / "docs" / "runtime" / "adapter_profiles.md",
        """# Adapter Profiles

## 5. Adapter Profiles

### code_adapter
- `adapter_id`: `code_adapter`
- `domain_type`: `code`
- `applies_to`:
  - Python
  - backend
- `context_priority_rules`:
  - prioritize source files
""",
    )
    _write(root / "docs" / "canonical" / "architecture.md", "# Architecture\n")
    _write(root / "docs" / "runtime" / "PROJECT_RULES.md", "# Rules\n")
    _write(
        root / "tasks" / "P10-T01-TASK-0079" / "task.md",
        """# Task

## Metadata
- **ID:** TASK-0079
- **Status:** review
- **Phase:** Phase 10
""",
    )
    _write(
        root / "src" / "app.py",
        """import os

def run():
    print("ok")
""",
    )
    _write(
        root / "docs" / "README.md",
        """# Readme
See [Architecture](docs/canonical/architecture.md).
""",
    )
    _write(
        root / "compose.yaml",
        """services:
  api:
    depends_on:
      - db
""",
    )


def test_build_knowledge_graph_creates_nodes_and_confidence_edges(tmp_path: Path):
    _seed_repo(tmp_path)
    result, artifact = build_knowledge_graph(
        tmp_path,
        source_paths=["src/app.py", "docs/README.md", "compose.yaml"],
    )

    assert result.ok is True
    assert artifact is not None
    assert artifact.nodes
    assert artifact.edges
    assert any(node.kind == "file" for node in artifact.nodes)
    assert any(node.kind == "task_packet" for node in artifact.nodes)
    assert any(node.kind == "adapter" for node in artifact.nodes)
    assert all(edge.confidence in EDGE_CONFIDENCE_VALUES for edge in artifact.edges)


def test_persist_knowledge_graph_writes_json_artifact(tmp_path: Path):
    _seed_repo(tmp_path)
    _, artifact = build_knowledge_graph(tmp_path, source_paths=["src/app.py"])
    assert artifact is not None

    result, path = persist_knowledge_graph(tmp_path, artifact)
    assert result.ok is True
    assert path.exists()

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["graph_id"] == artifact.graph_id
    assert isinstance(payload["nodes"], list)
    assert isinstance(payload["edges"], list)


def test_build_and_persist_knowledge_graph_returns_payload(tmp_path: Path):
    _seed_repo(tmp_path)
    result, payload = build_and_persist_knowledge_graph(
        tmp_path,
        source_paths=["src/app.py", "docs/README.md"],
    )

    assert result.ok is True
    assert payload is not None
    assert payload["artifact_path"].endswith(".json")
    assert payload["graph"]["engine"] in {"networkx", "fallback"}


def test_build_knowledge_graph_requires_sources(tmp_path: Path):
    result, artifact = build_knowledge_graph(tmp_path, source_paths=[])
    assert result.ok is False
    assert artifact is None
    assert result.errors == ["source_paths is required"]
