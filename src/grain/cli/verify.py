# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import click

from grain.adapters.filesystem import resolve_repo_root
from grain.cli.output import print_result
from grain.domain.errors import ValidationError
from grain.services.verification_service import (
    ingest_verification_result,
    get_verification_request_status,
    submit_verification_request,
)


@click.group("verify")
def verify_group():
    """Submit and inspect external verification bridge artifacts."""


@verify_group.command("submit")
@click.option("--id", "task_id", required=True, metavar="TASK-####", help="Packet ID to submit for verification.")
@click.option(
    "--provider",
    default="assay",
    show_default=True,
    help="Verification provider identifier. Phase 28 currently supports only `assay`.",
)
@click.pass_context
def verify_submit(ctx, task_id, provider):
    """Create a packet-local verification request for external verification."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, record = submit_verification_request(root, task_id, provider=provider)
    if record is None:
        if fmt == "json":
            click.echo(json.dumps(dataclasses.asdict(result), indent=2))
        else:
            print_result(result, fmt=fmt)
        if any("not found" in error for error in result.errors):
            raise click.UsageError(f"packet '{task_id}' not found")
        raise ValidationError("verify submit failed", detail="; ".join(result.errors))

    if fmt == "json":
        data = dataclasses.asdict(result)
        data["verification_request"] = dataclasses.asdict(record)
        click.echo(json.dumps(data, indent=2))
        return

    click.echo("verify submit: ok")
    click.echo(f"  task_id           {record.task_id}")
    click.echo(f"  verification_id   {record.verification_id}")
    click.echo(f"  provider          {record.provider}")
    click.echo(f"  status            {record.status}")
    click.echo(f"  packet_dir        {record.packet_dir}")
    click.echo(f"  artifact_count    {len(record.artifact_paths)}")
    for path in result.files_created:
        click.echo(f"  created           {path}")
    for path in result.files_updated:
        click.echo(f"  updated           {path}")


@verify_group.command("status")
@click.option("--verification-id", required=True, metavar="VERIFY-####-NNN", help="Verification request ID to inspect.")
@click.pass_context
def verify_status(ctx, verification_id):
    """Inspect a pending or completed packet-local verification request."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, record = get_verification_request_status(root, verification_id)
    if record is None:
        if fmt == "json":
            click.echo(json.dumps(dataclasses.asdict(result), indent=2))
        else:
            print_result(result, fmt=fmt)
        raise ValidationError("verify status failed", detail="; ".join(result.errors))

    if fmt == "json":
        data = dataclasses.asdict(result)
        data["verification_request"] = dataclasses.asdict(record)
        click.echo(json.dumps(data, indent=2))
        return

    click.echo("verify status: ok")
    click.echo(f"  verification_id   {record.verification_id}")
    click.echo(f"  task_id           {record.task_id}")
    click.echo(f"  provider          {record.provider}")
    click.echo(f"  status            {record.status}")
    click.echo(f"  packet_dir        {record.packet_dir}")
    click.echo(f"  submitted_at      {record.submitted_at}")
    click.echo(f"  artifact_count    {len(record.artifact_paths)}")


@verify_group.command("ingest")
@click.option("--verification-id", required=True, metavar="VERIFY-####-NNN", help="Verification request ID to resolve.")
@click.option("--payload", "payload_path", required=True, metavar="PATH", help="Path to the Assay verification payload JSON file.")
@click.pass_context
def verify_ingest(ctx, verification_id, payload_path):
    """Ingest a completed Assay verification payload into packet-local artifacts."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, record = ingest_verification_result(root, verification_id, Path(payload_path))
    if record is None:
        if fmt == "json":
            click.echo(json.dumps(dataclasses.asdict(result), indent=2))
        else:
            print_result(result, fmt=fmt)
        raise ValidationError("verify ingest failed", detail="; ".join(result.errors))

    if fmt == "json":
        data = dataclasses.asdict(result)
        data["verification_result"] = dataclasses.asdict(record)
        click.echo(json.dumps(data, indent=2))
        return

    click.echo("verify ingest: ok")
    click.echo(f"  verification_id   {record.verification_id}")
    click.echo(f"  task_id           {record.task_id}")
    click.echo(f"  outcome           {record.outcome}")
    click.echo(f"  severity          {record.severity}")
    click.echo(f"  issue_type        {record.issue_type}")
    click.echo(f"  verified_at       {record.verified_at}")
    for path in result.files_created:
        click.echo(f"  created           {path}")
    for path in result.files_updated:
        click.echo(f"  updated           {path}")
