# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

import json
from pathlib import Path

import click

from grain.adapters.adapter_config import load_adapter_profiles
from grain.adapters.filesystem import resolve_repo_root
from grain.domain.errors import GeneralError


@click.group("adapter")
def adapter_group():
    """Inspect adapter profiles and capability-facing metadata."""


@adapter_group.command("list")
@click.pass_context
def adapter_list(ctx):
    """List known adapter profiles."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    profiles = load_adapter_profiles(root)

    if fmt == "json":
        data = {
            "ok": True,
            "command": "adapter list",
            "repo": str(root),
            "profiles": [
                {
                    "adapter_id": profile.adapter_id,
                    "domain_type": profile.domain_type,
                    "applies_to": profile.applies_to,
                }
                for profile in profiles
            ],
            "count": len(profiles),
            "source_path": "docs/runtime/adapter_profiles.md",
        }
        click.echo(json.dumps(data, indent=2))
        return

    click.echo("adapter list: ok")
    click.echo("  source            docs/runtime/adapter_profiles.md")
    click.echo(f"  adapters          {len(profiles)}")
    for profile in profiles:
        applies = ", ".join(profile.applies_to) if profile.applies_to else "(none)"
        click.echo(f"  {profile.adapter_id:<18}  {profile.domain_type:<10}  {applies}")


@adapter_group.command("show")
@click.option("--id", "adapter_id", required=True, help="Adapter ID to show.")
@click.pass_context
def adapter_show(ctx, adapter_id):
    """Show one adapter profile in detail."""
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    profiles = load_adapter_profiles(root)
    profile = next((item for item in profiles if item.adapter_id == adapter_id), None)
    if profile is None:
        raise click.UsageError(f"adapter '{adapter_id}' not found")

    payload = {
        "adapter_id": profile.adapter_id,
        "domain_type": profile.domain_type,
        "applies_to": profile.applies_to,
        "relevant_file_patterns": profile.relevant_file_patterns,
        "ignore_file_patterns": profile.ignore_file_patterns,
        "build_or_run_hints": profile.build_or_run_hints,
        "test_or_validation_hints": profile.test_or_validation_hints,
        "review_focus_hints": profile.review_focus_hints,
        "context_priority_rules": profile.context_priority_rules,
        "default_model_bias": profile.default_model_bias,
    }

    if fmt == "json":
        data = {
            "ok": True,
            "command": "adapter show",
            "repo": str(root),
            "adapter": payload,
            "source_path": "docs/runtime/adapter_profiles.md",
        }
        click.echo(json.dumps(data, indent=2))
        return

    click.echo("adapter show: ok")
    click.echo(f"  adapter_id        {profile.adapter_id}")
    click.echo(f"  domain_type       {profile.domain_type}")
    click.echo("  applies_to")
    for item in profile.applies_to:
        click.echo(f"    - {item}")
    click.echo("  relevant_file_patterns")
    for item in profile.relevant_file_patterns:
        click.echo(f"    - {item}")
    click.echo("  ignore_file_patterns")
    for item in profile.ignore_file_patterns:
        click.echo(f"    - {item}")
    click.echo("  build_or_run_hints")
    for item in profile.build_or_run_hints:
        click.echo(f"    - {item}")
    click.echo("  test_or_validation_hints")
    for item in profile.test_or_validation_hints:
        click.echo(f"    - {item}")
    click.echo("  review_focus_hints")
    for item in profile.review_focus_hints:
        click.echo(f"    - {item}")
    click.echo("  context_priority_rules")
    for item in profile.context_priority_rules:
        click.echo(f"    - {item}")
    click.echo("  default_model_bias")
    for item in profile.default_model_bias:
        click.echo(f"    - {item}")


@adapter_group.command("install")
@click.option("--source", type=click.Path(path_type=Path), default=None, help="Path to a validated adapter package directory.")
@click.option("--handle", default="", help="Registry package_id or adapter_id to install from a local reviewed-registry checkout.")
@click.option(
    "--registry-root",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to a local reviewed-registry checkout used with --handle.",
)
@click.pass_context
def adapter_install(ctx, source, handle, registry_root):
    """Install one explicit community adapter package into the repo."""
    from grain.services.adapter_install_service import install_adapter

    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    result, payload = install_adapter(
        root,
        source=source,
        handle=handle.strip(),
        registry_root=registry_root,
    )
    if payload is None:
        raise GeneralError("adapter install failed")
    if not result.ok:
        raise GeneralError("adapter install failed", detail="; ".join(result.errors))

    if fmt == "json":
        data = {
            "ok": True,
            "command": "adapter install",
            "repo": str(root),
            "source_kind": payload.source_kind,
            "source_ref": payload.source_ref,
            "package_id": payload.package_id,
            "adapter_id": payload.adapter_id,
            "installed_path": payload.installed_path,
        }
        click.echo(json.dumps(data, indent=2))
        return

    click.echo("adapter install: ok")
    click.echo(f"  source_kind       {payload.source_kind}")
    click.echo(f"  source_ref        {payload.source_ref}")
    click.echo(f"  package_id        {payload.package_id}")
    click.echo(f"  adapter_id        {payload.adapter_id}")
    for path in result.files_updated:
        click.echo(f"  updated   {path}")
