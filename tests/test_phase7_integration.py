"""Focused integration tests for Phase 7 new-project onboarding flow.

Covers: scaffolding, adapter selection, starter-packet bootstrap, and
the combined golden path — individually and end-to-end.
"""

import json
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main

_EXPECTED_SEED_FILES = [
    "docs/runtime/PROJECT_RULES.md",
    "docs/runtime/docs_manifest.yaml",
    "docs/runtime/adapter_profiles.md",
    "templates/tasks/task.md",
    "templates/tasks/task_packet.md",
]

_EXPECTED_DIRS = [
    "docs/canonical",
    "docs/working",
    "docs/runtime",
    "tasks",
    "templates/tasks",
]


# --- scaffolding ---


def test_forge_init_creates_required_dirs(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "init"])
    assert result.exit_code == 0, result.output
    for rel in _EXPECTED_DIRS:
        assert (tmp_path / rel).is_dir(), f"missing dir: {rel}"


def test_forge_init_seeds_runtime_and_template_files(tmp_path):
    runner = CliRunner()
    runner.invoke(main, ["--repo", str(tmp_path), "init"])
    for rel in _EXPECTED_SEED_FILES:
        assert (tmp_path / rel).is_file(), f"missing seed file: {rel}"


def test_forge_init_is_idempotent(tmp_path):
    runner = CliRunner()
    r1 = runner.invoke(main, ["--repo", str(tmp_path), "init"])
    r2 = runner.invoke(main, ["--repo", str(tmp_path), "init"])
    assert r1.exit_code == 0
    assert r2.exit_code == 0


# --- adapter selection ---


def test_forge_init_valid_primary_adapter_surfaces_in_output(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(tmp_path), "init", "--primary-adapter", "code_adapter"]
    )
    assert result.exit_code == 0, result.output
    assert "primary=code_adapter" in result.output


def test_forge_init_valid_secondary_adapter_surfaces_in_output(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "init",
         "--primary-adapter", "code_adapter",
         "--secondary-adapter", "frontend_adapter"],
    )
    assert result.exit_code == 0, result.output
    assert "secondary=frontend_adapter" in result.output


def test_forge_init_unknown_adapter_warns_but_exits_zero(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(tmp_path), "init", "--primary-adapter", "ghost_adapter"]
    )
    assert result.exit_code == 0, result.output
    assert "ghost_adapter" in result.output


def test_forge_init_no_adapter_produces_no_adapter_output(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "init"])
    assert result.exit_code == 0
    assert "primary=" not in result.output
    assert "secondary=" not in result.output


# --- bootstrap ---


def test_forge_init_bootstrap_creates_starter_packet(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "init", "--bootstrap"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "tasks" / "P1-T01-TASK-0001").is_dir()
    assert (tmp_path / "tasks" / "P1-T01-TASK-0001" / "task.md").is_file()


def test_forge_init_bootstrap_creates_current_task_md_as_ready(tmp_path):
    runner = CliRunner()
    runner.invoke(main, ["--repo", str(tmp_path), "init", "--bootstrap"])
    current_task = tmp_path / "docs" / "working" / "current_task.md"
    assert current_task.is_file()
    content = current_task.read_text(encoding="utf-8")
    assert "TASK-0001" in content
    assert "Status: ready" in content


def test_forge_init_bootstrap_surfaces_task_id_in_text_output(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "init", "--bootstrap"])
    assert result.exit_code == 0, result.output
    assert "bootstrap" in result.output
    assert "TASK-0001" in result.output


# --- golden path: combined ---


def test_phase7_onboarding_init_with_adapters_and_bootstrap(tmp_path):
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "--repo",
            str(tmp_path),
            "--format",
            "json",
            "init",
            "--primary-adapter",
            "code_adapter",
            "--secondary-adapter",
            "frontend_adapter",
            "--bootstrap",
        ],
    )
    assert result.exit_code == 0, result.output

    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["primary_adapter"] == "code_adapter"
    assert "frontend_adapter" in data["secondary_adapters"]
    assert data["bootstrapped_task_id"] == "TASK-0001"

    # Scaffolding + seed files
    assert (tmp_path / "docs" / "runtime" / "PROJECT_RULES.md").exists()
    assert (tmp_path / "templates" / "tasks" / "task_packet.md").exists()

    # Bootstrap artifacts
    packet_dir = tmp_path / "tasks" / "P1-T01-TASK-0001"
    assert packet_dir.is_dir()
    task_md = packet_dir / "task.md"
    assert task_md.exists()
    assert "**Primary Adapter:** code_adapter" in task_md.read_text(encoding="utf-8")

    current_task = tmp_path / "docs" / "working" / "current_task.md"
    assert current_task.exists()
    current_task_text = current_task.read_text(encoding="utf-8")
    assert "Task ID: TASK-0001" in current_task_text
    assert "Status: ready" in current_task_text


def test_phase7_onboarding_init_dry_run_reports_without_writing(tmp_path):
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "--repo",
            str(tmp_path),
            "--format",
            "json",
            "init",
            "--dry-run",
            "--primary-adapter",
            "code_adapter",
            "--bootstrap",
        ],
    )
    assert result.exit_code == 0, result.output

    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["primary_adapter"] == "code_adapter"
    assert data["bootstrapped_task_id"] == "TASK-0001"
    assert any("dry-run" in w for w in data["warnings"])

    # Dry-run must not write.
    assert not (tmp_path / "docs" / "runtime" / "PROJECT_RULES.md").exists()
    assert not (tmp_path / "tasks" / "P1-T01-TASK-0001").exists()
    assert not (tmp_path / "docs" / "working" / "current_task.md").exists()


# --- JSON output ---


def test_forge_init_json_includes_adapter_and_bootstrap_fields(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "--format", "json",
         "init", "--primary-adapter", "code_adapter", "--bootstrap"],
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["primary_adapter"] == "code_adapter"
    assert data["bootstrapped_task_id"] == "TASK-0001"


# --- onboarding prompt surface ---


def test_workflow_onboard_new_prompt_exists():
    prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "workflow.onboard.new.md"
    assert prompt_path.is_file(), "prompts/workflow.onboard.new.md is missing"


def test_workflow_onboard_new_prompt_has_required_sections():
    prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "workflow.onboard.new.md"
    content = prompt_path.read_text(encoding="utf-8")
    assert "Primary Adapter" in content
    assert "Required Output" in content
    assert "Run Mode" in content
