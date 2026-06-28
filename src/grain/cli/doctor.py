# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""grain doctor — install/source alignment diagnostics."""

from __future__ import annotations

import json

import click

from grain.adapters.filesystem import resolve_repo_root


@click.command("doctor")
@click.pass_context
def doctor_cmd(ctx):
    """Show install mode, version alignment, and workspace diagnostics.

    \b
    Examples:
      grain doctor
      grain doctor --format json
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = None
    try:
        root = resolve_repo_root(repo)
    except Exception:
        pass

    from grain.services.doctor_service import run_doctor
    result = run_doctor(root)

    if fmt == "json":
        click.echo(json.dumps({
            "grain_version": result.grain_version,
            "install_mode": result.install_mode,
            "install_path": result.install_path,
            "source_path": result.source_path,
            "pyproject_version": result.pyproject_version,
            "version_match": result.version_match,
            "source_mtime": result.source_mtime,
            "install_mtime": result.install_mtime,
            "source_files_modified_since_install": result.source_files_modified_since_install,
            "workspace_root": result.workspace_root,
            "python_version": result.python_version,
            "checks": result.checks,
            "overall": result.overall,
        }, indent=2))
        return

    ok_sym = "✓"
    fail_sym = "✗"

    click.echo(f"Grain Doctor — {_today()}")
    click.echo("")

    click.echo("Install:")
    click.echo(f"  {'version':<18} {result.grain_version}")
    click.echo(f"  {'install mode':<18} {result.install_mode}")
    if result.install_path:
        click.echo(f"  {'install path':<18} {result.install_path}")
    if result.source_path:
        click.echo(f"  {'source path':<18} {result.source_path}")
    click.echo("")

    click.echo("Alignment:")
    ver_sym = ok_sym if result.version_match else fail_sym
    click.echo(f"  {'pyproject.toml':<18} {result.pyproject_version or '(not found)'}  {ver_sym}")
    if not result.version_match:
        click.echo(f"  → source version ({result.pyproject_version}) differs from installed ({result.grain_version})")
        click.echo("  → Run: uv run grain  (or pip install -e . to reinstall from source)")

    if result.source_mtime:
        mtime_sym = ok_sym if result.checks.get("mtime_ok") else fail_sym
        click.echo(f"  {'source mtime':<18} {result.source_mtime[:16]}  {mtime_sym}")
        if result.source_files_modified_since_install:
            click.echo(f"  {'install mtime':<18} {result.install_mtime[:16]}")
            click.echo(f"  {len(result.source_files_modified_since_install)} file(s) modified since install:")
            for f in result.source_files_modified_since_install:
                click.echo(f"    {f}")
            click.echo("  → Run: pip install -e . to reinstall from source")
    click.echo("")

    click.echo("Workspace:")
    ws_sym = ok_sym if result.workspace_root else fail_sym
    click.echo(f"  {'root':<18} {result.workspace_root or '(unresolved)'}  {ws_sym}")
    click.echo("")

    click.echo("Python:")
    click.echo(f"  {'version':<18} {result.python_version}")
    click.echo(f"  {'executable':<18} {_python_executable()}")
    click.echo("")

    passed = sum(1 for v in result.checks.values() if v)
    total = len(result.checks)
    overall_sym = ok_sym if result.overall == "ok" else fail_sym
    click.echo(f"Checks: {passed}/{total} pass  {overall_sym}")


def _today() -> str:
    from datetime import date
    return date.today().isoformat()


def _python_executable() -> str:
    import sys
    return sys.executable
