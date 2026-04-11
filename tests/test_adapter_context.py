"""Adapter-system tests for context assembly behavior."""

import yaml

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


def _write_adapter_profiles(repo_root):
    profiles_path = repo_root / "docs" / "runtime" / "adapter_profiles.md"
    profiles_path.parent.mkdir(parents=True, exist_ok=True)
    profiles_path.write_text(
        """# Adapter Profiles

## 5. Adapter Profiles

### code_adapter
- `adapter_id`: `code_adapter`
- `domain_type`: `code`
- `applies_to`:
  - Python
- `relevant_file_patterns`:
  - `src/**`
- `test_or_validation_hints`:
  - run focused tests first
- `review_focus_hints`:
  - behavior regressions
""",
        encoding="utf-8",
    )


def _write_workflow_doc(repo_root):
    workflow_path = repo_root / "docs" / "canonical" / "workflow_spec.md"
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text("# Workflow Spec\n", encoding="utf-8")


def test_context_bundle_is_adapter_neutral_when_primary_adapter_is_none(packet_repo):
    _write_manifest(packet_repo)
    _write_adapter_profiles(packet_repo)
    _write_workflow_doc(packet_repo)
    (packet_repo / "src").mkdir(parents=True, exist_ok=True)
    (packet_repo / "src" / "main.py").write_text("print('hi')\n", encoding="utf-8")
    create_packet_directory(packet_repo, phase=6, task_num=7)

    result, bundle = build_context_bundle(packet_repo, "TASK-0001")

    assert result.ok is True
    assert bundle is not None
    adapter_context = bundle.export_metadata["adapter_context"]
    assert adapter_context["primary_adapter"] == "none"
    assert adapter_context["applied"] is False
    assert adapter_context["selected_sources"] == []
    assert adapter_context["review_focus_hints"] == []
    assert adapter_context["test_or_validation_hints"] == []
    assert "src/main.py" not in bundle.export_metadata["sources"]


def test_context_bundle_handles_unknown_adapter_without_failure(packet_repo):
    _write_manifest(packet_repo)
    _write_adapter_profiles(packet_repo)
    _write_workflow_doc(packet_repo)
    create_packet_directory(packet_repo, phase=6, task_num=7)

    task_md = packet_repo / "tasks" / "P6-T07-TASK-0001" / "task.md"
    task_md.write_text(
        task_md.read_text(encoding="utf-8").replace(
            "- **Primary Adapter:** none",
            "- **Primary Adapter:** unknown_adapter",
        ),
        encoding="utf-8",
    )

    result, bundle = build_context_bundle(packet_repo, "TASK-0001")

    assert result.ok is True
    assert bundle is not None
    adapter_context = bundle.export_metadata["adapter_context"]
    assert adapter_context["primary_adapter"] == "unknown_adapter"
    assert adapter_context["applied"] is False
    assert adapter_context["selected_sources"] == []
    assert adapter_context["review_focus_hints"] == []
    assert adapter_context["test_or_validation_hints"] == []
