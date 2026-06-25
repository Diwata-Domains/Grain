# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""CLI command group for grain metrics operations (read-only, cached)."""

from __future__ import annotations

import json

import click

from grain.adapters.filesystem import resolve_repo_root


def _phase_dict(p) -> dict:
    return {
        "phase": p.phase,
        "closed_at": p.closed_at,
        "opened_at": p.opened_at,
        "duration_days": p.duration_days,
        "tasks_done": p.tasks_done,
        "tasks_total": p.tasks_total,
        "closure_rate": p.closure_rate,
        "grain_version": p.grain_version,
        "coverage": p.coverage,
    }


def _fmt_duration(days) -> str:
    if days is None:
        return "—"
    return f"{days}d"


def _fmt_closure(rate, done: int, total) -> str:
    if rate is not None:
        return f"{rate * 100:.0f}% ({done}/{total})"
    return f"{done} done"


@click.group("metrics", invoke_without_command=True)
@click.option("--phase", type=int, default=None, metavar="N",
              help="Show single-phase detail for phase N.")
@click.option("--no-cache", is_flag=True, default=False,
              help="Recompute instead of reading the 1-hour cache.")
@click.pass_context
def metrics_group(ctx, phase, no_cache):
    """Show per-phase workflow velocity and stop-reason metrics.

    \b
    Examples:
      grain metrics
      grain metrics --phase 31
      grain metrics --no-cache
      grain metrics export
      grain metrics --format json
    """
    if ctx.invoked_subcommand is not None:
        return

    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    from grain.services.metrics_service import compute_metrics, phase_metrics

    use_cache = not no_cache

    # ── Single-phase detail ─────────────────────────────────────────────────────
    if phase is not None:
        detail = phase_metrics(root, phase, use_cache=use_cache)
        if fmt == "json":
            click.echo(json.dumps(
                _phase_dict(detail) if detail else {"ok": False, "phase": phase},
                indent=2,
            ))
            return
        if detail is None:
            click.echo(f"error  no archived metrics for phase {phase}", err=True)
            raise click.UsageError(f"phase not found: {phase}")
        click.echo(f"grain metrics — phase {detail.phase}")
        click.echo(f"  opened_at     {detail.opened_at or '—'}")
        click.echo(f"  closed_at     {detail.closed_at or '—'}")
        click.echo(f"  duration      {_fmt_duration(detail.duration_days)}")
        click.echo(f"  tasks_done    {detail.tasks_done}")
        total_str = str(detail.tasks_total) if detail.tasks_total is not None else "—"
        click.echo(f"  tasks_total   {total_str}")
        click.echo(f"  closure       {_fmt_closure(detail.closure_rate, detail.tasks_done, detail.tasks_total)}")
        click.echo(f"  grain_version {detail.grain_version or '—'}")
        click.echo(f"  coverage      {detail.coverage}")
        return

    # ── Summary across all phases ───────────────────────────────────────────────
    result = compute_metrics(root, use_cache=use_cache)

    if fmt == "json":
        click.echo(json.dumps({
            "ok": result.ok,
            "computed_at": result.computed_at,
            "cached": result.cached,
            "phase_count": result.phase_count,
            "total_tasks_done": result.total_tasks_done,
            "coverage_note": result.coverage_note,
            "phases": [_phase_dict(p) for p in result.phases],
            "stop_reasons": [
                {"reason": s.reason, "count": s.count} for s in result.stop_reasons
            ],
        }, indent=2))
        return

    click.echo("grain metrics")
    if not result.phases:
        click.echo("  (no archived phases — nothing to measure yet)")
    else:
        click.echo(f"  phases        {result.phase_count}")
        click.echo(f"  tasks_done    {result.total_tasks_done}")
        click.echo("")
        click.echo(f"  {'phase':<7}{'closed':<13}{'dur':<7}{'tasks':<8}{'closure'}")
        for p in result.phases:
            click.echo(
                f"  {p.phase:<7}{(p.closed_at or '—'):<13}"
                f"{_fmt_duration(p.duration_days):<7}{p.tasks_done:<8}"
                f"{_fmt_closure(p.closure_rate, p.tasks_done, p.tasks_total)}"
            )

    if result.stop_reasons:
        click.echo("")
        click.echo("  stop reasons")
        for s in result.stop_reasons:
            click.echo(f"    {s.count:<4} {s.reason}")

    if result.coverage_note:
        click.echo("")
        click.echo(f"  note  {result.coverage_note}")


@metrics_group.command("export")
@click.pass_context
def metrics_export(ctx):
    """Dump the full metrics history as JSON (recomputed, ignores cache).

    \b
    Examples:
      grain metrics export
      grain metrics export --format json
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    root = resolve_repo_root(repo)

    from grain.services.metrics_service import export_metrics
    data = export_metrics(root)
    click.echo(json.dumps(data, indent=2))
