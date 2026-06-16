# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""CLI command for upgrading Grain-managed files to the current bundled versions."""

from __future__ import annotations

import json
from pathlib import Path

import click

from grain.services.upgrade_service import UpgradeResult, upgrade_repo


@click.command("upgrade")
@click.option("--dry-run", is_flag=True, default=False, help="Preview changes without writing.")
@click.option("--diff", "show_diff", is_flag=True, default=False, help="Show unified diffs for stale files without writing.")
@click.option("--interactive", "-i", is_flag=True, default=False, help="Review each stale file's diff and choose accept/skip.")
@click.option("--add-missing", "add_missing", is_flag=True, default=False, help="Seed absent seeded files into the workspace; never overwrites existing files.")
@click.option(
    "--format",
    "local_fmt",
    type=click.Choice(["text", "json"]),
    default=None,
    help="Output format override for this command.",
)
@click.pass_context
def upgrade_cmd(ctx, dry_run: bool, show_diff: bool, interactive: bool, add_missing: bool, local_fmt: str | None) -> None:
    """Update Grain-managed prompts and templates to the current installed version.

    Updates: prompts, task templates, safe runtime docs.

    Never touches: canonical docs, working docs, task packets,
    docs_manifest.yaml, adapter_profiles.md.

    \b
    Modes:
      grain upgrade                  Apply all changes; report absent seeded files
      grain upgrade --dry-run        List what would change
      grain upgrade --diff           Show unified diffs without writing
      grain upgrade --interactive    Review each file's diff, accept or skip
      grain upgrade --add-missing    Seed absent files only; never overwrites
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

    # Always compute diffs so we can detect user-customized files even in plain mode.
    result = upgrade_repo(root, dry_run=effective_dry_run, include_diffs=True, add_missing=add_missing)

    # Ratchet upgrade_policy.min_version to the current installed version on real runs.
    if not effective_dry_run:
        try:
            from grain.services.upgrade_service import write_upgrade_policy_min_version
            from importlib.metadata import version as _pkg_version, PackageNotFoundError
            try:
                _v = _pkg_version("grain-kit")
            except PackageNotFoundError:
                import tomllib as _toml
                _pyproject = root.parent / "pyproject.toml"
                if not _pyproject.exists():
                    import pathlib
                    _pyproject = pathlib.Path(__file__).resolve().parents[4] / "pyproject.toml"
                with _pyproject.open("rb") as _f:
                    _v = _toml.load(_f)["project"]["version"]
            write_upgrade_policy_min_version(root, _v)
        except Exception:
            pass

    if not need_diffs:
        # Only expose diffs in output when explicitly requested.
        result.diffs = {}

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
                    "absent": result.absent,
                    "protected": result.protected,
                    "customized": result.customized,
                    "skipped_customized": result.skipped_customized,
                    "dry_run": dry_run or show_diff,
                    "add_missing": add_missing,
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

    if result.skipped_customized and not dry_run:
        click.echo(
            f"warning   {len(result.skipped_customized)} Grain-managed file(s) appear to have been "
            "locally customized and were skipped:",
            err=True,
        )
        for rel in result.skipped_customized:
            click.echo(f"  - {rel}", err=True)
        click.echo(
            "  Run `grain upgrade --interactive` to review and apply selected changes, "
            "or `grain upgrade --diff` to preview them.",
            err=True,
        )

    click.echo("Updated:")
    for rel in result.updated:
        marker = " (customized)" if rel in result.customized else ""
        click.echo(f"- {rel}{marker}")
    if not result.updated:
        click.echo("- (none)")

    if result.skipped_customized:
        click.echo("Skipped Customized:")
        for rel in result.skipped_customized:
            click.echo(f"- {rel}")

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

    if result.absent:
        click.echo(f"\n{len(result.absent)} seeded file(s) absent from workspace:")
        for rel in result.absent:
            click.echo(f"  +  {rel}  (not present)")
        if not add_missing:
            click.echo("  Run `grain upgrade --add-missing` to seed them.")


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
