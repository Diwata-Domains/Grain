"""Phase 10 integration tests across extraction, graph, context, and orchestration."""

from __future__ import annotations

import json
from pathlib import Path

from grain.services.context_service import build_context_bundle
from grain.services.graph_service import build_and_persist_knowledge_graph, build_knowledge_graph
from grain.services.orchestration_service import analyze_scope_signals
from grain.services.structural_intelligence_service import extract_structural_entities_for_files


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _seed_runtime_docs(root: Path) -> None:
    _write(
        root / "docs" / "runtime" / "adapter_profiles.md",
        """# Adapter Profiles

## 5. Adapter Profiles

### code_adapter
- `adapter_id`: `code_adapter`
- `domain_type`: `code`
- `applies_to`:
  - python
  - backend
- `relevant_file_patterns`:
  - `src/**`
  - `tests/**`
- `context_priority_rules`:
  - prioritize source files, then tests
- `test_or_validation_hints`:
  - run focused tests
""",
    )
    _write(
        root / "docs" / "runtime" / "docs_manifest.yaml",
        """canonical:
  - id: workflow_spec
    path: docs/canonical/workflow_spec.md
    purpose: Workflow guidance
    authority: highest
    editable_by_agents: false
    read_when: [running_tasks]
working: []
runtime: []
tasks: {}
rules: {}
""",
    )
    _write(root / "docs" / "canonical" / "workflow_spec.md", "# Workflow Spec\n")
    _write(root / "docs" / "runtime" / "PROJECT_RULES.md", "# Rules\n")


def _seed_packet(root: Path) -> None:
    packet = root / "tasks" / "P10-T05-TASK-0001"
    _write(
        packet / "task.md",
        """# Task: Integration pipeline validation

## Metadata
- **ID:** TASK-0001
- **Status:** in_progress
- **Phase:** Phase 10
- **Backlog:** P10-T05
- **Packet Path:** tasks/P10-T05-TASK-0001/
- **Dependencies:** TASK-0082
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none
""",
    )
    _write(packet / "context.md", "# Context\n")
    _write(packet / "plan.md", "# Plan\n")
    _write(packet / "deliverable_spec.md", "# Deliverable\n")


def _seed_sources(root: Path) -> None:
    _write(
        root / "src" / "service.py",
        """import os

def run_service() -> str:
    return os.getcwd()
""",
    )
    _write(
        root / "tests" / "test_service.py",
        """from src.service import run_service

def test_run_service() -> None:
    assert run_service()
""",
    )


def test_phase10_pipeline_integrates_extraction_graph_context_and_orchestration(tmp_path: Path):
    _seed_runtime_docs(tmp_path)
    _seed_packet(tmp_path)
    _seed_sources(tmp_path)

    extractions = extract_structural_entities_for_files(
        tmp_path,
        ["src/service.py", "tests/test_service.py"],
    )
    assert len(extractions) == 2
    assert any(entity.entity_type == "function" for entity in extractions[0].entities)

    graph_result, artifact = build_knowledge_graph(
        tmp_path,
        source_paths=["src/service.py", "tests/test_service.py"],
    )
    assert graph_result.ok is True
    assert artifact is not None
    node_ids = {node.id for node in artifact.nodes}
    assert "file::src/service.py" in node_ids
    assert "adapter::code_adapter" in node_ids

    context_result, bundle = build_context_bundle(tmp_path, "TASK-0001")
    assert context_result.ok is True
    assert bundle is not None
    sources = bundle.export_metadata["sources"]
    assert "src/service.py" in sources
    assert "tests/test_service.py" in sources

    scope_result, scope_payload = analyze_scope_signals(
        tmp_path,
        "update python service behavior and tests",
        adapter_ids=["code_adapter"],
    )
    assert scope_result.ok is True
    assert scope_payload is not None
    assert scope_payload["active_adapters"] == ["code_adapter"]
    adapter_signal = scope_payload["adapter_signals"][0]
    assert adapter_signal["active"] is True
    assert "impact" in adapter_signal
    assert "src/service.py" in adapter_signal["impact"]["affected_files"]


def test_phase10_graph_rebuild_is_derivable_from_source_artifacts(tmp_path: Path):
    _seed_runtime_docs(tmp_path)
    _seed_sources(tmp_path)

    build_one_result, payload_one = build_and_persist_knowledge_graph(
        tmp_path,
        source_paths=["src/service.py", "tests/test_service.py"],
        produced_by="phase10.integration",
    )
    assert build_one_result.ok is True
    assert payload_one is not None

    first_path = tmp_path / payload_one["artifact_path"]
    assert first_path.exists()
    first_path.write_text('{"tampered": true}\n', encoding="utf-8")

    build_two_result, payload_two = build_and_persist_knowledge_graph(
        tmp_path,
        source_paths=["src/service.py", "tests/test_service.py"],
        produced_by="phase10.integration",
    )
    assert build_two_result.ok is True
    assert payload_two is not None

    graph_one = payload_one["graph"]
    graph_two = payload_two["graph"]
    assert graph_one["nodes"] == graph_two["nodes"]
    assert graph_one["edges"] == graph_two["edges"]

    rebuilt_payload = json.loads((tmp_path / payload_two["artifact_path"]).read_text(encoding="utf-8"))
    assert rebuilt_payload["nodes"] == graph_two["nodes"]
    assert rebuilt_payload["edges"] == graph_two["edges"]
