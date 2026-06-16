# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

import dataclasses
import json
from pathlib import Path

import click

from grain.adapters.filesystem import resolve_repo_root
from grain.domain.orchestrator import OrchestratorPlan
from grain.services.orchestration_service import (
    analyze_scope_signals,
    build_phase_level_plan,
    build_task_level_plan,
)

_PROPOSALS_DIR = Path("docs/working/proposals")


@click.group("orchestrate")
def orchestrate_group():
    """Produce orchestration scope signals and draft plan proposals."""


@orchestrate_group.command("scope")
@click.option("--scope", "scope_summary", required=True, help="Work scope to analyze.")
@click.option(
    "--adapter",
    "adapter_ids",
    multiple=True,
    help="Restrict analysis to one or more adapter IDs.",
)
@click.pass_context
def orchestrate_scope(ctx, scope_summary, adapter_ids):
    """Analyze a work scope and report adapter/domain signals."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, payload = analyze_scope_signals(
        root,
        scope_summary,
        adapter_ids=list(adapter_ids),
    )
    if payload is None:
        if fmt == "json":
            click.echo(json.dumps(dataclasses.asdict(result), indent=2))
        else:
            click.echo("orchestrate scope: failed")
            for err in result.errors:
                click.echo(f"  error     {err}", err=True)
        raise click.ClickException("orchestrate scope failed")

    if fmt == "json":
        data = dataclasses.asdict(result)
        data["scope_analysis"] = payload
        click.echo(json.dumps(data, indent=2))
        return

    click.echo("orchestrate scope: ok")
    click.echo(f"  scope             {payload['scope_summary']}")
    if payload["adapter_filter"]:
        click.echo(f"  adapter_filter    {', '.join(payload['adapter_filter'])}")
    click.echo(f"  active_adapters   {len(payload['active_adapters'])}")
    for adapter_id in payload["active_adapters"]:
        click.echo(f"    - {adapter_id}")
    if payload["cross_domain_flags"]:
        click.echo("  cross_domain_flags")
        for domain in payload["cross_domain_flags"]:
            click.echo(f"    - {domain}")
    click.echo(f"  adapter_signals   {len(payload['adapter_signals'])}")
    for signal in payload["adapter_signals"]:
        status = "active" if signal["active"] else "inactive"
        click.echo(
            f"    - {signal['adapter_id']} ({signal['domain_type']}) "
            f"score={signal['score']} {status}"
        )


@orchestrate_group.command("plan")
@click.option("--scope", "scope_summary", required=True, help="Work scope to plan.")
@click.option(
    "--adapter",
    "adapter_ids",
    multiple=True,
    help="Restrict planning to one or more adapter IDs.",
)
@click.pass_context
def orchestrate_plan(ctx, scope_summary, adapter_ids):
    """Generate a draft OrchestratorPlan and write it to proposals."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    is_phase_scope = _is_phase_scope(scope_summary)
    if is_phase_scope:
        result, plan = build_phase_level_plan(
            root,
            scope_summary,
            adapter_ids=list(adapter_ids),
            produced_by="orchestration_service.phase.cli",
        )
        plan_mode = "phase"
    else:
        result, plan = build_task_level_plan(
            root,
            scope_summary,
            adapter_ids=list(adapter_ids),
            produced_by="orchestration_service.task.cli",
        )
        plan_mode = "task"

    if plan is None:
        if fmt == "json":
            click.echo(json.dumps(dataclasses.asdict(result), indent=2))
        else:
            click.echo("orchestrate plan: failed")
            for err in result.errors:
                click.echo(f"  error     {err}", err=True)
        raise click.ClickException("orchestrate plan failed")

    proposal_path = _write_plan_proposal(root, plan)

    if fmt == "json":
        data = dataclasses.asdict(result)
        data["plan_mode"] = plan_mode
        data["proposal_path"] = str(proposal_path)
        data["orchestrator_plan"] = dataclasses.asdict(plan)
        click.echo(json.dumps(data, indent=2))
        return

    click.echo("orchestrate plan: ok")
    click.echo(f"  plan_mode         {plan_mode}")
    click.echo(f"  plan_id           {plan.plan_id}")
    click.echo(f"  proposal_path     {proposal_path}")
    click.echo(f"  active_adapters   {len(plan.active_adapters)}")
    for adapter_id in plan.active_adapters:
        click.echo(f"    - {adapter_id}")
    click.echo(f"  packet_candidates {len(plan.packet_candidates)}")
    for candidate in plan.packet_candidates:
        click.echo(
            f"    - {candidate.candidate_id}: {candidate.title} "
            f"(adapter={candidate.primary_adapter or 'none'})"
        )
    click.echo(f"  dependency_links  {len(plan.dependency_links)}")
    click.echo(f"  split_recommendations  {len(plan.split_recommendations)}")
    for candidate_id in plan.split_recommendations:
        click.echo(f"    - {candidate_id}")


@orchestrate_group.command("accept")
@click.option("--plan", "plan_id", required=True, help="Orchestrator plan ID to accept (e.g. OP-ABC12345).")
@click.pass_context
def orchestrate_accept(ctx, plan_id):
    """Mark a plan proposal as accepted for loop ordering integration."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    proposal_path = root / _PROPOSALS_DIR / f"{plan_id}.json"
    if not proposal_path.exists():
        raise click.ClickException(f"plan proposal not found: {proposal_path}")

    try:
        payload = json.loads(proposal_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise click.ClickException(f"invalid plan JSON: {exc}") from exc

    payload["status"] = "accepted"
    proposal_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if fmt == "json":
        click.echo(
            json.dumps(
                {
                    "ok": True,
                    "command": "orchestrate accept",
                    "plan_id": plan_id,
                    "proposal_path": str(proposal_path.relative_to(root)),
                    "status": "accepted",
                },
                indent=2,
            )
        )
        return

    click.echo("orchestrate accept: ok")
    click.echo(f"  plan_id           {plan_id}")
    click.echo(f"  proposal_path     {proposal_path.relative_to(root)}")
    click.echo("  status            accepted")


def _is_phase_scope(scope_summary: str) -> bool:
    lowered = scope_summary.lower()
    return any(token in lowered for token in ("phase", "replan", "reshape"))


def _write_plan_proposal(root: Path, plan: OrchestratorPlan) -> Path:
    proposals_dir = root / _PROPOSALS_DIR
    proposals_dir.mkdir(parents=True, exist_ok=True)
    proposal_path = proposals_dir / f"{plan.plan_id}.json"
    proposal_path.write_text(
        json.dumps(dataclasses.asdict(plan), indent=2) + "\n",
        encoding="utf-8",
    )
    return proposal_path
