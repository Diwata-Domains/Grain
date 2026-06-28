# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json

import click

from grain.adapters.filesystem import resolve_repo_root
from grain.services.mcp_service import build_manifest, serve_stdio


@click.group("mcp")
def mcp_group():
    """Desktop and MCP wrapper commands."""


@mcp_group.command("manifest")
@click.option("--server-name", default="grain", show_default=True, help="Server name to emit in the MCP client manifest.")
@click.pass_context
def mcp_manifest(ctx, server_name):
    """Emit a local MCP client manifest for Grain."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)
    payload = build_manifest(root, server_name=server_name)

    if fmt == "json":
        click.echo(json.dumps(payload, indent=2))
        return

    click.echo("mcp manifest: ok")
    click.echo(f"  server_name       {server_name}")
    click.echo(f"  command           {payload['mcpServers'][server_name]['command']}")
    click.echo("  args")
    for arg in payload["mcpServers"][server_name]["args"]:
        click.echo(f"    - {arg}")


@mcp_group.command("serve")
@click.pass_context
def mcp_serve(ctx):
    """Serve the local Grain MCP wrapper over stdio."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    root = resolve_repo_root(repo)
    serve_stdio(root)
