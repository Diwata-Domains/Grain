# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

import json

import click

from grain.adapters.filesystem import resolve_repo_root
from grain.cli.output import print_result
from grain.domain.errors import ValidationError
from grain.services import docs_service


@click.group("docs")
def docs_group():
    """Inspect and validate repository documentation state."""


@docs_group.command("audit")
@click.option("--doc", default=None, help="Run checks only for this doc (e.g. current_task, backlog, structural).")
@click.option("--severity", default=None, type=click.Choice(["high", "medium"]), help="Filter by minimum severity (high=errors only, medium=warnings+errors).")
@click.option("--fix", is_flag=True, default=False, help="Apply safe auto-fixes (prompts per finding).")
@click.option("--no-confirm", is_flag=True, default=False, help="Apply fixes without prompting (agent use only). Requires --fix.")
@click.pass_context
def docs_audit(ctx, doc, severity, fix, no_confirm):
    """Run a broad workspace health check across all registered working documents.

    \b
    Examples:
      grain docs audit
      grain docs audit --doc current_task
      grain docs audit --severity high
      grain docs audit --format json
      grain docs audit --fix
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    from grain.services.docs_audit_service import run_audit, save_audit_cache, apply_fixes

    result = run_audit(root, doc_filter=doc, severity_filter=severity)
    save_audit_cache(root, result)

    if fmt == "json":
        click.echo(json.dumps({
            "run_at": result.run_at,
            "summary": result.summary,
            "overall": result.overall,
            "findings": [
                {
                    "doc": f.doc,
                    "check_id": f.check_id,
                    "severity": f.severity,
                    "message": f.message,
                    "remediation": f.remediation,
                }
                for f in result.findings
                if f.severity != "pass"
            ],
        }, indent=2))
        return

    # --- text output ---
    run_date = result.run_at[:10]
    click.echo(f"grain docs audit — {run_date}")
    click.echo("")

    # Group by doc
    docs_seen: list[str] = []
    findings_by_doc: dict[str, list] = {}
    for f in result.findings:
        if f.doc not in findings_by_doc:
            docs_seen.append(f.doc)
            findings_by_doc[f.doc] = []
        findings_by_doc[f.doc].append(f)

    for doc_key in docs_seen:
        doc_findings = findings_by_doc[doc_key]
        click.echo(doc_key)
        for f in doc_findings:
            if f.severity == "pass":
                symbol = click.style("  ✓", fg="green") if _color_ok() else "  ✓"
                click.echo(f"{symbol}  {f.check_id:<40} {f.message}")
            elif f.severity == "warning":
                symbol = click.style("  ⚠", fg="yellow") if _color_ok() else "  ⚠"
                click.echo(f"{symbol}  {f.check_id:<40} {f.message}")
                if f.remediation:
                    click.echo(f"     → {f.remediation}")
            elif f.severity == "error":
                symbol = click.style("  ✗", fg="red") if _color_ok() else "  ✗"
                click.echo(f"{symbol}  {f.check_id:<40} {f.message}")
                if f.remediation:
                    click.echo(f"     → {f.remediation}")
        click.echo("")

    s = result.summary
    status_color = {"ok": "green", "warning": "yellow", "error": "red"}.get(result.overall, "white")
    status_label = click.style(result.overall, fg=status_color) if _color_ok() else result.overall
    click.echo(
        f"Checks: {s['pass']} pass, {s['warning']} warning(s), {s['error']} error(s) — {status_label}"
    )

    if fix:
        non_pass = [f for f in result.findings if f.severity != "pass"]
        if non_pass:
            applied = apply_fixes(root, result, confirm=not no_confirm)
            if applied:
                click.echo("\nFixes applied:")
                for desc in applied:
                    click.echo(f"  - {desc}")
            else:
                click.echo("\nNo fixes applied.")


def _color_ok() -> bool:
    ctx = click.get_current_context(silent=True)
    return ctx is not None


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
