# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""CLI command group for grain suggest operations (proposal-only, deterministic)."""

from __future__ import annotations

import json

import click

from grain.adapters.filesystem import resolve_repo_root


def _proposal_dict(p) -> dict:
    return {
        "id": p.id,
        "kind": p.kind,
        "title": p.title,
        "status": p.status,
        "signal": p.signal,
        "signal_ref": p.signal_ref,
        "rationale": p.rationale,
        "created_at": p.created_at,
        "task_ref": p.task_ref,
        "task_id": p.task_id,
        "phase": p.phase,
        "objective": p.objective,
        "suggested_phase": p.suggested_phase,
        "source_signals": list(p.source_signals),
    }


@click.group("suggest", invoke_without_command=True)
@click.option("--type", "kind_filter", default=None,
              type=click.Choice(["pick-up", "new-task"]),
              help="Filter to a single suggestion type.")
@click.option("--limit", type=int, default=None, help="Limit the number of suggestions shown.")
@click.option("--prune", "do_prune", is_flag=True, default=False,
              help="Move expired and old-dismissed proposals to docs/archive/proposals/.")
@click.pass_context
def suggest_group(ctx, kind_filter, limit, do_prune):
    """Proactively surface what to work on next (file-backed proposals).

    \b
    Examples:
      grain suggest
      grain suggest --type pick-up
      grain suggest --limit 3
      grain suggest --prune
    """
    if ctx.invoked_subcommand is not None:
        return

    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    from grain.services.suggest_service import generate, prune

    if do_prune:
        result = prune(root)
        if fmt == "json":
            click.echo(json.dumps({"ok": result.ok, "pruned": result.moved}, indent=2))
            return
        click.echo("suggest prune: ok")
        if result.moved:
            for p in result.moved:
                click.echo(f"  moved  {p}")
        else:
            click.echo("  (nothing to prune)")
        return

    result = generate(root, kind_filter=kind_filter, limit=limit)

    if fmt == "json":
        click.echo(json.dumps({
            "ok": result.ok,
            "proposals": [_proposal_dict(p) for p in result.proposals],
            "written": result.written,
            "pruned": result.pruned,
        }, indent=2))
        return

    from datetime import date
    click.echo(f"grain suggest — {date.today().isoformat()}")
    click.echo("")
    if not result.proposals:
        click.echo("No suggestions. Workspace has no actionable signals right now.")
        return
    for p in result.proposals:
        click.echo(f"SUGGESTION {p.id}")
        click.echo(f"  Type:      {p.kind}")
        if p.kind == "pick-up":
            click.echo(f"  Task:      {p.task_ref}" + (f" ({p.task_id})" if p.task_id else ""))
            if p.phase:
                click.echo(f"  Phase:     {p.phase}")
        else:
            click.echo(f"  Objective: {p.objective or p.title}")
            if p.suggested_phase:
                click.echo(f"  Phase:     {p.suggested_phase}")
        click.echo(f"  Signal:    {p.signal}" + (f" ({p.signal_ref})" if p.signal_ref else ""))
        if p.rationale:
            click.echo(f"  Rationale: {p.rationale}")
        click.echo(f"  → grain suggest accept {p.id}")
        click.echo(f"  → grain suggest dismiss {p.id}")
        click.echo("")
    n = len(result.proposals)
    click.echo(f"{n} suggestion{'s' if n != 1 else ''}. Run 'grain suggest list' to see all active proposals.")


@suggest_group.command("list")
@click.option("--status", default=None,
              type=click.Choice(["pending", "accepted", "dismissed", "expired", "all"]),
              help="Filter by proposal status (default: pending).")
@click.pass_context
def suggest_list(ctx, status):
    """List active proposals (default: pending)."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    from grain.services.suggest_service import list_proposals
    result = list_proposals(root, status=status)

    if fmt == "json":
        click.echo(json.dumps([_proposal_dict(p) for p in result.proposals], indent=2))
        return

    if not result.proposals:
        click.echo("suggest list: (empty)")
        return
    click.echo("suggest list:")
    for p in result.proposals:
        label = p.task_ref if p.kind == "pick-up" else (p.objective or p.title)
        click.echo(f"  {p.id:<20} {p.kind:<10} {p.status:<10} {label}")


@suggest_group.command("show")
@click.argument("proposal_id")
@click.pass_context
def suggest_show(ctx, proposal_id):
    """Show full detail for a proposal by id."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    from grain.services.suggest_service import show_proposal
    result = show_proposal(root, proposal_id)

    if fmt == "json":
        click.echo(json.dumps({
            "ok": result.ok,
            "path": result.path,
            "proposal": _proposal_dict(result.proposal) if result.proposal else None,
            "errors": result.errors,
        }, indent=2))
        return

    if not result.ok:
        for e in result.errors:
            click.echo(f"error  {e}", err=True)
        raise click.ClickException(f"proposal not found: {proposal_id}")

    p = result.proposal
    click.echo(f"suggest show: {p.id}")
    click.echo(f"  type       {p.kind}")
    click.echo(f"  status     {p.status}")
    click.echo(f"  generated  {p.created_at}")
    click.echo(f"  signal     {p.signal}")
    if p.signal_ref:
        click.echo(f"  signal_ref {p.signal_ref}")
    if p.kind == "pick-up":
        click.echo(f"  task_ref   {p.task_ref}")
        if p.task_id:
            click.echo(f"  task_id    {p.task_id}")
        if p.phase:
            click.echo(f"  phase      {p.phase}")
    else:
        click.echo(f"  objective  {p.objective or p.title}")
        if p.suggested_phase:
            click.echo(f"  phase      {p.suggested_phase}")
    if p.rationale:
        click.echo(f"  rationale  {p.rationale}")
    click.echo(f"  source_signals  ({len(p.source_signals)})")
    for s in p.source_signals:
        click.echo(f"    - {s}")
    click.echo(f"  path       {result.path}")


@suggest_group.command("accept")
@click.argument("proposal_id")
@click.option("--no-confirm", is_flag=True, default=False,
              help="Auto-confirm switching the active task for a pick-up accept. "
                   "new-task accept ALWAYS prompts regardless (D4).")
@click.pass_context
def suggest_accept(ctx, proposal_id, no_confirm):
    """Accept a proposal.

    pick-up activates the existing ready task; if a different task is already
    in_progress it refuses (or prompts) rather than clobbering current_task.md.
    new-task ALWAYS shows the proposed task.md and requires confirmation before
    any packet is created (D4).
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    from grain.services.suggest_service import accept

    # First pass — never auto-confirm; this surfaces needs_confirm + preview for new-task.
    result = accept(root, proposal_id, confirmed=False)

    # new-task confirmation gate (D4): always print proposed content; require explicit yes.
    if result.needs_confirm and result.kind == "new-task":
        if fmt == "json":
            click.echo(json.dumps({
                "ok": False,
                "needs_confirm": True,
                "proposal_id": result.proposal_id,
                "kind": result.kind,
                "proposed_task_md": result.proposed_task_md,
                "errors": result.errors,
            }, indent=2))
            return
        click.echo(f"suggest accept: {proposal_id} (new-task — confirmation required)")
        click.echo("")
        click.echo(result.proposed_task_md)
        # D4: new-task accept always prompts, even with --no-confirm.
        confirmed = click.confirm("Create this packet?", default=False)
        if not confirmed:
            click.echo("suggest accept: cancelled (no packet created)")
            return
        result = accept(root, proposal_id, confirmed=True)

    # pick-up active-task gate: another task is in_progress. Refuse (json/--no-confirm
    # off) or, in interactive text mode, prompt before switching the active task.
    elif result.needs_confirm and result.kind == "pick-up":
        if fmt == "json":
            click.echo(json.dumps({
                "ok": False,
                "needs_confirm": True,
                "proposal_id": result.proposal_id,
                "kind": result.kind,
                "task_ref": result.task_ref,
                "errors": result.errors,
            }, indent=2))
            raise SystemExit(1)
        for e in result.errors:
            click.echo(f"error  {e}", err=True)
        if no_confirm:
            result = accept(root, proposal_id, confirmed=True)
        else:
            if not click.confirm("Switch the active task and pick this up?", default=False):
                click.echo("suggest accept: cancelled (active task unchanged)")
                return
            result = accept(root, proposal_id, confirmed=True)

    if fmt == "json":
        click.echo(json.dumps({
            "ok": result.ok,
            "proposal_id": result.proposal_id,
            "kind": result.kind,
            "expired": result.expired,
            "task_ref": result.task_ref,
            "task_id": result.task_id,
            "files_created": result.files_created,
            "files_updated": result.files_updated,
            "errors": result.errors,
        }, indent=2))
        if not result.ok:
            raise SystemExit(1)
        return

    if not result.ok:
        for e in result.errors:
            click.echo(f"error  {e}", err=True)
        if result.expired:
            click.echo(f"suggest accept: {proposal_id} expired (signal resolved)")
            return
        raise click.ClickException(f"accept failed: {proposal_id}")

    click.echo(f"suggest accept: {proposal_id} accepted")
    click.echo(f"  kind       {result.kind}")
    if result.task_ref:
        click.echo(f"  task_ref   {result.task_ref}")
    if result.task_id:
        click.echo(f"  task_id    {result.task_id}")
    for f in result.files_created:
        click.echo(f"  created    {f}")
    for f in result.files_updated:
        click.echo(f"  updated    {f}")


@suggest_group.command("dismiss")
@click.argument("proposal_id")
@click.pass_context
def suggest_dismiss(ctx, proposal_id):
    """Dismiss a proposal (not re-surfaced for the same signal)."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    from grain.services.suggest_service import dismiss
    result = dismiss(root, proposal_id)

    if fmt == "json":
        click.echo(json.dumps({
            "ok": result.ok,
            "proposal_id": result.proposal_id,
            "path": result.path,
            "errors": result.errors,
        }, indent=2))
        if not result.ok:
            raise SystemExit(1)
        return

    if not result.ok:
        for e in result.errors:
            click.echo(f"error  {e}", err=True)
        raise click.ClickException(f"dismiss failed: {proposal_id}")

    click.echo(f"suggest dismiss: {proposal_id} dismissed")
    click.echo(f"  path  {result.path}")
