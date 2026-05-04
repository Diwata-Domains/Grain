from __future__ import annotations

import click

from grain.adapters.filesystem import resolve_repo_root
from grain.tui.app import launch_tui


@click.command("tui")
@click.pass_context
def tui_cmd(ctx: click.Context) -> None:
    """Launch the Grain terminal UI shell."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    root = resolve_repo_root(repo)

    try:
        launch_tui(root)
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc
