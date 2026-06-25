"""Tests for the grain notes CLI — text and JSON output."""

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


# ── add ─────────────────────────────────────────────────────────────────────

def test_add_text(tmp_path):
    result = _run(tmp_path, "notes", "add", "phase close friction")
    assert result.exit_code == 0, result.output
    assert "notes add: ok" in result.output
    assert "id     1" in result.output
    assert (tmp_path / _NOTES).exists()


def test_add_json(tmp_path):
    result = _run(tmp_path, "notes", "add", "a bug", "--type", "bug", fmt="json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["note"]["id"] == 1
    assert data["note"]["type"] == "bug"
    assert data["note"]["status"] == "open"


def test_add_then_list_text(tmp_path):
    _run(tmp_path, "notes", "add", "first friction")
    result = _run(tmp_path, "notes", "list")
    assert result.exit_code == 0, result.output
    assert "first friction" in result.output
    assert "#1" in result.output


# ── list ────────────────────────────────────────────────────────────────────

def test_list_empty_text(tmp_path):
    result = _run(tmp_path, "notes", "list")
    assert result.exit_code == 0, result.output
    assert "no matching entries" in result.output


def test_list_json_is_array(tmp_path):
    _run(tmp_path, "notes", "add", "one")
    _run(tmp_path, "notes", "add", "two", "--type", "bug")
    result = _run(tmp_path, "notes", "list", fmt="json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 2


def test_list_type_filter(tmp_path):
    _run(tmp_path, "notes", "add", "a friction")
    _run(tmp_path, "notes", "add", "a bug", "--type", "bug")
    result = _run(tmp_path, "notes", "list", "--type", "bug", fmt="json")
    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["type"] == "bug"


def test_list_status_filter_all(tmp_path):
    _run(tmp_path, "notes", "add", "one")
    _run(tmp_path, "notes", "add", "two")
    _run(tmp_path, "notes", "resolve", "2")
    result = _run(tmp_path, "notes", "list", "--status", "all", fmt="json")
    data = json.loads(result.output)
    assert len(data) == 2


# ── show ────────────────────────────────────────────────────────────────────

def test_show_text(tmp_path):
    _run(tmp_path, "notes", "add", "find this", "--type", "bug")
    result = _run(tmp_path, "notes", "show", "1")
    assert result.exit_code == 0, result.output
    assert "notes show: #1" in result.output
    assert "find this" in result.output


def test_show_missing_is_usage_error(tmp_path):
    _run(tmp_path, "notes", "add", "one")
    result = _run(tmp_path, "notes", "show", "999")
    assert result.exit_code == 2


def test_show_json(tmp_path):
    _run(tmp_path, "notes", "add", "json me", "--severity", "medium")
    result = _run(tmp_path, "notes", "show", "1", fmt="json")
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["note"]["severity"] == "medium"


# ── resolve ─────────────────────────────────────────────────────────────────

def test_resolve_text(tmp_path):
    _run(tmp_path, "notes", "add", "fix me")
    result = _run(tmp_path, "notes", "resolve", "1", "done")
    assert result.exit_code == 0, result.output
    assert "notes resolve: ok" in result.output
    assert "status  resolved" in result.output


def test_resolve_drops_from_default_list(tmp_path):
    _run(tmp_path, "notes", "add", "fix me")
    _run(tmp_path, "notes", "resolve", "1")
    result = _run(tmp_path, "notes", "list", fmt="json")
    data = json.loads(result.output)
    assert data == []


def test_resolve_missing_is_usage_error(tmp_path):
    _run(tmp_path, "notes", "add", "one")
    result = _run(tmp_path, "notes", "resolve", "999")
    assert result.exit_code == 2


def test_resolve_json(tmp_path):
    _run(tmp_path, "notes", "add", "fix me")
    result = _run(tmp_path, "notes", "resolve", "1", "patched", fmt="json")
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["note"]["status"] == "resolved"
    assert "patched" in data["note"]["body"]
