# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""One shared, subcommand-local ``--format`` option for every envelope command.

Grain is agent-first: a flag whose position changes its validity is a trap. The
top-level ``grain --format json <cmd>`` has always worked, but historically the
SAME flag after the subcommand (``grain <cmd> --format json``) raised
``No such option: --format`` — so an agent that learned the flag on one command
got a usage error applying it to another.

:func:`install_format_option` walks the assembled command tree once and attaches
an eager, subcommand-local ``--format [text|json]`` to every envelope-emitting
leaf. Groups are pure dispatchers and are skipped; a leaf that emits no JSON
envelope (see :data:`NO_ENVELOPE_COMMANDS`) is skipped too.

Resolution — the more specific position wins:

* ``grain --format json X``                -> json   (top-level flag; leaf unset)
* ``grain X --format json``                -> json   (leaf flag; overrides default)
* ``grain --format json X --format text``  -> text   (leaf flag beats top-level)

This holds because Click runs the root group's callback (which resolves the
default and the top-level flag into ``ctx.obj["fmt"]``) BEFORE it processes a
leaf's parameters. The leaf option is eager and ``expose_value=False``: when
given it overwrites ``ctx.obj["fmt"]`` (the same slot the root writes and every
command already reads); when unset it leaves the resolved default untouched and
is never passed to the command callback, so command signatures are unchanged.
"""

from __future__ import annotations

import click

FORMAT_CHOICES = ("text", "json")

# Leaves that emit NO JSON envelope, so they carry no local ``--format``:
#   "mcp serve" — long-running stdio MCP server; streams protocol frames and
#                 never returns a command envelope.
#   "tui"       — launches the interactive terminal UI; no machine-readable
#                 output at all.
NO_ENVELOPE_COMMANDS = frozenset({"mcp serve", "tui"})


def _store_format(ctx: click.Context, param: click.Parameter, value: str | None) -> str | None:
    # Defer to the top-level value (already resolved into ctx.obj["fmt"] by the
    # root callback) when unset; override it only when the local flag is given,
    # so the more specific position wins.
    if value is not None:
        ctx.ensure_object(dict)
        ctx.obj["fmt"] = value
    return value


def make_format_option() -> click.Option:
    """Build a fresh subcommand-local ``--format`` option instance."""
    return click.Option(
        ["--format", "_fmt_local"],
        type=click.Choice(FORMAT_CHOICES),
        # A compact metavar (choices stay in the help text and in Click's
        # invalid-value error) keeps this option from becoming the widest in a
        # command and reflowing neighbouring option help. Validation is unchanged:
        # the type is still a Choice, so only text/json are accepted.
        metavar="FMT",
        default=None,
        show_default=False,
        expose_value=False,
        is_eager=True,
        callback=_store_format,
        help=(
            "Output format for this command: text or json. Overrides the "
            "top-level --format when given after the subcommand."
        ),
    )


def _has_format_option(command: click.Command) -> bool:
    return any("--format" in getattr(param, "opts", ()) for param in command.params)


def install_format_option(
    group: click.Group, *, exclude: frozenset[str] = NO_ENVELOPE_COMMANDS
) -> None:
    """Attach a local ``--format`` to every envelope-emitting leaf under ``group``.

    Walks the assembled tree once. Groups are recursed into but never decorated
    (they only dispatch). Each leaf gets a fresh option unless it already has one
    or its space-joined path (e.g. ``"mcp serve"``) is in ``exclude``. Idempotent:
    re-running never double-adds.
    """
    def _walk(command: click.Command, path: str) -> None:
        if isinstance(command, click.Group):
            for name, sub in command.commands.items():
                _walk(sub, f"{path} {name}".strip())
            return
        if path in exclude:
            return
        if not _has_format_option(command):
            command.params.append(make_format_option())

    _walk(group, "")
