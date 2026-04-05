"""Tests for `forge docs validate` command."""

import subprocess
import sys
from pathlib import Path

import yaml
from click.testing import CliRunner

from forge.cli import main


def test_docs_validate_passes_on_valid_repo(valid_repo):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(valid_repo), "docs", "validate"])
    assert result.exit_code == 0
    assert "ok" in result.output


def test_docs_validate_fails_when_manifest_missing(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "docs", "validate"])
    assert result.exit_code != 0


def test_docs_validate_reports_schema_error(tmp_path):
    runner = CliRunner()
    # Missing required top-level sections
    (tmp_path / "docs" / "runtime").mkdir(parents=True)
    (tmp_path / "docs" / "runtime" / "docs_manifest.yaml").write_text("version: 1\n")

    result = runner.invoke(main, ["--repo", str(tmp_path), "docs", "validate"])
    assert result.exit_code != 0
    assert "error" in result.output.lower() or "Missing" in result.output


def test_docs_validate_reports_missing_doc_file(valid_repo):
    runner = CliRunner()
    # Remove a declared canonical file after the repo is set up
    (valid_repo / "docs" / "canonical" / "architecture.md").unlink()

    result = runner.invoke(main, ["--repo", str(valid_repo), "docs", "validate"])
    assert result.exit_code != 0
    assert "architecture" in result.output or "architecture" in (result.output + str(result.exception))


def test_docs_validate_json_format(valid_repo):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(valid_repo), "--format", "json", "docs", "validate"])
    assert result.exit_code == 0
    import json
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["command"] == "docs validate"


def test_docs_validate_exit_code_3_on_failure(tmp_path):
    """Exit code 3 requires the cli() wrapper — use subprocess like smoke tests."""
    forge = str(Path(sys.executable).parent / "forge")
    (tmp_path / "docs" / "runtime").mkdir(parents=True)
    (tmp_path / "docs" / "runtime" / "docs_manifest.yaml").write_text("version: 1\n")

    proc = subprocess.run(
        [forge, "--repo", str(tmp_path), "docs", "validate"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 3
