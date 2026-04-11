"""Tests for `forge context build` command."""

import json

import yaml
from click.testing import CliRunner

from grain.cli import main
from grain.services.task_service import create_packet_directory


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


def test_context_build_exits_zero(packet_repo):
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
    create_packet_directory(packet_repo, phase=4, task_num=5)

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(packet_repo), "context", "build", "--id", "TASK-0001"],
    )
    assert result.exit_code == 0, result.output
    assert "context build: ok" in result.output
    assert "workflow_spec.md" in result.output


def test_context_build_json_output(packet_repo):
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
    create_packet_directory(packet_repo, phase=4, task_num=5)

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--repo",
            str(packet_repo),
            "--format",
            "json",
            "context",
            "build",
            "--id",
            "TASK-0001",
        ],
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["bundle"]["task_id"] == "TASK-0001"
    assert data["bundle"]["selected_canonical_docs"][0]["id"] == "workflow_spec"
    assert "generated_at" in data["bundle"]["export_metadata"]
    assert "sources" in data["bundle"]["export_metadata"]


def test_context_build_include_working(packet_repo):
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
    create_packet_directory(packet_repo, phase=4, task_num=5)

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--repo",
            str(packet_repo),
            "context",
            "build",
            "--id",
            "TASK-0001",
            "--include-working",
            "--tag",
            "selecting_tasks",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "working_docs      1" in result.output
    assert "docs/working/backlog.md" in result.output


def test_context_build_unknown_task_exits_two(packet_repo):
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
        ["--repo", str(packet_repo), "context", "build", "--id", "TASK-9999"],
    )
    assert result.exit_code == 2, result.output


def test_context_build_shows_adapter_hints_when_primary_adapter_active(packet_repo):
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
        ["--repo", str(packet_repo), "context", "build", "--id", "TASK-0001"],
    )
    assert result.exit_code == 0, result.output
    assert "primary_adapter   code_adapter" in result.output
    assert "review_hints      1" in result.output
    assert "validation_hints  1" in result.output
