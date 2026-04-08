import click
from pathlib import Path

from forge.services.init_service import init_repo
from forge.cli.output import CommandResult, print_result


@click.command("init")
@click.option("--force", is_flag=True, default=False, show_default=True, help="Overwrite existing non-canonical files.")
@click.option("--dry-run", is_flag=True, default=False, show_default=True, help="Report intended actions without writing anything.")
@click.option("--primary-adapter", default="", show_default=False, help="Primary adapter ID for this project (e.g. code_adapter).")
@click.option("--secondary-adapter", multiple=True, help="Secondary adapter ID (repeatable).")
@click.option("--bootstrap", is_flag=True, default=False, show_default=True, help="Create a starter task packet and initialize current_task.md after scaffolding.")
@click.pass_context
def init_cmd(ctx, force, dry_run, primary_adapter, secondary_adapter, bootstrap):
    """Initialize repository structure and baseline toolkit artifacts."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = Path(repo).resolve() if repo else Path.cwd()

    svc_result = init_repo(
        root=root,
        force=force,
        dry_run=dry_run,
        primary_adapter=primary_adapter,
        secondary_adapters=list(secondary_adapter),
        bootstrap=bootstrap,
    )

    base_warnings = ["dry-run: no files written"] if dry_run else []
    result = CommandResult(
        ok=True,
        command="init",
        repo=str(root),
        files_created=svc_result.created,
        files_updated=svc_result.updated,
        files_skipped=svc_result.skipped,
        files_blocked=svc_result.blocked,
        primary_adapter=svc_result.primary_adapter,
        secondary_adapters=svc_result.secondary_adapters,
        bootstrapped_task_id=svc_result.bootstrapped_task_id,
        warnings=base_warnings + svc_result.adapter_warnings,
    )

    print_result(result, fmt=fmt)
