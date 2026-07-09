# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Tests for `grain notes triage` — replay-based staleness classification.

Triage replays each open note's recorded command in a throwaway workspace and
classifies it stale / still-open / needs-human. The classification logic is
tested with a deterministic replay stub (so it is fast and does not shell out);
one integration test exercises the real throwaway-workspace replayer end to end.
"""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from grain.cli import main
from grain.services.notes_service import (
    TRIAGE_HUMAN,
    TRIAGE_OPEN,
    TRIAGE_STALE,
    ReplayOutcome,
    _verdict_for,
    add_note,
    list_notes,
    make_default_replayer,
    parse_replay_command,
    triage_notes,
)

_NOTES = "docs/working/tooling_notes.md"


def _run(tmp_path: Path, *args: str, fmt: str = "text"):
    runner = CliRunner()
    cmd = ["--repo", str(tmp_path)]
    if fmt == "json":
        cmd += ["--format", "json"]
    cmd += list(args)
    return runner.invoke(main, cmd)


def _stub(command: str) -> ReplayOutcome:
    """Faithful replay stub: real parser decides replayability; we fake exits.

    Anything mentioning ``next`` exits 0 (a fixed command); everything else that
    IS a grain command exits 1 (still errors). Non-grain / prose / empty cells
    fall through to the parser's ``None`` and are marked not replayable.
    """
    argv = parse_replay_command(command)
    if argv is None:
        return ReplayOutcome(replayable=False, command=command)
    exit_code = 0 if "next" in argv else 1
    return ReplayOutcome(
        replayable=True, exit_code=exit_code, command="grain " + " ".join(argv),
    )


# ── parse_replay_command ──────────────────────────────────────────────────────

def test_parse_plain_grain_command():
    assert parse_replay_command("grain workflow next") == ["workflow", "next"]


def test_parse_strips_backticks():
    assert parse_replay_command("`grain status`") == ["status"]


def test_parse_takes_first_slash_alternative():
    # "`a` / `b`" records equivalent alternatives — replay the first.
    assert parse_replay_command(
        "`grain workflow next --format json` / `grain status`"
    ) == ["workflow", "next", "--format", "json"]


def test_parse_skips_leading_env_assignments():
    assert parse_replay_command("GRAIN_SKIP_VERSION_CHECK=1 grain status") == [
        "status"
    ]


def test_parse_rejects_empty_and_dash():
    assert parse_replay_command("") is None
    assert parse_replay_command("   ") is None
    assert parse_replay_command("—") is None


def test_parse_rejects_free_prose():
    assert parse_replay_command("packet structure") is None
    assert parse_replay_command("some observation about init") is None


def test_parse_rejects_non_grain_commands():
    assert parse_replay_command("git push") is None
    assert parse_replay_command("pytest -q") is None


def test_parse_rejects_shell_pipelines():
    assert parse_replay_command("grain status | grep x") is None
    assert parse_replay_command("grain a && grain b") is None
    assert parse_replay_command("grain status > out.txt") is None


def test_parse_rejects_interactive_and_agent_commands():
    assert parse_replay_command("grain tui") is None
    assert parse_replay_command("grain mcp serve") is None
    assert parse_replay_command("grain orchestrate run") is None
    assert parse_replay_command("grain workflow run") is None
    # global flags before the subcommand must not hide an unsafe subcommand
    assert parse_replay_command("grain --format json workflow run") is None


# ── classification (service, deterministic stub) ──────────────────────────────

def test_triage_classifies_stale_open_and_human(tmp_path):
    add_note(tmp_path, "format flag bug, --format is not accepted as an option here", command="grain workflow next --format json")
    add_note(tmp_path, "still broken, no such command exists for this", command="grain phase close")
    add_note(tmp_path, "free prose only, no command", command="")

    result = triage_notes(tmp_path, replay=_stub, version="9.9.9")
    by_body = {i.note.body.split(",")[0]: i for i in result.items}

    assert by_body["format flag bug"].verdict == TRIAGE_STALE
    assert by_body["still broken"].verdict == TRIAGE_OPEN
    assert by_body["free prose only"].verdict == TRIAGE_HUMAN
    assert len(result.stale) == 1
    assert len(result.still_open) == 1
    assert len(result.needs_human) == 1


def test_triage_is_dry_run_by_default(tmp_path):
    add_note(tmp_path, "format flag bug", command="grain workflow next")

    result = triage_notes(tmp_path, replay=_stub, version="9.9.9")

    assert result.dry_run is True
    assert result.resolved_count == 0
    # The stale candidate is reported but NOT mutated.
    still_open = list_notes(tmp_path, status_filter="open").notes
    assert len(still_open) == 1
    assert still_open[0].status == "open"


def test_triage_resolve_stale_closes_only_candidates(tmp_path):
    add_note(tmp_path, "fixed one, --format is not accepted as an option", command="grain workflow next --format json")
    add_note(tmp_path, "still broken, no such command exists for this", command="grain phase close")
    add_note(tmp_path, "prose", command="")

    result = triage_notes(
        tmp_path, replay=_stub, resolve_stale=True, version="9.9.9",
    )

    assert result.dry_run is False
    assert result.resolved_count == 1

    everything = {n.body.split(" —")[0]: n for n in
                  list_notes(tmp_path, status_filter="all").notes}
    assert everything["fixed one, --format is not accepted as an option"].status == "resolved"
    assert everything["still broken, no such command exists for this"].status == "open"   # conservative
    assert everything["prose"].status == "open"           # needs human, untouched
    # The fixing version is recorded on the closed note.
    resolved = list_notes(tmp_path, status_filter="resolved").notes
    assert len(resolved) == 1
    assert "9.9.9" in resolved[0].body


def test_triage_conservative_unrelated_nonzero_never_stale(tmp_path):
    """A command that exits nonzero for ANY reason stays open, never stale."""
    add_note(tmp_path, "flaky, the doctor option does not exist", command="grain doctor")

    def replay(command):
        # Simulate an unrelated failure (exit 3) — must NOT be closed.
        return ReplayOutcome(replayable=True, exit_code=3, command=command)

    result = triage_notes(
        tmp_path, replay=replay, resolve_stale=True, version="9.9.9",
    )
    assert len(result.stale) == 0
    assert len(result.still_open) == 1
    assert result.resolved_count == 0
    assert list_notes(tmp_path, status_filter="open").notes[0].status == "open"


def test_triage_only_considers_open_notes(tmp_path):
    add_note(tmp_path, "already handled", command="grain workflow next")
    from grain.services.notes_service import resolve_note
    resolve_note(tmp_path, 1)  # flip to resolved

    result = triage_notes(tmp_path, replay=_stub, version="9.9.9")
    assert result.items == []


# ── CLI ───────────────────────────────────────────────────────────────────────

def test_triage_cli_text(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "grain.services.notes_service.make_default_replayer", lambda **k: _stub,
    )
    _run(tmp_path, "notes", "add", "fixed: --format is not accepted as an option", "--command", "grain workflow next --format json")
    _run(tmp_path, "notes", "add", "broken: no such command", "--command", "grain phase close")

    result = _run(tmp_path, "notes", "triage")
    assert result.exit_code == 0, result.output
    assert "heuristic" in result.output.lower()
    assert "1 stale candidate" in result.output
    assert "stale ✓" in result.output
    assert "--resolve-stale" in result.output   # dry-run hint


def test_triage_cli_json(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "grain.services.notes_service.make_default_replayer", lambda **k: _stub,
    )
    _run(tmp_path, "notes", "add", "fixed: --format is not accepted as an option", "--command", "grain workflow next --format json")
    _run(tmp_path, "notes", "add", "broken: no such command", "--command", "grain phase close")

    result = _run(tmp_path, "notes", "triage", fmt="json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["fleet"] is False
    assert data["dry_run"] is True
    assert data["summary"]["stale"] == 1
    assert data["summary"]["open"] == 1
    verdicts = {i["verdict"] for i in data["items"]}
    assert verdicts == {TRIAGE_STALE, TRIAGE_OPEN}


def test_triage_cli_resolve_stale(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "grain.services.notes_service.make_default_replayer", lambda **k: _stub,
    )
    _run(tmp_path, "notes", "add", "fixed: --format is not accepted as an option", "--command", "grain workflow next --format json")

    result = _run(tmp_path, "notes", "triage", "--resolve-stale")
    assert result.exit_code == 0, result.output

    # The note is now resolved and drops out of the default (open) list.
    listed = _run(tmp_path, "notes", "list", fmt="json")
    assert json.loads(listed.output) == []
    resolved = _run(tmp_path, "notes", "list", "--status", "resolved", fmt="json")
    assert len(json.loads(resolved.output)) == 1


def test_triage_rejects_roots_without_fleet(tmp_path):
    result = _run(tmp_path, "notes", "triage", "/some/root")
    assert result.exit_code == 2
    assert "only accepted with --fleet" in result.output


# ── real replayer (integration) ───────────────────────────────────────────────

def test_real_replayer_classifies_by_actual_exit_code(tmp_path):
    """End-to-end: the default replayer actually runs grain in a throwaway ws.

    `grain --version` exits 0 (stale candidate); a bogus subcommand exits
    nonzero (stays open). This proves the subprocess/init/copytree path works.
    """
    add_note(tmp_path, "version prints: no such option --version, does not exist", command="grain --version")
    add_note(tmp_path, "bogus: this command does not exist", command="grain definitely-not-a-real-subcommand")

    result = triage_notes(
        tmp_path, replay=make_default_replayer(), version="9.9.9",
    )
    by_body = {i.note.body: i for i in result.items}
    assert by_body["version prints: no such option --version, does not exist"].verdict == TRIAGE_STALE
    assert by_body["version prints: no such option --version, does not exist"].replay.exit_code == 0
    assert by_body["bogus: this command does not exist"].verdict == TRIAGE_OPEN
    assert by_body["bogus: this command does not exist"].replay.exit_code != 0


# ── T12: an exit code is not evidence ────────────────────────────────────────
#
# Measured on the real fleet 2026-07-09: classifying a note stale because its
# command "now exits 0" had ~27% precision. Eleven of fifteen candidates already
# exited 0 on grain 0.5.0 — their exit code never encoded the defect, because the
# symptom needed workspace state the throwaway sandbox does not have.
#
# A note may only be called stale when its symptom lives on the CLI surface (a
# command or flag that did not exist) AND that surface now exists.

def _outcome(exit_code: int, stderr: str = "", command: str = "grain phase list") -> ReplayOutcome:
    return ReplayOutcome(replayable=True, exit_code=exit_code, command=command, stderr=stderr)


# The four sound cases: the note says the command/flag is absent, and it now exists.
def test_cli_surface_symptom_that_now_exits_zero_is_stale():
    obs = "No `phase list` command exists — only `phase next`."
    assert _verdict_for(_outcome(0), obs) == TRIAGE_STALE


def test_cli_surface_flag_rejection_that_now_exits_zero_is_stale():
    obs = "`--format` is not accepted as an option on `task list` — works only as a top-level flag."
    out = _outcome(0, command="grain task list --format json")
    assert _verdict_for(out, obs) == TRIAGE_STALE


def test_missing_argument_proves_the_command_exists_so_note_is_stale():
    # `grain notes add` shipped. Replaying it bare exits 2 with `Missing argument`,
    # which is proof the command EXISTS. Click exits 2 for `No such command` too,
    # so the exit code alone cannot tell them apart — the stderr can.
    obs = "`grain notes add` does not exist yet."
    out = _outcome(2, "Error: Missing argument 'MESSAGE'.", command="grain notes add")
    assert _verdict_for(out, obs) == TRIAGE_STALE


def test_no_such_command_means_still_open():
    obs = "`grain frobnicate` does not exist."
    out = _outcome(2, "Error: No such command 'frobnicate'.", command="grain frobnicate")
    assert _verdict_for(out, obs) == TRIAGE_OPEN


# The unsound cases: a behavioural symptom can never be cleared by exit 0.
def test_state_dependent_symptom_exiting_zero_is_never_stale():
    # `grain onboard` always exited 0; the note is about missing guidance.
    obs = "`grain onboard` scaffolds files but does not populate them — the CLI output does not surface the next step."
    assert _verdict_for(_outcome(0), obs) == TRIAGE_HUMAN


def test_upgrade_add_missing_reporting_bug_is_not_stale_on_exit_zero():
    # This WAS fixed in Phase 38, but the replay does not establish it: the bare
    # command exits 0 in an empty workspace on 0.5.0 too. Right answer, wrong reason.
    obs = "grain upgrade --add-missing reports 'Added: (none)' but DOES create the absent seed files."
    assert _verdict_for(_outcome(0), obs) == TRIAGE_HUMAN


def test_behavioural_symptom_needs_human_whatever_the_exit_code():
    # A behavioural symptom leaves no trace in an exit code, in EITHER direction.
    # Calling it "still open" would be as unfounded as calling it stale.
    obs = "grain phase close --dry-run returns JSON with \"dry_run\": false when it should be true."
    assert _verdict_for(_outcome(1), obs) == TRIAGE_HUMAN
    assert _verdict_for(_outcome(0), obs) == TRIAGE_HUMAN


def test_unreplayable_note_needs_human():
    assert _verdict_for(ReplayOutcome(replayable=False, command=""), "free prose") == TRIAGE_HUMAN


# ── T12b: the replay must exercise the symptom the note describes ─────────────

def _out(exit_code: int, command: str, stderr: str = "") -> ReplayOutcome:
    return ReplayOutcome(replayable=True, exit_code=exit_code, command=command, stderr=stderr)


def test_absent_command_symptom_is_cleared_by_the_bare_command():
    # "No `phase list` command exists" — replaying `grain phase list` IS the test.
    obs = "No `phase list` command exists — only `phase next`."
    assert _verdict_for(_out(0, "grain phase list"), obs) == TRIAGE_STALE


def test_rejected_option_symptom_needs_the_option_in_the_replayed_command():
    obs = "`--format` is not accepted as an option on `task list`."
    # The recorded command carries the option: exit 0 proves it is accepted.
    assert _verdict_for(_out(0, "grain task list --format json"), obs) == TRIAGE_STALE
    # It does not: exit 0 proves nothing about the option.
    assert _verdict_for(_out(0, "grain task list"), obs) == TRIAGE_HUMAN


def test_rejected_positional_symptom_needs_a_positional_in_the_replayed_command():
    # Real note: `grain task validate P8-T02-TASK-0027` -> "Got unexpected extra
    # argument". The recorded command is the bare `grain task validate`, which
    # exits 0 on every version. It must not be called stale.
    obs = "grain task validate/show reject a positional packet dir with 'Got unexpected extra argument'."
    assert _verdict_for(_out(0, "grain task validate"), obs) == TRIAGE_HUMAN
    # With the positional actually present, exit 0 does settle it.
    assert _verdict_for(_out(0, "grain task validate P8-T02-TASK-0027"), obs) == TRIAGE_STALE
