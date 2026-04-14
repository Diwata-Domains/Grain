"""CLI command for upgrading Grain-managed files to the current bundled versions."""

from __future__ import annotations

import json
from pathlib import Path

import click

from grain.services.upgrade_service import upgrade_repo


@click.command("upgrade")
@click.option("--dry-run", is_flag=True, default=False, help="Preview changes without writing.")
@click.option("--diff", "show_diff", is_flag=True, default=False, help="Show unified diffs for stale files without writing.")
@click.option("--interactive", "-i", is_flag=True, default=False, help="Review each stale file's diff and choose accept/skip.")
@click.option(
    "--format",
    "local_fmt",
    type=click.Choice(["text", "json"]),
    default=None,
    help="Output format override for this command.",
)
@click.pass_context
def upgrade_cmd(ctx, dry_run: bool, show_diff: bool, interactive: bool, local_fmt: str | None) -> None:
    """Update Grain-managed prompts and templates to the current installed version.

    Updates: prompts, task templates, safe runtime docs.

    Never touches: canonical docs, working docs, task packets,
    docs_manifest.yaml, adapter_profiles.md.

    \b
    Modes:
      grain upgrade                  Apply all changes
      grain upgrade --dry-run        List what would change
      grain upgrade --diff           Show unified diffs without writing
      grain upgrade --interactive    Review each file's diff, accept or skip
    """
    repo = ctx.obj.get("repo") if ctx.obj else None
    fmt = local_fmt or (ctx.obj.get("fmt", "text") if ctx.obj else "text")

    if repo:
        root = Path(repo).resolve()
    else:
        from grain.adapters.filesystem import resolve_repo_root
        root = resolve_repo_root(None)

    # --diff and --interactive both imply preview mode (no write unless user accepts)
    effective_dry_run = dry_run or show_diff
    need_diffs = show_diff or interactive

    result = upgrade_repo(root, dry_run=effective_dry_run, include_diffs=need_diffs)

    # --- interactive mode ---
    if interactive:
        _run_interactive(root, result)
        return

    # --- json output ---
    if fmt == "json":
        click.echo(
            json.dumps(
                {
                    "updated": result.updated,
                    "added": result.added,
                    "unchanged": result.unchanged,
                    "protected": result.protected,
                    "dry_run": dry_run or show_diff,
                    "diffs": result.diffs,
                },
                indent=2,
            )
        )
        return

    # --- text output ---
    if show_diff:
        status = "diff"
    elif dry_run:
        status = "dry-run"
    else:
        status = "ok"

    click.echo(f"upgrade: {status}")
    if dry_run:
        click.echo("  dry_run           true")

    if show_diff and result.diffs:
        click.echo("")
        for rel, diff_text in result.diffs.items():
            click.echo(f"--- {rel} ---")
            _print_diff(diff_text)
            click.echo("")
        click.echo(f"Run `grain upgrade` to apply all {len(result.updated)} change(s).")
        return

    click.echo("Updated:")
    for rel in result.updated:
        click.echo(f"- {rel}")
    if not result.updated:
        click.echo("- (none)")

    click.echo("Added:")
    for rel in result.added:
        click.echo(f"- {rel}")
    if not result.added:
        click.echo("- (none)")

    click.echo("Unchanged:")
    for rel in result.unchanged:
        click.echo(f"- {rel}")
    if not result.unchanged:
        click.echo("- (none)")

    click.echo("Protected (not touched):")
    for rel in result.protected:
        click.echo(f"- {rel}")


def _print_diff(diff_text: str) -> None:
    """Print a unified diff with optional ANSI colouring if the terminal supports it."""
    use_color = click.get_current_context(silent=True) is not None
    for line in diff_text.splitlines():
        if use_color and line.startswith("+") and not line.startswith("+++"):
            click.echo(click.style(line, fg="green"))
        elif use_color and line.startswith("-") and not line.startswith("---"):
            click.echo(click.style(line, fg="red"))
        elif line.startswith("@@"):
            click.echo(click.style(line, fg="cyan") if use_color else line)
        else:
            click.echo(line)


def _run_interactive(root: Path, preview: "UpgradeResult") -> None:
    """Walk stale files, show each diff, and ask the user to accept or skip."""
    from grain.services.upgrade_service import upgrade_repo as _upgrade_one

    if not preview.updated and not preview.added:
        click.echo("upgrade: nothing to do — all Grain-managed files are current.")
        return

    accepted: list[str] = []
    skipped: list[str] = []

    for rel in preview.updated:
        diff_text = preview.diffs.get(rel, "")
        click.echo(f"\n{'=' * 60}")
        click.echo(f"  {rel}  (stale)")
        click.echo(f"{'=' * 60}")
        if diff_text:
            _print_diff(diff_text)
        else:
            click.echo("  (diff unavailable)")

        choice = click.prompt(
            "\nAccept change?",
            type=click.Choice(["y", "n", "q"], case_sensitive=False),
            default="n",
            show_choices=True,
        )
        if choice == "q":
            click.echo("Aborted. No further files processed.")
            break
        if choice == "y":
            accepted.append(rel)

    for rel in preview.added:
        click.echo(f"\n{'=' * 60}")
        click.echo(f"  {rel}  (missing — will be created)")
        click.echo(f"{'=' * 60}")
        choice = click.prompt(
            "Accept addition?",
            type=click.Choice(["y", "n", "q"], case_sensitive=False),
            default="y",
            show_choices=True,
        )
        if choice == "q":
            click.echo("Aborted. No further files processed.")
            break
        if choice == "y":
            accepted.append(rel)
        else:
            skipped.append(rel)

    # Apply only accepted files
    if accepted:
        from grain.services.upgrade_service import _UPGRADE_TARGETS, _ADDITIVE_TARGETS, _SOURCE_ROOT
        for rel in accepted:
            source_rel = _UPGRADE_TARGETS.get(rel) or _ADDITIVE_TARGETS.get(rel)
            if not source_rel:
                continue
            source = _SOURCE_ROOT / source_rel
            if not source.exists():
                continue
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    click.echo(f"\nupgrade: done — applied {len(accepted)}, skipped {len(skipped)}.")
