"""Tests for `grain onboard` command and additive scaffold behavior."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main


def _run(tmp_path: Path, *args: str):
    runner = CliRunner()
    return runner.invoke(main, ["--repo", str(tmp_path), *args])


def test_onboard_help_works(tmp_path: Path):
    result = _run(tmp_path, "onboard", "--help")
    assert result.exit_code == 0
    assert "Scaffold Grain directory structure" in result.output


def test_onboard_creates_dirs_and_stubs_on_empty_repo(tmp_path: Path):
    result = _run(tmp_path, "onboard", str(tmp_path))
    assert result.exit_code == 0, result.output

    assert (tmp_path / "docs" / "canonical").is_dir()
    assert (tmp_path / "docs" / "working").is_dir()
    assert (tmp_path / "docs" / "runtime").is_dir()
    assert (tmp_path / "tasks").is_dir()
    assert (tmp_path / "prompts").is_dir()

    stub = tmp_path / "docs" / "canonical" / "product_scope.md"
    assert stub.exists()
    assert "# DRAFT" in stub.read_text(encoding="utf-8")


def test_onboard_does_not_force_cli_or_workflow_canonical_stubs(tmp_path: Path):
    result = _run(tmp_path, "onboard", str(tmp_path))
    assert result.exit_code == 0, result.output

    assert not (tmp_path / "docs" / "canonical" / "cli_spec.md").exists()
    assert not (tmp_path / "docs" / "canonical" / "workflow_spec.md").exists()
    assert not (tmp_path / "docs" / "canonical" / "data_contracts.md").exists()


def test_onboard_skips_existing_files_without_overwriting(tmp_path: Path):
    existing = tmp_path / "docs" / "canonical" / "architecture.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("keep me", encoding="utf-8")

    result = _run(tmp_path, "onboard", str(tmp_path))
    assert result.exit_code == 0, result.output
    assert "docs/canonical/architecture.md" in result.output
    assert existing.read_text(encoding="utf-8") == "keep me"


def test_onboard_dry_run_writes_nothing(tmp_path: Path):
    result = _run(tmp_path, "onboard", str(tmp_path), "--dry-run")
    assert result.exit_code == 0, result.output
    assert "dry_run           true" in result.output
    assert not (tmp_path / "docs").exists()
    assert not (tmp_path / "tasks").exists()


def test_onboard_json_output_matches_contract(tmp_path: Path):
    result = _run(tmp_path, "--format", "json", "onboard", str(tmp_path), "--dry-run")
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert set(payload.keys()) == {"created", "skipped", "root"}
    assert isinstance(payload["created"], list)
    assert isinstance(payload["skipped"], list)
    assert payload["root"] == str(tmp_path.resolve())


def test_onboard_local_format_option_matches_contract(tmp_path: Path):
    result = _run(tmp_path, "onboard", str(tmp_path), "--dry-run", "--format", "json")
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert set(payload.keys()) == {"created", "skipped", "root"}


def test_onboard_text_output_has_created_and_skipped_sections(tmp_path: Path):
    result = _run(tmp_path, "onboard", str(tmp_path), "--dry-run")
    assert result.exit_code == 0, result.output
    assert "Created:" in result.output
    assert "Skipped:" in result.output


def test_onboard_path_defaults_to_repo_root(tmp_path: Path):
    result = _run(tmp_path, "onboard")
    assert result.exit_code == 0, result.output
    assert (tmp_path / "docs").exists()
    assert (tmp_path / "tasks").exists()


def test_onboard_rejects_nonexistent_path(tmp_path: Path):
    missing = tmp_path / "missing-dir"
    result = _run(tmp_path, "onboard", str(missing))
    assert result.exit_code == 2
    assert "existing directory" in result.output


def test_onboard_creates_tooling_notes_with_table_header(tmp_path: Path):
    result = _run(tmp_path, "onboard", str(tmp_path))
    assert result.exit_code == 0, result.output

    tooling_notes = tmp_path / "docs" / "working" / "tooling_notes.md"
    assert tooling_notes.exists()
    content = tooling_notes.read_text(encoding="utf-8")
    assert "| Date | Type | Command | Observation | Severity | Status |" in content


def test_onboard_creates_workflow_metrics(tmp_path: Path):
    result = _run(tmp_path, "onboard", str(tmp_path))
    assert result.exit_code == 0, result.output
    assert (tmp_path / "docs" / "working" / "workflow_metrics.md").exists()


def test_all_stub_files_contain_draft_marker(tmp_path: Path):
    result = _run(tmp_path, "onboard", str(tmp_path))
    assert result.exit_code == 0, result.output

    # These files are functional inboxes/state files, not draft documentation.
    # They do not carry a # DRAFT marker by design.
    _RUNTIME_STATE_FILES = {"current_task.md", "tooling_notes.md"}

    # Only canonical and working stubs carry the DRAFT marker.
    # Runtime docs are seeded from bundled sources and are not DRAFT.
    stub_dirs = ["docs/canonical", "docs/working"]
    for stub_dir in stub_dirs:
        for path in (tmp_path / stub_dir).rglob("*.md"):
            if path.name in _RUNTIME_STATE_FILES:
                continue
            assert "# DRAFT" in path.read_text(encoding="utf-8"), path
