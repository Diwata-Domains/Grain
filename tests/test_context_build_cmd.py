"""Tests for `forge context build` command."""

import json

import yaml
from click.testing import CliRunner

from forge.cli import main
from forge.services.task_service import create_packet_directory


def _write_manifest(repo_root, manifest_dict):
    manifest_path = repo_root / "docs" / "runtime" / "docs_manifest.yaml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(yaml.dump(manifest_dict))


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
