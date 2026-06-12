import sys
import tomllib
import click
from importlib.metadata import version, PackageNotFoundError

try:
    _VERSION = version("grain-kit")
except PackageNotFoundError:
    try:
        with open("pyproject.toml", "rb") as f:
            _VERSION = tomllib.load(f)["project"]["version"]
    except Exception:
        _VERSION = "unknown"

from .init import init_cmd
from .docs import docs_group
from .task import task_group
from .verify import verify_group
from .adapter import adapter_group
from .context import context_group
from .embedding import embedding_group
from .model import model_group
from .mcp import mcp_group
from .phase import phase_group
from .prompt import prompt_group
from .orchestrate import orchestrate_group
from .review import review_group
from .office import office_group
from .tui import tui_cmd
from .hooks import hooks_group
from .workflow import workflow_group
from .onboard import onboard_cmd
from .upgrade import upgrade_cmd
from .error_handler import handle_error
from grain.domain.errors import ForgeError
from grain.adapters.manifest import load_manifest, load_grain_config
from grain.adapters.filesystem import resolve_repo_root


def _parse_semver(raw: str) -> tuple[int, int, int] | None:
    parts = raw.strip().split(".")
    if len(parts) < 3:
        return None

    values: list[int] = []
    for part in parts[:3]:
        digits = []
        for ch in part:
            if ch.isdigit():
                digits.append(ch)
            else:
                break
        if not digits:
            return None
        values.append(int("".join(digits)))
    return tuple(values)  # type: ignore[return-value]


def _maybe_warn_if_grain_outdated(repo: str | None, invoked_subcommand: str | None) -> None:
    if not invoked_subcommand or _VERSION == "unknown":
        return

    try:
        root = resolve_repo_root(repo)
    except FileNotFoundError:
        return

    manifest_path = root / "docs" / "runtime" / "docs_manifest.yaml"
    if not manifest_path.exists():
        return

    try:
        manifest = load_manifest(root)
    except Exception:
        return

    project = manifest.get("project")
    if not isinstance(project, dict):
        return

    required = project.get("minimum_grain_version", "")
    if not isinstance(required, str) or not required.strip():
        return

    current_version = _parse_semver(_VERSION)
    required_version = _parse_semver(required)
    if current_version is None or required_version is None:
        return

    if current_version >= required_version:
        return

    click.echo(
        (
            f"warning   repo requires Grain >= {required}; installed {_VERSION}. "
            "Update first with `uv tool upgrade grain-kit` "
            "or `pip install --upgrade grain-kit`."
        ),
        err=True,
    )


def _maybe_warn_if_upgrade_needed(root_path, invoked_subcommand: str | None) -> None:
    """If grain.upgrade_check = warn in docs_manifest.yaml, surface a hint when stale files exist."""
    if invoked_subcommand in {"upgrade", "onboard"}:
        return  # onboard seeds managed files itself; warning before it runs is noise

    try:
        cfg = load_grain_config(root_path)
    except Exception:
        return

    if cfg.upgrade_check != "warn":
        return

    try:
        from grain.services.upgrade_service import upgrade_repo
        result = upgrade_repo(root_path, dry_run=True)
        stale = len(result.updated) + len(result.added)
        if stale > 0:
            click.echo(
                f"hint   {stale} Grain-managed file(s) are out of date. "
                "Run `grain upgrade --diff` to review or `grain upgrade` to apply.",
                err=True,
            )
    except Exception:
        return


@click.group()
@click.version_option(_VERSION, "--version", "-V")
@click.option("--repo", default=None, metavar="PATH", help="Path to repository root (auto-detected if omitted).")
@click.option(
    "--format",
    "fmt",
    default=None,
    show_default=False,
    type=click.Choice(["text", "json"]),
    help="Output format for command results (default: from docs_manifest.yaml grain.default_format or 'text').",
)
@click.pass_context
def main(ctx, repo, fmt):
    """Grain — CLI workflow orchestrator for AI-assisted development."""
    ctx.ensure_object(dict)
    ctx.obj["repo"] = repo

    # Resolve effective format: CLI flag > grain config > hardcoded default
    if fmt is None:
        try:
            root = resolve_repo_root(repo)
            cfg = load_grain_config(root)
            fmt = cfg.default_format
        except Exception:
            fmt = "text"

    ctx.obj["fmt"] = fmt
    _maybe_warn_if_grain_outdated(repo, ctx.invoked_subcommand)

    # Upgrade staleness hint (only when upgrade_check = warn in grain config)
    try:
        root = resolve_repo_root(repo)
        _maybe_warn_if_upgrade_needed(root, ctx.invoked_subcommand)
    except Exception:
        pass


@main.result_callback()
def _on_result(*args, **kwargs):
    pass


def cli():
    """Entrypoint wrapper that catches ForgeError and exits with the correct code."""
    try:
        main(standalone_mode=False)
    except ForgeError as exc:
        code = handle_error(exc)
        sys.exit(code)
    except click.UsageError as exc:
        click.echo(f"Error: {exc.format_message()}", err=True)
        sys.exit(2)
    except click.ClickException as exc:
        exc.show()
        sys.exit(exc.exit_code)
    except SystemExit:
        raise
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


main.add_command(init_cmd)
main.add_command(docs_group)
main.add_command(task_group)
main.add_command(verify_group)
main.add_command(adapter_group)
main.add_command(context_group)
main.add_command(embedding_group)
main.add_command(model_group)
main.add_command(mcp_group)
main.add_command(phase_group)
main.add_command(prompt_group)
main.add_command(orchestrate_group)
main.add_command(review_group)
main.add_command(office_group)
main.add_command(tui_cmd)
main.add_command(hooks_group)
main.add_command(workflow_group)
main.add_command(onboard_cmd)
main.add_command(upgrade_cmd)
