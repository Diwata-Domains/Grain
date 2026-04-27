from __future__ import annotations

import json
from pathlib import Path

import yaml

from grain.adapters.export import render_context_markdown_export
from grain.services.codebase_scanner import CodebaseScanner
from grain.services.context_service import build_context_bundle
from grain.services.onboard_doc_generator import OnboardDocGenerator
from grain.services.orchestration_service import analyze_scope_signals

def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_manifest(root: Path) -> None:
    manifest = {
        "canonical": [
            {
                "id": "workflow_spec",
                "path": "docs/canonical/workflow_spec.md",
                "purpose": "workflow",
                "authority": "highest",
                "editable_by_agents": False,
                "read_when": ["running_tasks"],
            }
        ],
        "working": [],
        "runtime": [],
        "tasks": {},
        "rules": {},
    }
    _write(root / "docs" / "runtime" / "docs_manifest.yaml", yaml.dump(manifest))
    _write(root / "docs" / "canonical" / "workflow_spec.md", "# Workflow Spec\nPhase 18 integration.\n")


def _write_adapter_profiles(root: Path) -> None:
    _write(
        root / "docs" / "runtime" / "adapter_profiles.md",
        """# Adapter Profiles

## 5. Adapter Profiles

### code_adapter
- `adapter_id`: `code_adapter`
- `domain_type`: `code`
- `applies_to`:
  - python
- `context_priority_rules`:
  - prioritize source files

### data_adapter
- `adapter_id`: `data_adapter`
- `domain_type`: `data`
- `applies_to`:
  - notebook
  - parquet
  - model
- `relevant_file_patterns`:
  - `**/*.ipynb`
  - `**/*.parquet`
- `build_or_run_hints`:
  - treat data artifacts as metadata-only
- `test_or_validation_hints`:
  - validate metadata summaries
- `review_focus_hints`:
  - metadata-only behavior
- `context_priority_rules`:
  - prioritize notebooks and lightweight metadata
""",
    )


def _write_notebook(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {},
        "cells": [
            {"cell_type": "markdown", "source": ["# Analysis"], "metadata": {}},
            {"cell_type": "code", "source": ["print('train')"], "outputs": [], "metadata": {}},
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_packet(root: Path, adapter_id: str) -> None:
    _write(
        root / "tasks" / "P18-T01-TASK-0001" / "task.md",
        f"""# Task: Phase 18 Integration

## Metadata
- **ID:** TASK-0001
- **Status:** in_progress
- **Phase:** Phase 18 — Data Adapter
- **Backlog:** P18-T06
- **Packet Path:** tasks/P18-T01-TASK-0001/
- **Dependencies:** none
- **Primary Adapter:** {adapter_id}
- **Secondary Adapters:** none

## Objective
Review notebook and parquet artifacts for a training workflow.
""",
    )


def test_phase18_data_adapter_flow(tmp_path: Path, monkeypatch):
    _write_manifest(tmp_path)
    _write_adapter_profiles(tmp_path)
    _write_notebook(tmp_path / "analysis.ipynb")
    _write(tmp_path / "data" / "train.parquet", "PAR1")
    _write_packet(tmp_path, "data_adapter")

    monkeypatch.setattr(
        "grain.adapters.export.DataArtifactExtractor.extract",
        lambda self, path: f"# Data Artifact: {path.name}\n- Content policy: metadata-only",
    )

    result, bundle = build_context_bundle(tmp_path, "TASK-0001")
    assert result.ok is True
    assert bundle is not None
    assert "analysis.ipynb" in bundle.export_metadata["sources"]
    assert "data/train.parquet" in bundle.export_metadata["sources"]

    content = render_context_markdown_export(tmp_path, bundle)
    assert "## Source: `analysis.ipynb`" in content
    assert "# Analysis" in content
    assert "## Source: `data/train.parquet`" in content
    assert "- Content policy: metadata-only" in content

    result, payload = analyze_scope_signals(tmp_path, "review notebook parquet model pipeline")
    assert result.ok is True
    assert payload is not None
    assert "data_adapter" in payload["active_adapters"]

    scan = CodebaseScanner(tmp_path).scan()
    assert "data_adapter" in scan.applicable_adapters
    assert not any("data_adapter" in hint for hint in scan.custom_adapter_hints)

    OnboardDocGenerator(tmp_path).generate(scan)
    backlog = (tmp_path / "docs" / "working" / "backlog.md").read_text(encoding="utf-8")
    product_scope = (tmp_path / "docs" / "canonical" / "product_scope.md").read_text(encoding="utf-8")
    assert "data_adapter" in backlog
    assert "data_adapter" in product_scope
