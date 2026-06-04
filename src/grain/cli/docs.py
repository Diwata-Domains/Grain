import json

import click

from grain.adapters.filesystem import resolve_repo_root
from grain.cli.output import print_result
from grain.domain.errors import ValidationError
from grain.services import docs_service


@click.group("docs")
def docs_group():
    """Inspect and validate repository documentation state."""


@docs_group.command("validate")
@click.pass_context
def docs_validate(ctx):
    """Validate required documentation structure and contracts."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result = docs_service.validate_docs(root)
    print_result(result, fmt=fmt)

    if not result.ok:
        raise ValidationError("docs validation failed", detail=f"{len(result.errors)} error(s)")


@docs_group.command("index")
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    show_default=True,
    help="Print intended output without writing files.",
)
@click.pass_context
def docs_index(ctx, dry_run):
    """Generate or refresh docs/runtime/docs_index.md from the manifest."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result = docs_service.generate_index(root, dry_run=dry_run)
    print_result(result, fmt=fmt)

    if not result.ok:
        raise ValidationError("docs index generation failed")


@docs_group.command("show")
@click.argument("doc_id")
@click.pass_context
def docs_show(ctx, doc_id):
    """Display doc metadata or path information for a known document."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, record = docs_service.show_doc(root, doc_id)

    if not result.ok:
        for err in result.errors:
            click.echo(f"  error     {err}", err=True)
        raise click.UsageError(f"Doc '{doc_id}' not found")

    if fmt == "json":
        import dataclasses
        data = dataclasses.asdict(result)
        data["doc"] = {
            "id": record.id,
            "path": record.path,
            "layer": record.layer,
            "authority": record.authority,
            "purpose": record.purpose,
            "editable_by_agents": record.editable_by_agents,
            "read_when": record.read_when,
        }
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo("docs show: ok")
        click.echo(f"  id                  {record.id}")
        click.echo(f"  path                {record.path}")
        click.echo(f"  layer               {record.layer}")
        click.echo(f"  authority           {record.authority}")
        click.echo(f"  purpose             {record.purpose}")
        click.echo(f"  editable_by_agents  {str(record.editable_by_agents).lower()}")
