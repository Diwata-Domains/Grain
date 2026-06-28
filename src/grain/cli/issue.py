# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""grain issue — file a GitHub issue directly via the REST API.

The standalone, headless API path. Unlike ``grain report`` (browser-confirmed
URL) and ``grain notes publish`` (publishes a logged note), ``grain issue create``
files an issue immediately from explicit arguments and never touches the notes
log. The token is read from ``GRAIN_GITHUB_TOKEN`` only.
"""

from __future__ import annotations

import json

import click

from grain.adapters.filesystem import resolve_repo_root


@click.group("issue")
def issue_group():
    """File GitHub issues against the workspace's configured repo."""


@issue_group.command("create")
@click.option("--title", required=True, help="Issue title.")
@click.option("--type", "issue_type", default="bug",
              type=click.Choice(["bug", "feature", "friction", "ux"]),
              help="Issue type; maps to a GitHub label (default: bug).")
@click.option("--body", "body", default="", help="Issue body (optional).")
@click.pass_context
def issue_create(ctx, title, issue_type, body):
    """Create a GitHub issue via the API on github.repo from docs_manifest.yaml.

    \b
    Examples:
      grain issue create --title "phase close needs metrics" --type friction
      grain issue create --title "init crash" --type bug --body "stack on --name"
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    from grain.adapters.manifest import load_github_config
    from grain.services.github_service import create_issue, label_for_type

    gh = load_github_config(root)
    label = label_for_type(issue_type)
    result = create_issue(gh.repo, title, body, [label])

    if fmt == "json":
        click.echo(json.dumps({
            "ok": result.ok,
            "issue_url": result.issue_url,
            "issue_number": result.issue_number,
            "title": result.title,
            "labels": result.labels,
            "repo": result.repo,
            "errors": result.errors,
        }, indent=2))
        return

    if not result.ok:
        for e in result.errors:
            click.echo(f"error  {e}", err=True)
        raise click.ClickException("issue create failed")

    click.echo("issue create: ok")
    click.echo(f"  repo   {result.repo}")
    click.echo(f"  label  {', '.join(result.labels)}")
    click.echo(f"  → {result.issue_url}")
