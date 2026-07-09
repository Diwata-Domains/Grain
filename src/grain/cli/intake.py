# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""grain intake — import promoted Assay tickets as Grain task packets.

The pull side of the Assay-to-Grain seam. Assay's Task-5 API exposes promoted
tickets; ``grain intake pull`` mints a real ``TASK-####`` packet for each one
not already imported (by ``assay_vid``) and acks it back to Assay. Endpoint and
key are read from the environment only — never written to any workspace file.
"""

from __future__ import annotations

import json
import os

import click

from grain.adapters.filesystem import resolve_repo_root
from grain.domain.errors import ConfigError, GeneralError

_ENDPOINT_ENV = "GRAIN_ASSAY_ENDPOINT"
_KEY_ENV = "GRAIN_ASSAY_KEY"


@click.group("intake")
def intake_group():
    """Import promoted tickets from Assay as Grain task packets."""


@intake_group.command("pull")
@click.option("--phase", type=int, required=True, help="Phase number to import tickets into.")
@click.option(
    "--task-num", type=int, default=None,
    help="Starting within-phase task number (auto-computed from existing packets if omitted).",
)
@click.pass_context
def intake_pull(ctx, phase, task_num):
    """Pull promoted tickets from Assay and mint task packets for the new ones.

    \b
    Examples:
      grain intake pull --phase 20
      grain intake pull --phase 20 --task-num 3
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    endpoint = os.environ.get(_ENDPOINT_ENV, "")
    if not endpoint.strip():
        raise ConfigError(
            f"{_ENDPOINT_ENV} is not set",
            detail=f"set {_ENDPOINT_ENV} to the Assay API base URL, e.g. https://assay.example.com",
        )

    key = os.environ.get(_KEY_ENV, "")
    if not key.strip():
        raise ConfigError(
            f"{_KEY_ENV} is not set",
            detail=f"set {_KEY_ENV} to the Assay API key",
        )

    from grain.services.intake_service import pull_promotions

    result = pull_promotions(root, phase, task_num, endpoint, key)

    if fmt == "json":
        click.echo(json.dumps({
            "ok": result.ok,
            "imported": result.imported,
            "skipped": result.skipped,
            "errors": result.errors,
        }, indent=2))
    else:
        click.echo(f"intake pull: {'ok' if result.ok else 'failed'}")
        for item in result.imported:
            click.echo(f"  imported  {item['task_id']}  ({item['assay_vid']})  {item['packet_dir']}")
        for vid in result.skipped:
            click.echo(f"  skipped   {vid}  (already imported)")
        for err in result.errors:
            click.echo(f"  error     {err}", err=True)

    if not result.ok:
        raise GeneralError("intake pull failed", detail="; ".join(result.errors))
