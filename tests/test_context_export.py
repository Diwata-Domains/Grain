"""Tests for context export rendering and write-path behavior."""

import yaml

from grain.adapters.export import render_context_markdown_export, write_context_markdown_export
from grain.services.context_service import build_context_bundle
from grain.services.task_service import create_packet_directory


def _write_manifest(repo_root):
    manifest_path = repo_root / "docs" / "runtime" / "docs_manifest.yaml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        yaml.dump(
            {
                "canonical": [
                    {
                        "id": "workflow_spec",
                        "path": "docs/canonical/workflow_spec.md",
                        "purpose": "Workflow guidance",
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
        ),
        encoding="utf-8",
    )


def _write_doc(repo_root, relative_path, content):
    file_path = repo_root / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")


def _write_adapter_profiles(repo_root):
    _write_doc(
        repo_root,
        "docs/runtime/adapter_profiles.md",
        """# Adapter Profiles

## 5. Adapter Profiles

### data_adapter
- `adapter_id`: `data_adapter`
- `domain_type`: `data`
- `applies_to`:
  - notebook
  - parquet
- `relevant_file_patterns`:
  - `**/*.parquet`
- `test_or_validation_hints`:
  - validate metadata summaries
""",
    )


def _set_primary_adapter(repo_root, packet_dir_name, adapter_id):
    task_md = repo_root / "tasks" / packet_dir_name / "task.md"
    task_md.write_text(
        task_md.read_text(encoding="utf-8").replace(
            "- **Primary Adapter:** none",
            f"- **Primary Adapter:** {adapter_id}",
        ),
        encoding="utf-8",
    )


def test_render_context_markdown_export_includes_sources_and_content(packet_repo):
    _write_manifest(packet_repo)
    _write_doc(packet_repo, "docs/canonical/workflow_spec.md", "# Workflow Spec\nExport body.\n")
    create_packet_directory(packet_repo, phase=4, task_num=13)

    result, bundle = build_context_bundle(packet_repo, "TASK-0001")

    assert result.ok is True
    assert bundle is not None

    content = render_context_markdown_export(packet_repo, bundle)

    assert "# Context Export" in content
    assert "Task ID: TASK-0001" in content
    assert "## Sources" in content
    assert f"- `{bundle.packet_dir.relative_to(packet_repo).as_posix()}/task.md`" in content
    assert "## Source: `docs/canonical/workflow_spec.md`" in content
    assert "Export body." in content


def test_write_context_markdown_export_defaults_to_packet_directory(packet_repo):
    _write_manifest(packet_repo)
    _write_doc(packet_repo, "docs/canonical/workflow_spec.md", "# Workflow Spec\nExport body.\n")
    create_packet_directory(packet_repo, phase=4, task_num=13)

    result, bundle = build_context_bundle(packet_repo, "TASK-0001")

    assert result.ok is True
    assert bundle is not None

    export_path = write_context_markdown_export(packet_repo, bundle)

    assert export_path == bundle.packet_dir / "context_export.md"
    assert export_path.exists()
    assert "Export body." in export_path.read_text(encoding="utf-8")


def test_render_context_markdown_export_includes_adapter_hint_sections(packet_repo):
    _write_manifest(packet_repo)
    _write_doc(packet_repo, "docs/canonical/workflow_spec.md", "# Workflow Spec\nExport body.\n")
    create_packet_directory(packet_repo, phase=4, task_num=13)

    result, bundle = build_context_bundle(packet_repo, "TASK-0001")
    assert result.ok is True
    assert bundle is not None

    bundle.export_metadata["adapter_context"] = {
        "primary_adapter": "code_adapter",
        "review_focus_hints": ["behavior regressions"],
        "test_or_validation_hints": ["run focused tests before full suite"],
    }

    content = render_context_markdown_export(packet_repo, bundle)
    assert "Primary Adapter: code_adapter" in content
    assert "## Adapter Hints" in content
    assert "### Review Focus Hints" in content
    assert "### Test/Validation Hints" in content
    assert "- behavior regressions" in content
    assert "- run focused tests before full suite" in content


def test_render_context_markdown_export_uses_data_artifact_extractor(packet_repo, monkeypatch):
    _write_manifest(packet_repo)
    _write_doc(packet_repo, "docs/canonical/workflow_spec.md", "# Workflow Spec\nExport body.\n")
    _write_adapter_profiles(packet_repo)
    _write_doc(packet_repo, "data/train.parquet", "PAR1")
    create_packet_directory(packet_repo, phase=4, task_num=13)
    _set_primary_adapter(packet_repo, "P4-T13-TASK-0001", "data_adapter")

    monkeypatch.setattr(
        "grain.adapters.export.DataArtifactExtractor.extract",
        lambda self, path: f"# Data Artifact: {path.name}\n- Content policy: metadata-only",
    )

    result, bundle = build_context_bundle(packet_repo, "TASK-0001")
    assert result.ok is True
    assert bundle is not None

    content = render_context_markdown_export(packet_repo, bundle)
    assert "## Source: `data/train.parquet`" in content
    assert "# Data Artifact: train.parquet" in content
    assert "- Content policy: metadata-only" in content
