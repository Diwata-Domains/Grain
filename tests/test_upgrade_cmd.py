"""Tests for grain upgrade command and upgrade service."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from grain.cli import main
from grain.services.upgrade_service import upgrade_repo, _PROTECTED, _unified_diff


def _run(tmp_path: Path, *args: str):
    runner = CliRunner()
    return runner.invoke(main, ["--repo", str(tmp_path), *args])


def _write(path: Path, content: str = "old content") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# --- Unit tests ---

def test_upgrade_updates_stale_prompt(tmp_path: Path):
    target = tmp_path / "prompts" / "task.execute.md"
    _write(target, "old hollow wrapper content")

    result = upgrade_repo(tmp_path, allow_customized_updates=True)

    assert "prompts/task.execute.md" in result.updated
    assert "Read" in target.read_text(encoding="utf-8")


def test_upgrade_adds_missing_prompt(tmp_path: Path):
    result = upgrade_repo(tmp_path)

    assert "prompts/task.execute.md" in result.added
    assert (tmp_path / "prompts" / "task.execute.md").exists()


def test_upgrade_marks_unchanged_when_already_current(tmp_path: Path):
    # First upgrade to get current content
    upgrade_repo(tmp_path)
    # Second upgrade — everything should be unchanged
    result = upgrade_repo(tmp_path)

    assert not result.updated
    assert not result.added
    assert "prompts/task.execute.md" in result.unchanged


def test_upgrade_dry_run_does_not_write(tmp_path: Path):
    result = upgrade_repo(tmp_path, dry_run=True)

    assert result.added  # would have been added
    assert not (tmp_path / "prompts" / "task.execute.md").exists()


def test_upgrade_never_touches_protected_files(tmp_path: Path):
    manifest = tmp_path / "docs" / "runtime" / "docs_manifest.yaml"
    adapter_profiles = tmp_path / "docs" / "runtime" / "adapter_profiles.md"
    _write(manifest, "user manifest content")
    _write(adapter_profiles, "user adapter content")

    upgrade_repo(tmp_path)

    assert manifest.read_text(encoding="utf-8") == "user manifest content"
    assert adapter_profiles.read_text(encoding="utf-8") == "user adapter content"


def test_upgrade_protected_list_always_returned(tmp_path: Path):
    result = upgrade_repo(tmp_path)

    for p in _PROTECTED:
        assert p in result.protected


def test_upgrade_adds_missing_implementation_plan(tmp_path: Path):
    result = upgrade_repo(tmp_path)

    assert "docs/working/implementation_plan.md" in result.added
    assert (tmp_path / "docs" / "working" / "implementation_plan.md").exists()


def test_upgrade_does_not_overwrite_existing_implementation_plan(tmp_path: Path):
    plan = tmp_path / "docs" / "working" / "implementation_plan.md"
    _write(plan, "# My custom plan\n\nPhase 1 tasks...")

    upgrade_repo(tmp_path)

    assert plan.read_text(encoding="utf-8") == "# My custom plan\n\nPhase 1 tasks..."


def test_upgrade_adds_tasks_next_and_implement_if_missing(tmp_path: Path):
    result = upgrade_repo(tmp_path)

    assert "prompts/tasks.next_and_implement.md" in result.added
    assert (tmp_path / "prompts" / "tasks.next_and_implement.md").exists()


# --- CLI tests ---

def test_upgrade_cmd_help_works(tmp_path: Path):
    result = _run(tmp_path, "upgrade", "--help")
    assert result.exit_code == 0
    assert "upgrade" in result.output


def test_upgrade_cmd_text_output_has_sections(tmp_path: Path):
    result = _run(tmp_path, "upgrade")
    assert result.exit_code == 0
    assert "upgrade: ok" in result.output
    assert "Updated:" in result.output
    assert "Added:" in result.output
    assert "Unchanged:" in result.output
    assert "Protected (not touched):" in result.output


def test_upgrade_cmd_dry_run_reports_without_writing(tmp_path: Path):
    result = _run(tmp_path, "upgrade", "--dry-run")
    assert result.exit_code == 0
    assert "dry-run" in result.output
    assert not (tmp_path / "prompts" / "task.execute.md").exists()


def test_upgrade_cmd_json_output_matches_contract(tmp_path: Path):
    import json
    result = _run(tmp_path, "upgrade", "--format", "json")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "updated" in data
    assert "added" in data
    assert "unchanged" in data
    assert "protected" in data
    assert "skipped_customized" in data
    assert "dry_run" in data


def test_upgrade_cmd_idempotent_on_second_run(tmp_path: Path):
    _run(tmp_path, "upgrade")
    result = _run(tmp_path, "upgrade")
    assert result.exit_code == 0
    assert "(none)" in result.output  # nothing updated or added second time


# --- diff tests ---

def test_upgrade_diff_flag_shows_diff_without_writing(tmp_path: Path):
    target = tmp_path / "prompts" / "task.execute.md"
    _write(target, "old content that differs from bundled")

    result = _run(tmp_path, "upgrade", "--diff")

    assert result.exit_code == 0
    assert "upgrade: diff" in result.output
    assert "prompts/task.execute.md" in result.output
    assert not target.read_text(encoding="utf-8") == ""  # still has old content
    assert target.read_text(encoding="utf-8") == "old content that differs from bundled"


def test_upgrade_diff_shows_removed_and_added_lines(tmp_path: Path):
    target = tmp_path / "prompts" / "task.execute.md"
    _write(target, "old line that will be removed\n")

    result = _run(tmp_path, "upgrade", "--diff")

    assert result.exit_code == 0
    assert "-old line that will be removed" in result.output


def test_upgrade_diff_json_includes_diffs_key(tmp_path: Path):
    import json
    target = tmp_path / "prompts" / "task.execute.md"
    _write(target, "stale content")

    result = _run(tmp_path, "upgrade", "--diff", "--format", "json")

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "diffs" in data
    assert "prompts/task.execute.md" in data["diffs"]
    assert data["diffs"]["prompts/task.execute.md"] != ""


def test_upgrade_include_diffs_populates_result(tmp_path: Path):
    target = tmp_path / "prompts" / "task.execute.md"
    _write(target, "stale content")

    result = upgrade_repo(tmp_path, dry_run=True, include_diffs=True)

    assert "prompts/task.execute.md" in result.diffs
    diff = result.diffs["prompts/task.execute.md"]
    assert "-stale content" in diff
    assert "+++" in diff


def test_upgrade_no_diffs_when_flag_not_set(tmp_path: Path):
    target = tmp_path / "prompts" / "task.execute.md"
    _write(target, "stale content")

    result = upgrade_repo(tmp_path)

    assert result.diffs == {}


def test_upgrade_skips_customized_file_by_default(tmp_path: Path):
    target = tmp_path / "prompts" / "task.execute.md"
    _write(target, "custom local line\n")

    result = upgrade_repo(tmp_path)

    assert "prompts/task.execute.md" in result.customized
    assert "prompts/task.execute.md" in result.skipped_customized
    assert target.read_text(encoding="utf-8") == "custom local line\n"


def test_upgrade_can_apply_customized_file_when_explicitly_allowed(tmp_path: Path):
    target = tmp_path / "prompts" / "task.execute.md"
    _write(target, "custom local line\n")

    result = upgrade_repo(tmp_path, allow_customized_updates=True)

    assert "prompts/task.execute.md" in result.customized
    assert "prompts/task.execute.md" not in result.skipped_customized
    assert "Read" in target.read_text(encoding="utf-8")


def test_upgrade_cmd_text_output_lists_skipped_customized_files(tmp_path: Path):
    target = tmp_path / "prompts" / "task.execute.md"
    _write(target, "custom local line\n")

    result = _run(tmp_path, "upgrade")

    assert result.exit_code == 0
    assert "Skipped Customized:" in result.output
    assert "prompts/task.execute.md" in result.output


def test_unified_diff_helper_shows_delta():
    diff = _unified_diff("some/file.md", "line A\nline B\n", "line A\nline C\n")
    assert "-line B" in diff
    assert "+line C" in diff


# --- content quality tests ---

def test_project_rules_does_not_contain_grain_description(tmp_path: Path):
    """Bundled PROJECT_RULES.md must not describe Grain itself."""
    upgrade_repo(tmp_path)
    content = (tmp_path / "docs" / "runtime" / "PROJECT_RULES.md").read_text(encoding="utf-8")
    assert "CLI-first toolkit" not in content
    assert "workflow orchestrator" not in content


def test_agent_profiles_does_not_say_for_grain(tmp_path: Path):
    """Bundled agent_profiles.md must say 'for this project', not 'for Grain'."""
    upgrade_repo(tmp_path)
    content = (tmp_path / "docs" / "runtime" / "agent_profiles.md").read_text(encoding="utf-8")
    assert "for Grain" not in content
    assert "for this project" in content
