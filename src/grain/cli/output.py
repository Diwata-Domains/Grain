# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

import dataclasses
import json

import click

# CommandResult moved to the domain layer to break the cli<->services import cycle
# (services import it without pulling in grain.cli). Re-exported here for callers
# that still do `from grain.cli.output import CommandResult`.
from grain.domain.command_result import CommandResult

__all__ = ["CommandResult", "print_result"]


def print_result(result: CommandResult, fmt: str = "text") -> None:
    """Print a CommandResult in the requested format (text or json)."""
    if fmt == "json":
        click.echo(json.dumps(dataclasses.asdict(result), indent=2))
        return

    # text output
    if result.command:
        label = "ok" if result.ok else "failed"
        click.echo(f"{result.command}: {label}")

    for path in result.files_created:
        click.echo(f"  created   {path}")
    for path in result.files_updated:
        click.echo(f"  updated   {path}")
    for path in result.files_skipped:
        click.echo(f"  skipped   {path}")
    for path in result.files_blocked:
        click.echo(f"  blocked   {path}")
    if result.primary_adapter:
        click.echo(f"  adapter   primary={result.primary_adapter}")
    for aid in result.secondary_adapters:
        click.echo(f"  adapter   secondary={aid}")
    if result.bootstrapped_task_id:
        click.echo(f"  bootstrap {result.bootstrapped_task_id}")
    for warn in result.warnings:
        click.echo(f"  warning   {warn}")
    for err in result.errors:
        click.echo(f"  error     {err}", err=True)
