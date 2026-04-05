import pytest
from click.testing import CliRunner
from forge.cli import main

runner = CliRunner()

GROUPS = ["docs", "task", "context", "model", "review"]

SUBCOMMANDS = {
    "docs": ["validate", "index", "show"],
    "task": ["create", "list", "show", "status", "validate", "close"],
    "context": ["build", "show", "export"],
    "model": ["show", "select", "escalate"],
    "review": ["check", "handoff", "summary"],
}


def test_init_help():
    result = runner.invoke(main, ["init", "--help"])
    assert result.exit_code == 0


@pytest.mark.parametrize("group", GROUPS)
def test_group_help(group):
    result = runner.invoke(main, [group, "--help"])
    assert result.exit_code == 0


@pytest.mark.parametrize("group,subcommand", [
    (group, sub)
    for group, subs in SUBCOMMANDS.items()
    for sub in subs
])
def test_subcommand_help(group, subcommand):
    result = runner.invoke(main, [group, subcommand, "--help"])
    assert result.exit_code == 0
