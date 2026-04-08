import sys
import click
from importlib.metadata import version, PackageNotFoundError

try:
    _VERSION = version("forge")
except PackageNotFoundError:
    _VERSION = "unknown"

from .init import init_cmd
from .docs import docs_group
from .task import task_group
from .context import context_group
from .model import model_group
from .phase import phase_group
from .prompt import prompt_group
from .review import review_group
from .workflow import workflow_group
from .error_handler import handle_error
from forge.domain.errors import ForgeError


@click.group()
@click.version_option(_VERSION, "--version", "-V")
@click.option("--repo", default=None, metavar="PATH", help="Path to repository root (auto-detected if omitted).")
@click.option(
    "--format",
    "fmt",
    default="text",
    show_default=True,
    type=click.Choice(["text", "json"]),
    help="Output format for command results.",
)
@click.pass_context
def main(ctx, repo, fmt):
    """Forge — CLI workflow orchestrator for AI-assisted development."""
    ctx.ensure_object(dict)
    ctx.obj["repo"] = repo
    ctx.obj["fmt"] = fmt


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
main.add_command(context_group)
main.add_command(model_group)
main.add_command(phase_group)
main.add_command(prompt_group)
main.add_command(review_group)
main.add_command(workflow_group)
