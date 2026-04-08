import dataclasses
import json
from dataclasses import dataclass, field

import click


@dataclass
class CommandResult:
    ok: bool = True
    command: str = ""
    repo: str = ""
    task_id: str = ""
    status: str = ""
    files_created: list[str] = field(default_factory=list)
    files_updated: list[str] = field(default_factory=list)
    files_skipped: list[str] = field(default_factory=list)
    files_blocked: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    primary_adapter: str = ""
    secondary_adapters: list[str] = field(default_factory=list)
    bootstrapped_task_id: str = ""


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
