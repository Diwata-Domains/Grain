"""Tests for `forge docs show` command."""

import json

from click.testing import CliRunner

from grain.cli import main


def test_docs_show_known_doc_exits_zero(valid_repo):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(valid_repo), "docs", "show", "architecture"])
    assert result.exit_code == 0


def test_docs_show_displays_metadata_fields(valid_repo):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(valid_repo), "docs", "show", "architecture"])
    assert "architecture" in result.output
    assert "docs/canonical/architecture.md" in result.output
    assert "canonical" in result.output
    assert "highest" in result.output
    assert "Defines system structure" in result.output


def test_docs_show_unknown_doc_exits_two(valid_repo):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(valid_repo), "docs", "show", "nonexistent"])
    assert result.exit_code == 2


def test_docs_show_missing_manifest_exits_nonzero(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "docs", "show", "architecture"])
    assert result.exit_code != 0


def test_docs_show_json_format(valid_repo):
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(valid_repo), "--format", "json", "docs", "show", "architecture"]
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["doc"]["id"] == "architecture"
    assert data["doc"]["path"] == "docs/canonical/architecture.md"
    assert data["doc"]["layer"] == "canonical"
    assert data["doc"]["editable_by_agents"] is False
