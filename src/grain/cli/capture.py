# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""grain capture — a lightweight feature-request / quick-edit inbox.

Jot an idea into ``docs/working/inbox.md`` with ``grain capture add``, review with ``list``, and
turn one into a backlog draft entry + task packet with ``promote``. Pre-backlog and unphased —
scoping happens at promote (the packet tier) and later in the packet, never at capture time.
"""
from __future__ import annotations

import click

from grain.adapters.filesystem import resolve_repo_root
from grain.services import capture_service as cs


@click.group("capture")
def capture_group():
    """Capture feature-requests / quick-edits, then promote them into the backlog."""


def _root(ctx):
    return resolve_repo_root(ctx.obj.get("repo") if ctx.obj else None)


@capture_group.command("add")
@click.argument("title")
@click.option("--note", default="", help="Optional context for the capture.")
@click.option(
    "--kind",
    type=click.Choice(cs.VALID_KINDS),
    default="feature",
    help="Nature hint — drives the default promote tier (edit/chore/bug → simple packet).",
)
@click.pass_context
def capture_add(ctx, title, note, kind):
    """Capture a new inbox item.

    \b
    Example:
      grain capture add "Dark-mode toggle on the dashboard" --kind feature
    """
    try:
        cap_id = cs.capture(_root(ctx), title, note=note, kind=kind)
    except cs.CaptureError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"captured {cap_id}")


@capture_group.command("list")
@click.option(
    "--status", type=click.Choice(cs.VALID_STATUSES), default=None, help="Filter by status."
)
@click.pass_context
def capture_list(ctx, status):
    """List inbox captures (default: all)."""
    caps = cs.list_captures(_root(ctx), status=status)
    if not caps:
        click.echo("(no captures)")
        return
    for cap in caps:
        task = f" → {cap.task}" if cap.task else ""
        click.echo(f"{cap.id}  [{cap.status}]  {cap.kind:<8}  {cap.title}{task}")


@capture_group.command("promote")
@click.argument("cap_id")
@click.option("--phase", type=int, required=True, help="Backlog phase to promote into.")
@click.option(
    "--task-num", type=int, default=None, help="Within-phase task number (auto if omitted)."
)
@click.option(
    "--simple/--full",
    "simple",
    default=None,
    help="Packet tier (default: derived from the capture's kind).",
)
@click.option("--depends-on", default=None, help="Task ref this depends on, e.g. P3-T02.")
@click.pass_context
def capture_promote(ctx, cap_id, phase, task_num, simple, depends_on):
    """Promote a capture into a backlog draft entry + a task packet."""
    try:
        result = cs.promote(
            _root(ctx), cap_id, phase, task_num=task_num, simple=simple, depends_on=depends_on
        )
    except cs.CaptureError as exc:
        raise click.ClickException(str(exc)) from exc
    tier = "simple" if result.simple else "full"
    click.echo(
        f"promoted {result.cap_id} → {result.task_id} "
        f"(P{result.phase}-T{result.task_num:02d}, {tier})"
    )


@capture_group.command("drop")
@click.argument("cap_id")
@click.pass_context
def capture_drop(ctx, cap_id):
    """Shelve a capture (marks it dropped, keeps the line for history)."""
    try:
        cs.drop(_root(ctx), cap_id)
    except cs.CaptureError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"dropped {cap_id}")
