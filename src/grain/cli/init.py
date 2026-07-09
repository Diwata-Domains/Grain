# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

import click
from pathlib import Path

from grain.services.init_service import init_repo, update_agents_only
from grain.cli.output import CommandResult, print_result


@click.command("init")
@click.option("--force", is_flag=True, default=False, show_default=True, help="Overwrite existing non-canonical files.")
@click.option("--dry-run", is_flag=True, default=False, show_default=True, help="Report intended actions without writing anything.")
@click.option("--primary-adapter", default="", show_default=False, help="Primary adapter ID for this project (e.g. code_adapter).")
@click.option("--secondary-adapter", multiple=True, help="Secondary adapter ID (repeatable).")
@click.option("--bootstrap", is_flag=True, default=False, show_default=True, help="Create a starter task packet and initialize current_task.md after scaffolding.")
@click.option("--update-agents", "update_agents", is_flag=True, default=False, show_default=True, help="Only regenerate the grain block in AGENTS.md; skip full init.")
@click.option("--name", "project_name", default="", show_default=False, help="Project name — substitutes '[Your Project Name]' in all seeded files.")
@click.option("--type", "project_type", default="", show_default=False, help="Project type — substitutes placeholder in docs_manifest.yaml (e.g. cli_tool, web_app, service).")
@click.pass_context
def init_cmd(ctx, force, dry_run, primary_adapter, secondary_adapter, bootstrap, update_agents, project_name, project_type):
    """Initialize repository structure and baseline toolkit artifacts."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = Path(repo).resolve() if repo else Path.cwd()

    if update_agents:
        svc_result = update_agents_only(root, dry_run=dry_run)
    else:
        svc_result = init_repo(
            root=root,
            force=force,
            dry_run=dry_run,
            primary_adapter=primary_adapter,
            secondary_adapters=list(secondary_adapter),
            bootstrap=bootstrap,
            project_name=project_name,
            project_type=project_type,
        )

    base_warnings = ["dry-run: no files written"] if dry_run else []
    if not update_agents and not project_name:
        base_warnings.append(
            "project name not set — run `grain init --name <name>` or edit '[Your Project Name]' in seeded files"
        )
    agents_note = _agents_md_note(svc_result.agents_md_action, svc_result.claude_md_exists)

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
        warnings=base_warnings + svc_result.adapter_warnings + ([agents_note] if agents_note else []),
    )

    print_result(result, fmt=fmt)


def _agents_md_note(action: str, claude_md_exists: bool) -> str:
    notes = {
        "created": "AGENTS.md created with grain workflow instructions",
        "updated": "AGENTS.md grain block updated",
        "appended": "grain workflow instructions appended to existing AGENTS.md",
        "skipped": "",
    }
    note = notes.get(action, "")
    if note and claude_md_exists:
        note += " (CLAUDE.md also exists — grain block is in AGENTS.md which Claude Code reads)"
    return note
