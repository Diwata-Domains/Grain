import dataclasses
import json
from pathlib import Path

import click

from forge.adapters.export import write_context_markdown_export
from forge.adapters.filesystem import resolve_repo_root
from forge.domain.errors import GeneralError, ValidationError
from forge.services import context_service


@click.group("context")
def context_group():
    """Prepare minimal execution context for one task packet."""


@context_group.command("build")
@click.option("--id", "task_id", required=True, metavar="TASK-####", help="Packet ID to build context for.")
@click.option("--include-working", is_flag=True, default=False, help="Include selected working docs.")
@click.option(
    "--tag",
    "context_tags",
    multiple=True,
    help="Context tag(s) used for doc selection. Defaults to running_tasks when omitted.",
)
@click.pass_context
def context_build(ctx, task_id, include_working, context_tags):
    """Assemble context for a packet."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    tag_set = set(context_tags) if context_tags else None
    result, bundle = context_service.build_context_bundle(
        root,
        task_id,
        include_working_docs=include_working,
        context_tags=tag_set,
    )

    if not result.ok:
        if any("not found" in err for err in result.errors):
            for err in result.errors:
                click.echo(f"  error     {err}", err=True)
            raise click.UsageError(f"packet '{task_id}' not found")
        raise ValidationError("context build failed", detail="; ".join(result.errors))

    if bundle is None:
        raise GeneralError("context build failed", detail="bundle missing on successful result")

    if fmt == "json":
        data = dataclasses.asdict(result)
        data["bundle"] = {
            "task_id": bundle.task_id,
            "packet_dir": str(bundle.packet_dir),
            "packet_files": [
                {
                    "name": packet_file.name,
                    "path": str(packet_file.path),
                    "present": packet_file.present,
                }
                for packet_file in bundle.packet_files
            ],
            "selected_canonical_docs": [
                {
                    "id": record.id,
                    "path": record.path,
                    "layer": record.layer,
                    "purpose": record.purpose,
                    "authority": record.authority,
                    "editable_by_agents": record.editable_by_agents,
                    "read_when": record.read_when,
                }
                for record in bundle.selected_canonical_docs
            ],
            "selected_working_docs": [
                {
                    "id": record.id,
                    "path": record.path,
                    "layer": record.layer,
                    "purpose": record.purpose,
                    "authority": record.authority,
                    "editable_by_agents": record.editable_by_agents,
                    "read_when": record.read_when,
                }
                for record in bundle.selected_working_docs
            ],
            "export_metadata": bundle.export_metadata,
        }
        click.echo(json.dumps(data, indent=2))
        return

    click.echo("context build: ok")
    click.echo(f"  task_id           {bundle.task_id}")
    click.echo(f"  packet_dir        {bundle.packet_dir.name}")
    click.echo(f"  packet_files      {len(bundle.packet_files)}")
    click.echo(f"  canonical_docs    {len(bundle.selected_canonical_docs)}")
    click.echo(f"  working_docs      {len(bundle.selected_working_docs)}")
    click.echo(f"  sources           {len(bundle.export_metadata.get('sources', []))}")
    for source in bundle.export_metadata.get("sources", []):
        click.echo(f"    - {source}")


@context_group.command("show")
@click.option("--id", "task_id", required=True, metavar="TASK-####", help="Packet ID to show context for.")
@click.option("--include-working", is_flag=True, default=False, help="Include selected working docs.")
@click.option(
    "--tag",
    "context_tags",
    multiple=True,
    help="Context tag(s) used for doc selection. Defaults to running_tasks when omitted.",
)
@click.pass_context
def context_show(ctx, task_id, include_working, context_tags):
    """Display selected docs and packet materials for a packet."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    tag_set = set(context_tags) if context_tags else None
    result, bundle = context_service.build_context_bundle(
        root,
        task_id,
        include_working_docs=include_working,
        context_tags=tag_set,
    )

    if not result.ok:
        if any("not found" in err for err in result.errors):
            for err in result.errors:
                click.echo(f"  error     {err}", err=True)
            raise click.UsageError(f"packet '{task_id}' not found")
        raise ValidationError("context show failed", detail="; ".join(result.errors))

    if bundle is None:
        raise GeneralError("context show failed", detail="bundle missing on successful result")

    if fmt == "json":
        data = dataclasses.asdict(result)
        data["bundle"] = {
            "task_id": bundle.task_id,
            "packet_dir": str(bundle.packet_dir),
            "packet_files": [
                {
                    "name": packet_file.name,
                    "path": str(packet_file.path),
                    "present": packet_file.present,
                }
                for packet_file in bundle.packet_files
            ],
            "selected_canonical_docs": [
                {
                    "id": record.id,
                    "path": record.path,
                }
                for record in bundle.selected_canonical_docs
            ],
            "selected_working_docs": [
                {
                    "id": record.id,
                    "path": record.path,
                }
                for record in bundle.selected_working_docs
            ],
            "export_metadata": bundle.export_metadata,
        }
        click.echo(json.dumps(data, indent=2))
        return

    click.echo("context show: ok")
    click.echo(f"  task_id           {bundle.task_id}")
    click.echo(f"  packet_dir        {bundle.packet_dir.name}")
    click.echo("  packet_files")
    for packet_file in bundle.packet_files:
        click.echo(f"    {packet_file.name:<24}  present")
    click.echo("  canonical_docs")
    if not bundle.selected_canonical_docs:
        click.echo("    (none)")
    for record in bundle.selected_canonical_docs:
        click.echo(f"    {record.id:<24}  {record.path}")
    click.echo("  working_docs")
    if not bundle.selected_working_docs:
        click.echo("    (none)")
    for record in bundle.selected_working_docs:
        click.echo(f"    {record.id:<24}  {record.path}")


@context_group.command("export")
@click.option("--id", "task_id", required=True, metavar="TASK-####", help="Packet ID to export context for.")
@click.option(
    "--output",
    "output_path",
    default=None,
    help="Output markdown path (default: <packet-dir>/context_export.md).",
)
@click.option("--include-working", is_flag=True, default=False, help="Include selected working docs.")
@click.option(
    "--tag",
    "context_tags",
    multiple=True,
    help="Context tag(s) used for doc selection. Defaults to running_tasks when omitted.",
)
@click.pass_context
def context_export(ctx, task_id, output_path, include_working, context_tags):
    """Export context bundle for external tool usage."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    tag_set = set(context_tags) if context_tags else None
    result, bundle = context_service.build_context_bundle(
        root,
        task_id,
        include_working_docs=include_working,
        context_tags=tag_set,
    )

    if not result.ok:
        if any("not found" in err for err in result.errors):
            for err in result.errors:
                click.echo(f"  error     {err}", err=True)
            raise click.UsageError(f"packet '{task_id}' not found")
        raise ValidationError("context export failed", detail="; ".join(result.errors))

    if bundle is None:
        raise GeneralError("context export failed", detail="bundle missing on successful result")

    source_metadata = context_service.build_source_metadata(root, bundle)

    if fmt == "json":
        data = dataclasses.asdict(result)
        data["export"] = {
            "task_id": bundle.task_id,
            "generated_at": bundle.export_metadata.get("generated_at"),
            "sources": source_metadata,
        }
        click.echo(json.dumps(data, indent=2))
        return

    export_path = write_context_markdown_export(
        root=root,
        bundle=bundle,
        output_path=Path(output_path) if output_path else None,
    )

    click.echo("context export: ok")
    click.echo(f"  task_id           {bundle.task_id}")
    click.echo(f"  output            {export_path}")
    click.echo(f"  sources           {len(source_metadata)}")
