"""Tests for `forge context export` command."""

import json

import yaml
from click.testing import CliRunner

from forge.cli import main
from forge.domain.packets import find_packet_dir
from forge.services.task_service import create_packet_directory


def _write_manifest(repo_root, manifest_dict):
    manifest_path = repo_root / "docs" / "runtime" / "docs_manifest.yaml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(yaml.dump(manifest_dict))


def _write_adapter_profiles(repo_root):
    adapter_profiles = repo_root / "docs" / "runtime" / "adapter_profiles.md"
    adapter_profiles.parent.mkdir(parents=True, exist_ok=True)
    adapter_profiles.write_text(
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
  - run focused tests before full suite
- `review_focus_hints`:
  - behavior regressions
""",
        encoding="utf-8",
    )


def test_context_export_writes_markdown_default(packet_repo):
    _write_manifest(
        packet_repo,
        {
            "canonical": [
                {
                    "id": "workflow_spec",
                    "path": "docs/canonical/workflow_spec.md",
                    "purpose": "Workflow",
                    "authority": "highest",
                    "editable_by_agents": False,
                    "read_when": ["running_tasks"],
                }
            ],
            "working": [],
            "runtime": [],
            "tasks": {},
            "rules": {},
        },
    )
    workflow_doc = packet_repo / "docs" / "canonical" / "workflow_spec.md"
    workflow_doc.parent.mkdir(parents=True, exist_ok=True)
    workflow_doc.write_text("# Workflow\n", encoding="utf-8")
    create_packet_directory(packet_repo, phase=4, task_num=7)

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "context", "export", "--id", "TASK-0001"],
    )
    assert result.exit_code == 0, result.output
    assert "context export: ok" in result.output

    packet_dir = find_packet_dir(packet_repo / "tasks", "TASK-0001")
    export_path = packet_dir / "context_export.md"
    assert export_path.exists()
    content = export_path.read_text(encoding="utf-8")
    assert "# Context Export" in content
    assert "## Sources" in content
    assert "docs/canonical/workflow_spec.md" in content


def test_context_export_writes_markdown_custom_output(packet_repo):
    _write_manifest(
        packet_repo,
        {
            "canonical": [],
            "working": [],
            "runtime": [],
            "tasks": {},
            "rules": {},
        },
    )
    create_packet_directory(packet_repo, phase=4, task_num=7)

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--repo",
            str(packet_repo),
            "context",
            "export",
            "--id",
            "TASK-0001",
            "--output",
            "exports/context.md",
        ],
    )
    assert result.exit_code == 0, result.output
    assert (packet_repo / "exports" / "context.md").exists()


def test_context_export_json_metadata_only(packet_repo):
    _write_manifest(
        packet_repo,
        {
            "canonical": [
                {
                    "id": "workflow_spec",
                    "path": "docs/canonical/workflow_spec.md",
                    "purpose": "Workflow",
                    "authority": "highest",
                    "editable_by_agents": False,
                    "read_when": ["running_tasks"],
                }
            ],
            "working": [],
            "runtime": [],
            "tasks": {},
            "rules": {},
        },
    )
    create_packet_directory(packet_repo, phase=4, task_num=7)

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--repo",
            str(packet_repo),
            "--format",
            "json",
            "context",
            "export",
            "--id",
            "TASK-0001",
        ],
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["export"]["task_id"] == "TASK-0001"
    assert "generated_at" in data["export"]
    assert isinstance(data["export"]["sources"], list)
    assert "content" not in json.dumps(data["export"])

    packet_dir = find_packet_dir(packet_repo / "tasks", "TASK-0001")
    assert not (packet_dir / "context_export.md").exists()


def test_context_export_include_working(packet_repo):
    _write_manifest(
        packet_repo,
        {
            "canonical": [],
            "working": [
                {
                    "id": "backlog",
                    "path": "docs/working/backlog.md",
                    "purpose": "Backlog",
                    "authority": "secondary",
                    "editable_by_agents": True,
                    "read_when": ["selecting_tasks"],
                }
            ],
            "runtime": [],
            "tasks": {},
            "rules": {},
        },
    )
    backlog_doc = packet_repo / "docs" / "working" / "backlog.md"
    backlog_doc.parent.mkdir(parents=True, exist_ok=True)
    backlog_doc.write_text("# Backlog\n", encoding="utf-8")
    create_packet_directory(packet_repo, phase=4, task_num=7)

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--repo",
            str(packet_repo),
            "--format",
            "json",
            "context",
            "export",
            "--id",
            "TASK-0001",
            "--include-working",
            "--tag",
            "selecting_tasks",
        ],
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    kinds = {entry["kind"] for entry in data["export"]["sources"]}
    assert "working" in kinds


def test_context_export_unknown_task_exits_two(packet_repo):
    _write_manifest(
        packet_repo,
        {
            "canonical": [],
            "working": [],
            "runtime": [],
            "tasks": {},
            "rules": {},
        },
    )
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "context", "export", "--id", "TASK-9999"],
    )
    assert result.exit_code == 2, result.output


def test_context_export_json_includes_adapter_hints_when_active(packet_repo):
    _write_manifest(
        packet_repo,
        {
            "canonical": [],
            "working": [],
            "runtime": [],
            "tasks": {},
            "rules": {},
        },
    )
    _write_adapter_profiles(packet_repo)
    src_dir = packet_repo / "src"
    src_dir.mkdir(parents=True, exist_ok=True)
    (src_dir / "main.py").write_text("print('hi')\n", encoding="utf-8")
    create_packet_directory(packet_repo, phase=6, task_num=6)

    task_md = packet_repo / "tasks" / "P6-T06-TASK-0001" / "task.md"
    task_md.write_text(
        task_md.read_text(encoding="utf-8").replace(
            "- **Primary Adapter:** none",
            "- **Primary Adapter:** code_adapter",
        ),
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--repo",
            str(packet_repo),
            "--format",
            "json",
            "context",
            "export",
            "--id",
            "TASK-0001",
        ],
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    adapter_context = data["export"]["adapter_context"]
    assert adapter_context["primary_adapter"] == "code_adapter"
    assert adapter_context["review_focus_hints"] == ["behavior regressions"]
    assert adapter_context["test_or_validation_hints"] == ["run focused tests before full suite"]
