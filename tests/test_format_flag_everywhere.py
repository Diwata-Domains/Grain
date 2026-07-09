# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""`--format` must be accepted AFTER the subcommand, everywhere (P38-T02).

Grain is agent-first: a flag whose position changes its validity is a trap. The
top-level ``grain --format json <cmd>`` has always worked, but the same flag
after the subcommand (``grain <cmd> --format json``) used to raise
``No such option: --format`` — so an agent that learned the flag on one command
got a usage error applying it to another.

These tests ENUMERATE the assembled Click command tree via introspection and
assert that every envelope-emitting leaf accepts a subcommand-local
``--format [text|json]`` and, for a representative offline subset, actually
emits parseable JSON on stdout when the flag is given after the subcommand.
"""

from __future__ import annotations

import json

import click
import pytest
from click.testing import CliRunner

from grain.cli import main

# ---------------------------------------------------------------------------
# Leaves that legitimately emit NO JSON envelope, so they carry no --format.
# Every OTHER leaf must accept a local --format; this set is the only allowed
# gap. Kept explicit (by name, with a reason) so a new envelope command that
# forgets the flag is caught rather than silently excused.
#   "mcp serve" — long-running stdio MCP server; streams protocol frames over
#                 stdin/stdout and never returns a command envelope.
#   "tui"       — launches the interactive terminal UI; produces no
#                 machine-readable output at all.
# ---------------------------------------------------------------------------
EXCLUDE = frozenset({"mcp serve", "tui"})

# Offline, read-only, no-required-argument commands that emit a JSON envelope in
# a freshly onboarded workspace. Driven end-to-end with the flag AFTER the
# subcommand to prove the plumbing (not just the option's presence). Spans many
# command groups on purpose. Commands needing required args or an active packet
# (e.g. `verify status`, `review check`, `task show`) are covered by the
# introspection tests below but omitted here because they can't run bare.
FUNCTIONAL_JSON_COMMANDS = [
    "task list",
    "phase list",
    "phase next",
    "phase status",
    "notes list",
    "suggest list",
    "adapter list",
    "archive list",
    "recipe list",
    "model show",
    "docs index",
    "docs audit",
    "hooks status",
    "workflow next",
    "workflow explain",
    "workflow reconcile",
    "workflow guard",
    "status",
    "embedding show",
    "mcp manifest",
    "metrics export",
    "doctor",
    "report",
]


def _iter_leaves(cmd, prefix=""):
    """Yield ``(space_joined_path, command)`` for every non-group leaf."""
    if isinstance(cmd, click.Group):
        for name, sub in cmd.commands.items():
            yield from _iter_leaves(sub, f"{prefix} {name}".strip())
    else:
        yield prefix, cmd


def _format_option(cmd):
    """Return the leaf's ``--format`` Option, or None."""
    for param in cmd.params:
        if isinstance(param, click.Option) and "--format" in param.opts:
            return param
    return None


def _all_leaf_paths():
    return {path for path, _ in _iter_leaves(main)}


# ---------------------------------------------------------------------------
# Introspection: every envelope leaf accepts a local --format (the core guard)
# ---------------------------------------------------------------------------

def test_exclude_set_names_are_real_leaves():
    """Guard against the EXCLUDE set drifting away from the real command tree."""
    assert EXCLUDE <= _all_leaf_paths()


def test_no_envelope_leaf_silently_missing_format():
    """The ONLY leaves without a local --format are the declared non-envelope ones."""
    missing = {path for path, cmd in _iter_leaves(main) if _format_option(cmd) is None}
    assert missing == EXCLUDE, (
        "leaves missing a subcommand-local --format that are not in EXCLUDE "
        f"(or EXCLUDE entries that unexpectedly gained one): {missing ^ EXCLUDE}"
    )


@pytest.mark.parametrize(
    "path",
    sorted(p for p in _all_leaf_paths() if p not in EXCLUDE),
    ids=lambda p: p.replace(" ", "-"),
)
def test_every_envelope_leaf_declares_local_format(path):
    cmd = dict(_iter_leaves(main))[path]
    option = _format_option(cmd)
    assert option is not None, f"{path!r} has no local --format option"
    assert isinstance(option.type, click.Choice)
    assert set(option.type.choices) == {"text", "json"}
    # expose_value=False so command callbacks keep their existing signatures and
    # keep reading the resolved value from ctx.obj["fmt"].
    assert option.expose_value is False


# ---------------------------------------------------------------------------
# Functional: the local flag actually yields JSON on stdout, end to end
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def workspace(tmp_path_factory):
    ws = tmp_path_factory.mktemp("grain_ws")
    result = CliRunner().invoke(main, ["--repo", str(ws), "onboard", str(ws)])
    assert result.exit_code == 0, result.output
    return str(ws)


@pytest.mark.parametrize(
    "command", FUNCTIONAL_JSON_COMMANDS, ids=lambda c: c.replace(" ", "-")
)
def test_local_format_json_produces_parseable_json(workspace, command):
    """`grain <cmd> --format json` (flag AFTER the subcommand) emits JSON.

    Click 8.2+ keeps stderr separate, so ``result.output`` is stdout only and any
    free-text hint on stderr can never corrupt the JSON we parse.
    """
    runner = CliRunner()
    argv = ["--repo", workspace, *command.split(), "--format", "json"]
    result = runner.invoke(main, argv)
    assert result.exception is None or isinstance(result.exception, SystemExit), (
        f"{command} --format json crashed: {result.exception!r}"
    )
    assert result.output.strip(), f"{command} --format json produced no stdout"
    try:
        json.loads(result.output)
    except json.JSONDecodeError as exc:  # pragma: no cover - failure detail
        raise AssertionError(
            f"{command} --format json did not emit parseable JSON on stdout:\n"
            f"stdout={result.output!r}\nstderr={result.stderr!r}"
        ) from exc


# ---------------------------------------------------------------------------
# Resolution precedence: the more specific position wins
# ---------------------------------------------------------------------------

def test_format_resolution_precedence(workspace):
    """group-level sets the default; a local flag after the subcommand overrides it."""
    runner = CliRunner()

    # (1) group-level only -> json
    r1 = runner.invoke(main, ["--repo", workspace, "--format", "json", "task", "list"])
    json.loads(r1.output)

    # (2) local only -> json (this is the position that used to error out)
    r2 = runner.invoke(main, ["--repo", workspace, "task", "list", "--format", "json"])
    json.loads(r2.output)

    # (3) both, disagreeing -> the local (more specific) wins -> text, NOT json
    r3 = runner.invoke(
        main,
        ["--repo", workspace, "--format", "json", "task", "list", "--format", "text"],
    )
    assert r3.output.lstrip().startswith("task list:"), r3.output
    with pytest.raises(json.JSONDecodeError):
        json.loads(r3.output)
