# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

import dataclasses
import json
from pathlib import Path

import click

from grain.adapters.filesystem import resolve_repo_root
from grain.cli.output import print_result
from grain.domain.errors import GeneralError, ValidationError


@click.group("review")
def review_group():
    """Support acceptance, handoff, and completion workflows."""


@review_group.command("check")
@click.option("--id", "task_id", required=True, metavar="TASK-####", help="Packet ID to review.")
@click.pass_context
def review_check(ctx, task_id):
    """Run review-oriented validation on a packet."""
    from grain.services.review_service import check_packet_review_readiness

    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, report = check_packet_review_readiness(root, task_id)

    if report is None:
        if fmt == "json":
            click.echo(json.dumps(dataclasses.asdict(result), indent=2))
        else:
            print_result(result, fmt)
        raise click.UsageError(f"packet '{task_id}' not found")

    if fmt == "json":
        data = dataclasses.asdict(result)
        report_data = dataclasses.asdict(report)
        report_data["packet_dir"] = str(report.packet_dir)
        data["report"] = report_data
        click.echo(json.dumps(data, indent=2))
    else:
        print_result(result, fmt)
        click.echo(f"  task_id           {report.task_id}")
        click.echo(f"  packet_dir        {report.packet_dir.name}")
        click.echo(f"  packet_status     {report.packet_status or '(missing)'}")
        click.echo(f"  review_ready      {'yes' if report.review_ready else 'no'}")
        click.echo(f"  completion_ready  {'yes' if report.completion_ready else 'no'}")
        click.echo(f"  user_review_state {report.user_review_state or 'pending'}")
        click.echo(f"  verification_state {report.verification_state or 'not_run'}")
        if report.blockers:
            click.echo("  blockers")
            for blocker in report.blockers:
                click.echo(f"    - {blocker}")
        else:
            click.echo("  blockers         (none)")
        if report.warnings:
            click.echo("  warnings")
            for warning in report.warnings:
                click.echo(f"    - {warning}")

    if not result.ok:
        raise ValidationError("review check failed", detail="; ".join(report.blockers or result.errors))

    if fmt == "text":
        click.echo(f"  status            {report.packet_status}")

@review_group.command("handoff")
@click.option("--id", "task_id", required=True, metavar="TASK-####", help="Packet ID to hand off.")
@click.option(
    "--output",
    "output_path",
    default=None,
    metavar="PATH",
    help="Output markdown path (default: <packet-dir>/handoff.md).",
)
@click.pass_context
def review_handoff(ctx, task_id, output_path):
    """Generate or validate handoff artifacts."""
    from grain.services.handoff_service import materialize_handoff_artifact

    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, artifact, resolved_path = materialize_handoff_artifact(
        root,
        task_id,
        output_path=Path(output_path) if output_path else None,
    )

    if artifact is None:
        if any("not found" in err for err in result.errors):
            if fmt == "json":
                click.echo(json.dumps(dataclasses.asdict(result), indent=2))
            else:
                print_result(result, fmt)
            raise click.UsageError(f"packet '{task_id}' not found")
        if fmt == "json":
            click.echo(json.dumps(dataclasses.asdict(result), indent=2))
        else:
            print_result(result, fmt)
        raise ValidationError("review handoff failed", detail="; ".join(result.errors))

    if fmt == "json":
        data = dataclasses.asdict(result)
        handoff_data = dataclasses.asdict(artifact)
        handoff_data["packet_dir"] = str(artifact.packet_dir)
        data["handoff"] = handoff_data
        if resolved_path is not None:
            data["handoff"]["output_path"] = str(resolved_path)
        click.echo(json.dumps(data, indent=2))
    else:
        print_result(result, fmt)
        click.echo(f"  task_id           {artifact.task_id}")
        click.echo(f"  packet_dir        {artifact.packet_dir.name}")
        click.echo(f"  packet_status     {artifact.packet_status}")
        click.echo(f"  review_readiness  {artifact.review_readiness}")
        click.echo(f"  output            {resolved_path}")
        click.echo(f"  summary           {artifact.summary}")


@review_group.command("summary")
@click.option("--id", "task_id", required=True, metavar="TASK-####", help="Packet ID to summarize.")
@click.pass_context
def review_summary(ctx, task_id):
    """Produce a structured summary of packet state for final inspection."""
    from grain.services.review_service import build_packet_review_summary

    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, summary = build_packet_review_summary(root, task_id)

    if summary is None:
        if any("not found" in err for err in result.errors):
            if fmt == "json":
                click.echo(json.dumps(dataclasses.asdict(result), indent=2))
            else:
                print_result(result, fmt)
            raise click.UsageError(f"packet '{task_id}' not found")

        if fmt == "json":
            click.echo(json.dumps(dataclasses.asdict(result), indent=2))
        else:
            print_result(result, fmt)
        raise GeneralError("review summary failed", detail="; ".join(result.errors))

    if fmt == "json":
        data = dataclasses.asdict(result)
        summary_data = dataclasses.asdict(summary)
        summary_data["packet_dir"] = str(summary.packet_dir)
        data["summary"] = summary_data
        click.echo(json.dumps(data, indent=2))
        return

    print_result(result, fmt)
    click.echo(f"  task_id           {summary.task_id}")
    click.echo(f"  packet_dir        {summary.packet_dir.name}")
    click.echo(f"  packet_status     {summary.packet_status or '(missing)'}")
    click.echo(f"  phase             {summary.phase or '(missing)'}")
    click.echo(f"  review_ready      {'yes' if summary.review_ready else 'no'}")
    click.echo(f"  completion_ready  {'yes' if summary.completion_ready else 'no'}")
    click.echo(f"  user_review_state {summary.user_review_state or 'pending'}")
    click.echo(f"  verification_state {summary.verification_state or 'not_run'}")
    click.echo(f"  recommended_next_status  {summary.recommended_next_status}")
    click.echo("  packet_summary")
    packet_summary_lines = summary.packet_summary.splitlines() or ["(none)"]
    for line in packet_summary_lines:
        click.echo(f"    {line}")
    click.echo("  validation_findings")
    if summary.validation_findings:
        for finding in summary.validation_findings:
            click.echo(f"    - {finding}")
    else:
        click.echo("    (none)")
    click.echo("  warnings")
    if summary.warnings:
        for warning in summary.warnings:
            click.echo(f"    - {warning}")
    else:
        click.echo("    (none)")
    click.echo("  next_actions")
    for action in summary.next_actions:
        click.echo(f"    - {action}")
