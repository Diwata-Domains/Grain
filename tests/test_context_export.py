"""Tests for context export rendering and write-path behavior."""

import yaml

from forge.adapters.export import render_context_markdown_export, write_context_markdown_export
from forge.services.context_service import build_context_bundle
from forge.services.task_service import create_packet_directory


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
