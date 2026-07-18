# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""CLI tests for `grain capture` (add / list / promote / drop)."""

from __future__ import annotations

from click.testing import CliRunner

from grain.cli import main


def _run(args):
    return CliRunner().invoke(main, args)


def test_cli_add_and_list(packet_repo):
    r = _run(["--repo", str(packet_repo), "capture", "add", "Dark mode", "--kind", "feature"])
    assert r.exit_code == 0, r.output
    assert "captured CAP-0001" in r.output

    r2 = _run(["--repo", str(packet_repo), "capture", "list"])
    assert r2.exit_code == 0, r2.output
    assert "CAP-0001" in r2.output
    assert "Dark mode" in r2.output


def test_cli_list_empty(packet_repo):
    r = _run(["--repo", str(packet_repo), "capture", "list"])
    assert r.exit_code == 0
    assert "(no captures)" in r.output


def test_cli_promote(packet_repo):
    backlog = packet_repo / "docs" / "working" / "backlog.md"
    backlog.parent.mkdir(parents=True, exist_ok=True)
    backlog.write_text("# Backlog\n\n## Phase 3 — Things\n")
    _run(["--repo", str(packet_repo), "capture", "add", "New feature", "--kind", "feature"])

    r = _run(["--repo", str(packet_repo), "capture", "promote", "CAP-0001", "--phase", "3"])
    assert r.exit_code == 0, r.output
    assert "promoted CAP-0001 → TASK-" in r.output
    assert "full" in r.output
    assert "### P3-T01 — New feature" in backlog.read_text()


def test_cli_drop(packet_repo):
    _run(["--repo", str(packet_repo), "capture", "add", "toss"])
    r = _run(["--repo", str(packet_repo), "capture", "drop", "CAP-0001"])
    assert r.exit_code == 0, r.output
    assert "dropped CAP-0001" in r.output


def test_cli_bad_kind_rejected(packet_repo):
    r = _run(["--repo", str(packet_repo), "capture", "add", "x", "--kind", "banana"])
    assert r.exit_code != 0
