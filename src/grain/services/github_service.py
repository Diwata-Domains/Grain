# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""GitHub feedback service — pre-filled issue URLs and a REST issue client.

Two upstream feedback surfaces share this module:

* ``build_issue_url`` constructs a pre-filled GitHub "new issue" URL per
  ``docs/canonical/feedback_spec.md``. No network call is made; the user reviews
  and submits in the browser. The URL is privacy-preserving — it never carries
  file contents, absolute paths, repo names, or PII, only the note's own text.
* ``create_issue`` POSTs an issue to the GitHub REST API using a token read from
  the ``GRAIN_GITHUB_TOKEN`` environment variable. The HTTP call is funneled
  through an injectable ``http_post`` function so tests never touch the network.

Both paths reuse :func:`label_for_type` so the label applied to an issue matches
regardless of whether it travels via URL or API.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Callable
from urllib.parse import urlencode

_TOKEN_ENV = "GRAIN_GITHUB_TOKEN"
_API_BASE = "https://api.github.com"
_NEW_ISSUE_BASE = "https://github.com/{repo}/issues/new"
_REPORTED_VIA = "Reported via: grain report"

# Type/severity → GitHub label. Covers both note types (friction/bug/observation)
# and issue-create types (bug/feature/friction/ux). Unknown types fall back to
# the neutral "enhancement" label so an issue is never created label-less.
_LABEL_MAP = {
    "bug": "bug",
    "ux": "ux",
    "friction": "enhancement",
    "feature": "enhancement",
    "enhancement": "enhancement",
    "observation": "enhancement",
    "missing-command": "enhancement",
}
_DEFAULT_LABEL = "enhancement"


# ── Result types ──────────────────────────────────────────────────────────────

@dataclass
class IssueUrlResult:
    """A constructed pre-filled GitHub new-issue URL plus its components."""

    ok: bool
    url: str = ""
    title: str = ""
    labels: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class IssueCreateResult:
    """Outcome of a REST API issue creation."""

    ok: bool
    issue_url: str = ""
    issue_number: int | None = None
    title: str = ""
    labels: list[str] = field(default_factory=list)
    repo: str = ""
    errors: list[str] = field(default_factory=list)


# ── Public API ────────────────────────────────────────────────────────────────

def label_for_type(note_type: str) -> str:
    """Map a note/issue type to a GitHub label (defaults to ``enhancement``)."""
    return _LABEL_MAP.get((note_type or "").strip().lower(), _DEFAULT_LABEL)


def build_issue_title(note_type: str, command: str, observation: str) -> str:
    """Build the ``[type] command — observation`` title (observation ≤ 80 chars).

    Privacy: only the note's own type/command/observation text is used. The
    observation is truncated so long bodies never bloat the URL.
    """
    summary = (observation or "").strip().replace("\n", " ")
    if len(summary) > 80:
        summary = summary[:77].rstrip() + "..."
    cmd = (command or "").strip() or "grain"
    return f"[{(note_type or 'friction').strip().lower()}] {cmd} — {summary}"


def build_issue_body(
    observation: str,
    *,
    severity: str = "low",
    grain_version: str = "",
    os_platform: str = "",
    install_mode: str = "",
) -> str:
    """Build the structured issue body template per feedback_spec.

    Carries only the observation text and benign environment facts (Grain
    version, OS platform string, install mode). Never includes file contents,
    paths, repo names, or stack traces.
    """
    return (
        f"**Observation:** {(observation or '').strip()}\n"
        f"**Severity:** {(severity or 'low').strip()}\n"
        f"**Grain version:** {grain_version}\n"
        f"**OS:** {os_platform}\n"
        f"**Install mode:** {install_mode}\n\n"
        "**Steps to reproduce:**\n"
        "(please fill in if applicable)\n\n"
        "**Expected behavior:**\n"
        "(please fill in)\n\n"
        "---\n"
        f"{_REPORTED_VIA}\n"
    )


def build_issue_url(
    note_type: str,
    command: str,
    observation: str,
    *,
    repo: str = "Diwata-Domains/grain",
    severity: str = "low",
    grain_version: str = "",
    os_platform: str = "",
    install_mode: str = "",
) -> IssueUrlResult:
    """Construct a pre-filled GitHub new-issue URL (no network call).

    All query parameters are URL-encoded. The result is safe to open in a
    browser; GitHub renders the form pre-populated and the user submits.
    """
    if not observation or not observation.strip():
        return IssueUrlResult(ok=False, errors=["observation is empty"])

    title = build_issue_title(note_type, command, observation)
    body = build_issue_body(
        observation,
        severity=severity,
        grain_version=grain_version,
        os_platform=os_platform,
        install_mode=install_mode,
    )
    label = label_for_type(note_type)

    query = urlencode({"title": title, "body": body, "labels": label})
    url = f"{_NEW_ISSUE_BASE.format(repo=repo)}?{query}"
    return IssueUrlResult(ok=True, url=url, title=title, labels=[label])


def create_issue(
    repo: str,
    title: str,
    body: str,
    labels: list[str],
    *,
    token: str | None = None,
    http_post: Callable[..., dict] | None = None,
) -> IssueCreateResult:
    """Create a GitHub issue via the REST API using ``GRAIN_GITHUB_TOKEN``.

    The token is read from the environment unless one is passed explicitly; it is
    never written to any workspace file. ``http_post`` defaults to a small urllib
    wrapper and is injectable so tests can mock the HTTP layer.

    Returns ``ok=False`` with a clear error for the expected failures (missing
    token, missing repo, network/HTTP error) rather than raising.
    """
    if not repo or not repo.strip():
        return IssueCreateResult(
            ok=False,
            errors=[
                "no github.repo configured in docs_manifest.yaml; "
                "add a github: block with repo: owner/name"
            ],
        )

    tok = token if token is not None else os.environ.get(_TOKEN_ENV, "")
    if not tok or not tok.strip():
        return IssueCreateResult(
            ok=False,
            repo=repo,
            errors=[
                f"missing {_TOKEN_ENV}; set it in your environment to publish "
                "via the GitHub API (never stored in workspace files)"
            ],
        )

    poster = http_post if http_post is not None else _urllib_post
    payload = {"title": title, "body": body, "labels": list(labels)}
    url = f"{_API_BASE}/repos/{repo}/issues"

    try:
        response = poster(url, payload, tok)
    except Exception as exc:  # noqa: BLE001 — surfaced as an expected failure
        return IssueCreateResult(
            ok=False,
            repo=repo,
            title=title,
            labels=list(labels),
            errors=[f"github api request failed: {exc}"],
        )

    if not isinstance(response, dict):
        return IssueCreateResult(
            ok=False,
            repo=repo,
            title=title,
            labels=list(labels),
            errors=["github api returned an unexpected response"],
        )

    return IssueCreateResult(
        ok=True,
        issue_url=str(response.get("html_url", "")),
        issue_number=response.get("number"),
        title=title,
        labels=list(labels),
        repo=repo,
    )


# ── HTTP wrapper (injectable; mocked in tests) ─────────────────────────────────

def _urllib_post(url: str, payload: dict, token: str) -> dict:
    """POST JSON to the GitHub API and return the parsed response dict.

    Kept tiny and dependency-free (stdlib urllib) so it can be monkeypatched in
    tests. Raises on transport/HTTP errors; ``create_issue`` converts those into
    an expected failure result.
    """
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("Content-Type", "application/json")
    request.add_header("User-Agent", "grain-cli")
    with urllib.request.urlopen(request) as resp:  # noqa: S310 — fixed https host
        return json.loads(resp.read().decode("utf-8"))
