"""Tests for Jupyter notebook extraction and code adapter context wiring."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from grain.adapters.export import render_context_markdown_export
from grain.services.context_service import build_context_bundle
from grain.services.notebook_extractor import NotebookExtractor
from grain.services.task_service import create_packet_directory


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_notebook(path: Path, cells: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    nb = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {},
        "cells": cells,
    }
    path.write_text(json.dumps(nb), encoding="utf-8")


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
    path = root / "docs" / "runtime" / "docs_manifest.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(manifest), encoding="utf-8")
    _write(root / "docs" / "canonical" / "workflow_spec.md", "# Workflow Spec\n")


def _write_notebook_adapter_profile(root: Path) -> None:
    # Uses docs_adapter (no graph trace required) with ipynb patterns to test
    # the context pipeline without tree-sitter dependency.
    _write(
        root / "docs" / "runtime" / "adapter_profiles.md",
        """# Adapter Profiles

## 5. Adapter Profiles

### docs_adapter
- `adapter_id`: `docs_adapter`
- `domain_type`: `docs`
- `applies_to`:
  - Jupyter notebooks
- `relevant_file_patterns`:
  - `**/*.ipynb`
- `context_priority_rules`:
  - prioritize canonical docs first
- `test_or_validation_hints`:
  - validate notebook outputs
""",
    )


def _set_primary_adapter(root: Path, packet_dir_name: str, adapter_id: str) -> None:
    task_md = root / "tasks" / packet_dir_name / "task.md"
    task_md.write_text(
        task_md.read_text(encoding="utf-8").replace(
            "- **Primary Adapter:** none",
            f"- **Primary Adapter:** {adapter_id}",
        ),
        encoding="utf-8",
    )


# --- Unit tests ---

def test_extract_markdown_cell(tmp_path: Path):
    nb_path = tmp_path / "analysis.ipynb"
    _write_notebook(nb_path, [
        {"cell_type": "markdown", "source": ["# Introduction\n", "Some text."], "metadata": {}},
    ])
    text = NotebookExtractor().extract(nb_path)
    assert "# Notebook: analysis.ipynb" in text
    assert "# Introduction" in text
    assert "Some text." in text


def test_extract_code_cell(tmp_path: Path):
    nb_path = tmp_path / "model.ipynb"
    _write_notebook(nb_path, [
        {"cell_type": "code", "source": ["import pandas as pd\n", "df = pd.DataFrame()"], "outputs": [], "metadata": {}},
    ])
    text = NotebookExtractor().extract(nb_path)
    assert "## Cell 1 [code]" in text
    assert "import pandas as pd" in text
    assert "df = pd.DataFrame()" in text


def test_extract_code_cell_with_stream_output(tmp_path: Path):
    nb_path = tmp_path / "run.ipynb"
    _write_notebook(nb_path, [
        {
            "cell_type": "code",
            "source": ["print('hello')"],
            "outputs": [{"output_type": "stream", "name": "stdout", "text": ["hello\n"]}],
            "metadata": {},
        },
    ])
    text = NotebookExtractor().extract(nb_path)
    assert "**Output:**" in text
    assert "hello" in text


def test_extract_code_cell_with_execute_result(tmp_path: Path):
    nb_path = tmp_path / "result.ipynb"
    _write_notebook(nb_path, [
        {
            "cell_type": "code",
            "source": ["1 + 1"],
            "outputs": [{"output_type": "execute_result", "data": {"text/plain": ["2"]}, "metadata": {}, "execution_count": 1}],
            "metadata": {},
        },
    ])
    text = NotebookExtractor().extract(nb_path)
    assert "**Output:**" in text
    assert "2" in text


def test_extract_code_cell_with_error_output(tmp_path: Path):
    nb_path = tmp_path / "err.ipynb"
    _write_notebook(nb_path, [
        {
            "cell_type": "code",
            "source": ["raise ValueError('bad')"],
            "outputs": [{"output_type": "error", "ename": "ValueError", "evalue": "bad", "traceback": []}],
            "metadata": {},
        },
    ])
    text = NotebookExtractor().extract(nb_path)
    assert "ValueError: bad" in text


def test_extract_raw_cell(tmp_path: Path):
    nb_path = tmp_path / "raw.ipynb"
    _write_notebook(nb_path, [
        {"cell_type": "raw", "source": ["raw content here"], "metadata": {}},
    ])
    text = NotebookExtractor().extract(nb_path)
    assert "## Cell 1 [raw]" in text
    assert "raw content here" in text


def test_extract_empty_notebook_returns_empty_marker(tmp_path: Path):
    nb_path = tmp_path / "empty.ipynb"
    _write_notebook(nb_path, [])
    text = NotebookExtractor().extract(nb_path)
    assert "empty.ipynb is empty" in text


def test_extract_notebook_with_only_blank_cells_returns_empty_marker(tmp_path: Path):
    nb_path = tmp_path / "blank.ipynb"
    _write_notebook(nb_path, [
        {"cell_type": "code", "source": [], "outputs": [], "metadata": {}},
        {"cell_type": "markdown", "source": ["   "], "metadata": {}},
    ])
    text = NotebookExtractor().extract(nb_path)
    assert "blank.ipynb is empty" in text


def test_extract_missing_notebook_returns_warning(tmp_path: Path):
    text = NotebookExtractor().extract(tmp_path / "missing.ipynb")
    assert "could not read missing.ipynb" in text


def test_extract_invalid_json_returns_warning(tmp_path: Path):
    nb_path = tmp_path / "broken.ipynb"
    nb_path.write_text("not valid json", encoding="utf-8")
    text = NotebookExtractor().extract(nb_path)
    assert "could not read broken.ipynb" in text


# --- Integration tests ---

def test_context_bundle_selects_ipynb_sources(packet_repo: Path):
    _write_manifest(packet_repo)
    _write_notebook_adapter_profile(packet_repo)
    _write_notebook(packet_repo / "analysis.ipynb", [
        {"cell_type": "code", "source": ["x = 1"], "outputs": [], "metadata": {}},
    ])
    create_packet_directory(packet_repo, phase=1, task_num=1)
    _set_primary_adapter(packet_repo, "P1-T01-TASK-0001", "docs_adapter")

    result, bundle = build_context_bundle(packet_repo, "TASK-0001")
    assert result.ok is True
    assert bundle is not None
    sources = bundle.export_metadata["sources"]
    assert "analysis.ipynb" in sources


def test_context_export_renders_notebook_content(packet_repo: Path):
    _write_manifest(packet_repo)
    _write_notebook_adapter_profile(packet_repo)
    _write_notebook(packet_repo / "analysis.ipynb", [
        {"cell_type": "markdown", "source": ["# Analysis"], "metadata": {}},
        {"cell_type": "code", "source": ["import pandas as pd"], "outputs": [], "metadata": {}},
    ])
    create_packet_directory(packet_repo, phase=1, task_num=1)
    _set_primary_adapter(packet_repo, "P1-T01-TASK-0001", "docs_adapter")

    result, bundle = build_context_bundle(packet_repo, "TASK-0001")
    assert result.ok is True
    assert bundle is not None

    content = render_context_markdown_export(packet_repo, bundle)
    assert "## Source: `analysis.ipynb`" in content
    assert "# Analysis" in content
    assert "import pandas as pd" in content
