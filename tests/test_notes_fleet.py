# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Tests for fleet mode — `grain notes list --fleet` / `triage --fleet`.

Builds a real fixture tree of fake workspaces (two byte-identical inboxes that
simulate git worktree copies, one distinct inbox, a docs/archive snapshot, and a
template-only inbox) and asserts the dedupe and the exclusions, plus the one-
finding-per-defect rollup with the list of workspaces each defect was seen in.
"""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main
from grain.services.notes_service import (
    ReplayOutcome,
    parse_replay_command,
    scan_fleet,
    triage_fleet,
)

_HEADER = (
    "# Tooling Notes\n\n"
    "Lightweight inbox.\n\n"
    "| ID | Date | Type | Command | Observation | Severity | Status |\n"
    "|----|------|------|---------|-------------|----------|--------|\n"
)

# Shared defect X (logged in two distinct workspaces with the same command and
# the same observation prefix — the exact rollup the phase had to hand-build).
# The shared defect is a CLI-surface one — `phase close` reported absent — because
# only a CLI-surface symptom can be cleared by replay (see _verdict_for).
ROW_X = (
    "| 1 | 2026-07-01 | bug | grain phase close | no such command: phase close "
    "does not exist in this build | high | open |"
)
# ws1-only defect Y.
ROW_Y = (
    "| 2 | 2026-07-02 | bug | grain init | onboard leaves proposals/ directory "
    "missing after init | high | open |"
)
# Same as X but a different date/id — still the same defect after normalization.
ROW_X2 = (
    "| 1 | 2026-07-03 | bug | grain phase close | no such command: phase close "
    "does not exist in this build | high | open |"
)
# ws2-only defect Z.
ROW_Z = (
    "| 2 | 2026-07-04 | bug | grain notes add | notes add does not exist yet in "
    "this build | medium | open |"
)

_CONTENT_A = _HEADER + ROW_X + "\n" + ROW_Y + "\n"    # ws1 and its worktree copy
_CONTENT_B = _HEADER + ROW_X2 + "\n" + ROW_Z + "\n"   # ws2 (distinct)
_TEMPLATE = _HEADER                                    # ws3 (no data rows)


def _write_inbox(workspace: Path, content: str) -> Path:
    path = workspace / "docs" / "working" / "tooling_notes.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _build_fleet(root: Path) -> dict[str, Path]:
    """Create the fixture tree and return the workspace roots by name."""
    ws1 = root / "ws1"
    ws1_copy = root / "ws1_copy"          # identical content -> worktree copy
    ws2 = root / "ws2"                     # distinct inbox
    ws3 = root / "ws3"                     # template only (excluded)
    _write_inbox(ws1, _CONTENT_A)
    _write_inbox(ws1_copy, _CONTENT_A)    # byte-identical to ws1
    _write_inbox(ws2, _CONTENT_B)
    _write_inbox(ws3, _TEMPLATE)
    # A docs/archive snapshot (has data rows, but must be excluded).
    archive = ws2 / "docs" / "archive" / "2026-06" / "docs" / "working"
    archive.mkdir(parents=True, exist_ok=True)
    (archive / "tooling_notes.md").write_text(_CONTENT_A, encoding="utf-8")
    return {"ws1": ws1, "ws1_copy": ws1_copy, "ws2": ws2, "ws3": ws3}


# ── scan_fleet: dedupe + exclusions ───────────────────────────────────────────

def test_fleet_excludes_archive_template_and_collapses_worktrees(tmp_path):
    _build_fleet(tmp_path)
    result = scan_fleet([tmp_path])

    assert result.discovered == 5          # ws1, ws1_copy, ws2, ws3, archive snap
    assert result.skipped_archive == 1     # docs/archive/** snapshot
    assert result.skipped_template == 1    # ws3 header-only inbox
    assert result.skipped_worktree == 1    # ws1_copy collapsed into ws1
    assert result.workspaces == 2          # only ws1 (or its copy) and ws2 kept


def test_fleet_emits_one_finding_per_defect_with_workspaces(tmp_path):
    _build_fleet(tmp_path)
    result = scan_fleet([tmp_path])

    assert len(result.findings) == 3

    shared = next(f for f in result.findings if "phase close" in f.command)
    # Seen in ws1 AND ws2; the worktree copy must NOT inflate the count.
    assert shared.count == 2
    assert len(shared.workspaces) == 2
    basenames = {Path(w).name for w in shared.workspaces}
    assert "ws2" in basenames
    assert len(basenames & {"ws1", "ws1_copy"}) == 1   # collapsed to exactly one

    y = next(f for f in result.findings if "init" in f.command)
    z = next(f for f in result.findings if "notes add" in f.command)
    assert y.count == 1
    assert z.count == 1


def test_fleet_findings_sorted_by_prevalence(tmp_path):
    _build_fleet(tmp_path)
    result = scan_fleet([tmp_path])
    # Most-prevalent defect first.
    assert result.findings[0].count == 2


def test_fleet_status_filter_default_is_open(tmp_path):
    # A resolved row must not surface in the default (open) rollup.
    ws = tmp_path / "solo"
    _write_inbox(
        ws,
        _HEADER
        + "| 1 | 2026-07-01 | bug | grain phase close | done deal | low | resolved |\n",
    )
    assert scan_fleet([tmp_path]).findings == []
    assert len(scan_fleet([tmp_path], status_filter="all").findings) == 1


def test_fleet_scan_handles_missing_root(tmp_path):
    result = scan_fleet([tmp_path / "does-not-exist"])
    assert result.ok
    assert result.findings == []
    assert result.workspaces == 0


# ── CLI: notes list --fleet ───────────────────────────────────────────────────

def test_fleet_list_cli_text(tmp_path):
    _build_fleet(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["notes", "list", "--fleet", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "2 workspace(s)" in result.output
    assert "3 distinct finding(s)" in result.output
    assert "seen in:" in result.output
    assert "collapsed 1 worktree" in result.output


def test_fleet_list_cli_json(tmp_path):
    _build_fleet(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main, ["--format", "json", "notes", "list", "--fleet", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["fleet"] is True
    assert data["workspaces"] == 2
    assert data["skipped"] == {"archive": 1, "worktree": 1, "template": 1}
    assert len(data["findings"]) == 3
    shared = next(f for f in data["findings"] if "phase close" in f["command"])
    assert shared["count"] == 2


def test_fleet_list_rejects_roots_without_flag(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["notes", "list", str(tmp_path)])
    assert result.exit_code == 2
    assert "only accepted with --fleet" in result.output


# ── triage --fleet: replay once per defect, resolve across workspaces ──────────

def _stub(command: str) -> ReplayOutcome:
    argv = parse_replay_command(command)
    if argv is None:
        return ReplayOutcome(replayable=False, command=command)
    # The shared "phase close" defect is now fixed; everything else still errors.
    exit_code = 0 if argv[:2] == ["phase", "close"] else 1
    return ReplayOutcome(
        replayable=True, exit_code=exit_code, command="grain " + " ".join(argv),
    )


def test_triage_fleet_replays_once_per_deduped_defect(tmp_path):
    _build_fleet(tmp_path)
    calls: list[str] = []

    def counting_stub(command: str) -> ReplayOutcome:
        calls.append(command)
        return _stub(command)

    result = triage_fleet(
        [tmp_path], replay=counting_stub, version="9.9.9",
    )
    # 3 distinct findings -> exactly 3 replays (not once per workspace row).
    assert len(calls) == 3
    assert len(result.items) == 3
    assert result.fleet is True
    shared = next(i for i in result.items if "phase close" in i.replay.command)
    assert shared.verdict == "stale"
    # The stale finding still remembers both workspaces it was seen in.
    assert len(shared.workspaces) == 2


def test_triage_fleet_resolve_stale_closes_across_workspaces(tmp_path):
    names = _build_fleet(tmp_path)
    result = triage_fleet(
        [tmp_path], replay=_stub, resolve_stale=True, version="9.9.9",
    )

    # The shared "phase close" note is resolved in every workspace it was seen
    # in: the canonical of the worktree pair (ws1 or ws1_copy) + ws2.
    assert result.resolved_count == 2

    def _resolved(ws: Path) -> bool:
        text = (ws / "docs/working/tooling_notes.md").read_text()
        return "resolved" in text and "9.9.9" in text

    # ws2 always resolved; exactly one of the collapsed worktree pair resolved.
    assert _resolved(names["ws2"])
    assert _resolved(names["ws1"]) ^ _resolved(names["ws1_copy"])
