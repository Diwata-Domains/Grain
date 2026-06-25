# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""grain report — file friction notes upstream via a pre-filled GitHub issue URL.

The canonical, browser-confirmed, token-free path from ``feedback_spec.md``.
Scans ``docs/working/tooling_notes.md`` for open Grain-related rows, builds a
privacy-preserving pre-filled issue URL (no file contents, paths, or PII), opens
it in the browser (or prints it with ``--no-browser``), and marks the row
``reported``. Nothing is sent automatically — GitHub renders the form and the
user submits.
"""

from __future__ import annotations

import json
import platform

import click

from grain.adapters.filesystem import resolve_repo_root

# Heuristic: a note is "Grain-related" when its type signals a tool issue or its
# command/observation references the grain CLI.
_GRAIN_TYPES = frozenset({"bug", "friction", "ux", "missing-command"})


def _is_grain_related(note) -> bool:
    if note.type in _GRAIN_TYPES:
        return True
    haystack = f"{note.command} {note.body}".lower()
    return "grain" in haystack


@click.command("report")
@click.option("--id", "note_id", default=None, type=int, metavar="ID",
              help="Report a specific note by ID (otherwise lists candidates).")
@click.option("--all", "show_all", is_flag=True, default=False,
              help="Include all open notes, not just Grain-related ones.")
@click.option("--no-browser", is_flag=True, default=False,
              help="Print the issue URL instead of opening a browser.")
@click.pass_context
def report_cmd(ctx, note_id, show_all, no_browser):
    """Report open Grain-related tooling notes as pre-filled GitHub issues.

    \b
    Examples:
      grain report                 List open Grain-related notes to report
      grain report --all           Include non-Grain open notes
      grain report --id 3          Build the issue URL for note 3 and open it
      grain report --id 3 --no-browser
      grain report --format json
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = ctx.obj.get("fmt", "text") if ctx.obj else "text"
    root = resolve_repo_root(repo)

    from grain.adapters.manifest import load_github_config
    from grain.services.github_service import build_issue_url
    from grain.services.notes_service import list_notes, set_note_status

    gh = load_github_config(root)
    grain_version = _grain_version()
    os_platform = platform.system().lower()
    install_mode = _install_mode()

    open_notes = list_notes(root, status_filter="open").notes
    candidates = open_notes if show_all else [n for n in open_notes if _is_grain_related(n)]

    # ── Single-note report path: build URL, open/print, mark reported. ──────────
    if note_id is not None:
        target = next((n for n in open_notes if n.id == note_id), None)
        if target is None:
            if fmt == "json":
                click.echo(json.dumps(
                    {"ok": False, "errors": [f"note {note_id} not found or not open"]},
                    indent=2,
                ))
                return
            click.echo(f"error  note {note_id} not found or not open", err=True)
            raise click.UsageError(f"note not found: {note_id}")

        url_result = build_issue_url(
            target.type,
            target.command,
            target.body,
            repo=gh.report_repo,
            severity=target.severity,
            grain_version=grain_version,
            os_platform=os_platform,
            install_mode=install_mode,
        )

        opened = False
        if url_result.ok and not no_browser and fmt != "json":
            try:
                click.launch(url_result.url)
                opened = True
            except Exception:
                opened = False

        marked = False
        if url_result.ok:
            status_result = set_note_status(root, note_id, "reported")
            marked = status_result.ok

        if fmt == "json":
            click.echo(json.dumps({
                "ok": url_result.ok,
                "id": note_id,
                "url": url_result.url,
                "title": url_result.title,
                "labels": url_result.labels,
                "reported": marked,
                "errors": url_result.errors,
            }, indent=2))
            return

        if not url_result.ok:
            for e in url_result.errors:
                click.echo(f"error  {e}", err=True)
            raise click.ClickException("report failed")

        click.echo(f"report: note #{note_id} reported")
        if opened:
            click.echo("  opened in browser")
        else:
            click.echo(f"  url    {url_result.url}")
        if marked:
            click.echo("  status reported")
        return

    # ── Listing path: show candidates; user picks an --id to report. ────────────
    if fmt == "json":
        click.echo(json.dumps([
            {
                "id": n.id,
                "type": n.type,
                "severity": n.severity,
                "command": n.command,
                "observation": n.body,
                "url": build_issue_url(
                    n.type, n.command, n.body,
                    repo=gh.report_repo, severity=n.severity,
                    grain_version=grain_version, os_platform=os_platform,
                    install_mode=install_mode,
                ).url,
            }
            for n in candidates
        ], indent=2))
        return

    if not candidates:
        click.echo("report: no open Grain-related notes to report")
        return

    scope = "open" if show_all else "open Grain-related"
    click.echo(f"report: {len(candidates)} {scope} note(s)")
    for n in candidates:
        sev_marker = {"high": "✗", "medium": "⚠", "low": "·"}.get(n.severity, "·")
        click.echo(f"  {sev_marker}  #{n.id:<4} [{n.type:<13}] {n.body}")
    click.echo("  → report one with: grain report --id <ID>")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _grain_version() -> str:
    try:
        from importlib.metadata import version
        return version("grain-kit")
    except Exception:
        return ""


def _install_mode() -> str:
    try:
        from grain.services.doctor_service import detect_install_mode
        return detect_install_mode()
    except Exception:
        return "unknown"
