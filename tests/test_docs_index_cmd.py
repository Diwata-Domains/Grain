"""Tests for `forge docs index` command."""

import json
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main


def test_docs_index_writes_file(valid_repo):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(valid_repo), "docs", "index"])
    assert result.exit_code == 0
    index_path = valid_repo / "docs" / "runtime" / "docs_index.md"
    assert index_path.exists()


def test_docs_index_exits_zero(valid_repo):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(valid_repo), "docs", "index"])
    assert result.exit_code == 0
    assert "ok" in result.output


def test_docs_index_written_file_contains_doc_ids(valid_repo):
    runner = CliRunner()
    runner.invoke(main, ["--repo", str(valid_repo), "docs", "index"])
    content = (valid_repo / "docs" / "runtime" / "docs_index.md").read_text()
    assert "architecture" in content
    assert "project_rules" in content
    assert "backlog" in content


def test_docs_index_written_file_contains_layer_sections(valid_repo):
    runner = CliRunner()
    runner.invoke(main, ["--repo", str(valid_repo), "docs", "index"])
    content = (valid_repo / "docs" / "runtime" / "docs_index.md").read_text()
    assert "## Canonical Docs" in content
    assert "## Working Docs" in content
    assert "## Runtime Docs" in content


def test_docs_index_dry_run_does_not_write(valid_repo):
    runner = CliRunner()
    # Remove existing index if present
    index_path = valid_repo / "docs" / "runtime" / "docs_index.md"
    if index_path.exists():
        index_path.unlink()

    result = runner.invoke(main, ["--repo", str(valid_repo), "docs", "index", "--dry-run"])
    assert result.exit_code == 0
    assert not index_path.exists()
    assert "dry-run" in result.output


def test_docs_index_missing_manifest_exits_nonzero(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "docs", "index"])
    assert result.exit_code != 0


def test_docs_index_json_format(valid_repo):
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(valid_repo), "--format", "json", "docs", "index"]
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["command"] == "docs index"
