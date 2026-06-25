"""Tests for `grain report` — selection, --no-browser, JSON, row marked reported."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main

_NOTES = "docs/working/tooling_notes.md"


def _run(tmp_path: Path, *args: str, fmt: str = "text"):
    runner = CliRunner()
    cmd = ["--repo", str(tmp_path)]
    if fmt == "json":
        cmd += ["--format", "json"]
    cmd += list(args)
    return runner.invoke(main, cmd)


def _seed_note(tmp_path: Path, message: str, note_type: str = "bug") -> None:
    _run(tmp_path, "notes", "add", message, "--type", note_type)


# ── listing ───────────────────────────────────────────────────────────────────

def test_report_lists_open_grain_related(tmp_path):
    _seed_note(tmp_path, "grain status was slow", "bug")
    result = _run(tmp_path, "report")
    assert result.exit_code == 0, result.output
    assert "grain status was slow" in result.output
    assert "#1" in result.output


def test_report_empty(tmp_path):
    result = _run(tmp_path, "report")
    assert result.exit_code == 0, result.output
    assert "no open Grain-related notes" in result.output


def test_report_json_list_includes_url(tmp_path):
    _seed_note(tmp_path, "grain init crashed", "bug")
    result = _run(tmp_path, "report", fmt="json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == 1
    assert "github.com/Diwata-Domains/grain/issues/new" in data[0]["url"]


def test_report_observation_only_hidden_without_grain_keyword(tmp_path):
    # An "observation" note that does not mention grain is filtered out by default.
    _seed_note(tmp_path, "unrelated musing about coffee", "observation")
    result = _run(tmp_path, "report")
    assert result.exit_code == 0, result.output
    assert "no open Grain-related notes" in result.output

    # --all surfaces it.
    result_all = _run(tmp_path, "report", "--all")
    assert "coffee" in result_all.output


# ── single-note report ────────────────────────────────────────────────────────

def test_report_id_no_browser_prints_url(tmp_path):
    _seed_note(tmp_path, "grain status slow", "bug")
    result = _run(tmp_path, "report", "--id", "1", "--no-browser")
    assert result.exit_code == 0, result.output
    assert "github.com/Diwata-Domains/grain/issues/new" in result.output
    assert "reported" in result.output


def test_report_id_marks_row_reported(tmp_path):
    _seed_note(tmp_path, "grain status slow", "bug")
    _run(tmp_path, "report", "--id", "1", "--no-browser")

    # The row is now reported, so it no longer shows up as an open candidate.
    listing = _run(tmp_path, "report")
    assert "no open Grain-related notes" in listing.output

    text = (tmp_path / _NOTES).read_text(encoding="utf-8")
    assert "reported" in text


def test_report_id_json_marks_and_returns_url(tmp_path):
    _seed_note(tmp_path, "grain init crash", "bug")
    result = _run(tmp_path, "report", "--id", "1", fmt="json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["reported"] is True
    assert "github.com/Diwata-Domains/grain/issues/new" in data["url"]
    assert data["labels"] == ["bug"]


def test_report_id_unknown_note_usage_error(tmp_path):
    _seed_note(tmp_path, "grain status slow", "bug")
    result = _run(tmp_path, "report", "--id", "99", "--no-browser")
    assert result.exit_code == 2, result.output


def test_report_id_unknown_note_json(tmp_path):
    result = _run(tmp_path, "report", "--id", "99", fmt="json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is False
    assert data["errors"]
