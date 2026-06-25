"""Tests for the GitHub feedback service — URL construction and the API client.

Covers URL encoding, label mapping, privacy (no paths/contents leak), and the
REST issue-create path with a mocked HTTP poster (no real network).
"""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from grain.services.github_service import (
    build_issue_body,
    build_issue_title,
    build_issue_url,
    create_issue,
    label_for_type,
)


# ── label mapping ─────────────────────────────────────────────────────────────

def test_label_for_type_bug():
    assert label_for_type("bug") == "bug"


def test_label_for_type_friction_and_feature_map_to_enhancement():
    assert label_for_type("friction") == "enhancement"
    assert label_for_type("feature") == "enhancement"


def test_label_for_type_ux():
    assert label_for_type("ux") == "ux"


def test_label_for_type_unknown_defaults_enhancement():
    assert label_for_type("something-weird") == "enhancement"
    assert label_for_type("") == "enhancement"


# ── title / body construction ─────────────────────────────────────────────────

def test_build_issue_title_format():
    title = build_issue_title("bug", "grain init", "crash on missing name")
    assert title == "[bug] grain init — crash on missing name"


def test_build_issue_title_truncates_long_observation():
    long_obs = "x" * 200
    title = build_issue_title("friction", "grain status", long_obs)
    # 80-char cap on the observation summary, ellipsis appended.
    assert title.endswith("...")
    assert len(title) < 120


def test_build_issue_body_carries_env_facts_not_paths():
    body = build_issue_body(
        "phase close needs metrics",
        severity="medium",
        grain_version="0.4.0",
        os_platform="darwin",
        install_mode="installed",
    )
    assert "**Observation:** phase close needs metrics" in body
    assert "**Severity:** medium" in body
    assert "**Grain version:** 0.4.0" in body
    assert "**OS:** darwin" in body
    assert "Reported via: grain report" in body


# ── URL construction + privacy ────────────────────────────────────────────────

def test_build_issue_url_is_encoded_and_targets_repo():
    result = build_issue_url(
        "bug", "grain init", "crash & burn",
        repo="Diwata-Domains/grain",
    )
    assert result.ok
    parsed = urlparse(result.url)
    assert parsed.netloc == "github.com"
    assert parsed.path == "/Diwata-Domains/grain/issues/new"
    qs = parse_qs(parsed.query)
    # Title / body / labels present and properly decoded (so they were encoded).
    assert qs["title"][0] == "[bug] grain init — crash & burn"
    assert qs["labels"][0] == "bug"
    assert "crash & burn" in qs["body"][0]


def test_build_issue_url_never_leaks_paths_or_contents():
    # The builder is given only the note text; nothing else can leak.
    result = build_issue_url(
        "friction", "grain status",
        "status was slow on a big repo",
        repo="Diwata-Domains/grain",
    )
    assert result.ok
    # No absolute paths, home dirs, or repo-internal markers in the URL.
    assert "/Users/" not in result.url
    assert "/home/" not in result.url
    assert "docs/working" not in result.url


def test_build_issue_url_empty_observation_fails():
    result = build_issue_url("bug", "grain init", "   ")
    assert not result.ok
    assert result.errors


# ── REST API create_issue (mocked poster) ─────────────────────────────────────

def test_create_issue_posts_correct_payload():
    captured = {}

    def fake_post(url, payload, token):
        captured["url"] = url
        captured["payload"] = payload
        captured["token"] = token
        return {"html_url": "https://github.com/acme/widgets/issues/7", "number": 7}

    result = create_issue(
        "acme/widgets", "title here", "body here", ["bug"],
        token="tok123", http_post=fake_post,
    )
    assert result.ok
    assert result.issue_url == "https://github.com/acme/widgets/issues/7"
    assert result.issue_number == 7
    assert captured["url"] == "https://api.github.com/repos/acme/widgets/issues"
    assert captured["payload"] == {
        "title": "title here", "body": "body here", "labels": ["bug"],
    }
    assert captured["token"] == "tok123"


def test_create_issue_missing_token_fails_cleanly(monkeypatch):
    monkeypatch.delenv("GRAIN_GITHUB_TOKEN", raising=False)

    def fake_post(url, payload, token):  # pragma: no cover - must not be called
        raise AssertionError("HTTP must not be attempted without a token")

    result = create_issue("acme/widgets", "t", "b", ["bug"], http_post=fake_post)
    assert not result.ok
    assert any("GRAIN_GITHUB_TOKEN" in e for e in result.errors)


def test_create_issue_reads_token_from_env(monkeypatch):
    monkeypatch.setenv("GRAIN_GITHUB_TOKEN", "env-token")

    seen = {}

    def fake_post(url, payload, token):
        seen["token"] = token
        return {"html_url": "https://github.com/acme/widgets/issues/1", "number": 1}

    result = create_issue("acme/widgets", "t", "b", ["bug"], http_post=fake_post)
    assert result.ok
    assert seen["token"] == "env-token"


def test_create_issue_missing_repo_fails_cleanly():
    result = create_issue("", "t", "b", ["bug"], token="tok")
    assert not result.ok
    assert any("github.repo" in e for e in result.errors)


def test_create_issue_http_error_surfaces_as_failure():
    def boom(url, payload, token):
        raise RuntimeError("502 bad gateway")

    result = create_issue("acme/widgets", "t", "b", ["bug"], token="tok", http_post=boom)
    assert not result.ok
    assert any("502 bad gateway" in e for e in result.errors)
