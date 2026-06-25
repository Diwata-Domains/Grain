"""Tests for `grain notes publish` — mocked API, label mapping, missing token.

No real network: the HTTP poster is injected via the service's ``http_post``
hook by monkeypatching ``github_service._urllib_post``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
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


def _write_github_manifest(tmp_path: Path, repo: str = "acme/widgets") -> None:
    manifest = tmp_path / "docs" / "runtime" / "docs_manifest.yaml"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(f"version: 1\ngithub:\n  repo: {repo}\n", encoding="utf-8")


@pytest.fixture
def mock_post(monkeypatch):
    """Patch the urllib poster so publish never hits the network."""
    calls = []

    def fake_post(url, payload, token):
        calls.append({"url": url, "payload": payload, "token": token})
        return {"html_url": "https://github.com/acme/widgets/issues/42", "number": 42}

    from grain.services import github_service
    monkeypatch.setattr(github_service, "_urllib_post", fake_post)
    return calls


# ── happy path ────────────────────────────────────────────────────────────────

def test_publish_creates_issue_and_marks_published(tmp_path, monkeypatch, mock_post):
    monkeypatch.setenv("GRAIN_GITHUB_TOKEN", "tok")
    _write_github_manifest(tmp_path)
    _seed_note(tmp_path, "grain init crashes", "bug")

    result = _run(tmp_path, "notes", "publish", "1")
    assert result.exit_code == 0, result.output
    assert "notes publish: ok" in result.output
    assert "issues/42" in result.output

    # The HTTP layer was invoked against the configured repo.
    assert mock_post[0]["url"] == "https://api.github.com/repos/acme/widgets/issues"

    text = (tmp_path / _NOTES).read_text(encoding="utf-8")
    assert "published" in text


def test_publish_json(tmp_path, monkeypatch, mock_post):
    monkeypatch.setenv("GRAIN_GITHUB_TOKEN", "tok")
    _write_github_manifest(tmp_path)
    _seed_note(tmp_path, "grain init crashes", "bug")

    result = _run(tmp_path, "notes", "publish", "1", fmt="json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["published"] is True
    assert data["issue_number"] == 42
    assert data["labels"] == ["bug"]


# ── label mapping ─────────────────────────────────────────────────────────────

def test_publish_friction_maps_to_enhancement(tmp_path, monkeypatch, mock_post):
    monkeypatch.setenv("GRAIN_GITHUB_TOKEN", "tok")
    _write_github_manifest(tmp_path)
    _seed_note(tmp_path, "grain status slow", "friction")

    result = _run(tmp_path, "notes", "publish", "1", fmt="json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["labels"] == ["enhancement"]
    assert mock_post[0]["payload"]["labels"] == ["enhancement"]


# ── missing token ─────────────────────────────────────────────────────────────

def test_publish_missing_token_clean_error(tmp_path, monkeypatch):
    monkeypatch.delenv("GRAIN_GITHUB_TOKEN", raising=False)
    _write_github_manifest(tmp_path)
    _seed_note(tmp_path, "grain init crashes", "bug")

    result = _run(tmp_path, "notes", "publish", "1")
    assert result.exit_code != 0
    assert "GRAIN_GITHUB_TOKEN" in result.output

    # Note stays open (not published) when the token is missing.
    text = (tmp_path / _NOTES).read_text(encoding="utf-8")
    assert "published" not in text


def test_publish_missing_token_json(tmp_path, monkeypatch):
    monkeypatch.delenv("GRAIN_GITHUB_TOKEN", raising=False)
    _write_github_manifest(tmp_path)
    _seed_note(tmp_path, "grain init crashes", "bug")

    result = _run(tmp_path, "notes", "publish", "1", fmt="json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is False
    assert data["published"] is False
    assert any("GRAIN_GITHUB_TOKEN" in e for e in data["errors"])


# ── unknown note ──────────────────────────────────────────────────────────────

def test_publish_unknown_note_usage_error(tmp_path, monkeypatch, mock_post):
    monkeypatch.setenv("GRAIN_GITHUB_TOKEN", "tok")
    _write_github_manifest(tmp_path)

    result = _run(tmp_path, "notes", "publish", "99")
    assert result.exit_code == 2, result.output


# ── issue create (standalone) ─────────────────────────────────────────────────

def test_issue_create_files_without_notes_log(tmp_path, monkeypatch, mock_post):
    monkeypatch.setenv("GRAIN_GITHUB_TOKEN", "tok")
    _write_github_manifest(tmp_path)

    result = _run(tmp_path, "issue", "create", "--title", "phase close needs metrics",
                  "--type", "friction", fmt="json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["labels"] == ["enhancement"]
    assert data["issue_number"] == 42
    # The notes log was never created.
    assert not (tmp_path / _NOTES).exists()


def test_issue_create_no_repo_configured_fails(tmp_path, monkeypatch, mock_post):
    monkeypatch.setenv("GRAIN_GITHUB_TOKEN", "tok")
    # No github.repo in the manifest (none written at all).
    result = _run(tmp_path, "issue", "create", "--title", "x", "--type", "bug")
    assert result.exit_code != 0
    assert "github.repo" in result.output
