import pytest
from click.testing import CliRunner
from grain.cli import main

runner = CliRunner()

GROUPS = [
    "docs",
    "task",
    "adapter",
    "orchestrate",
    "context",
    "model",
    "review",
    "verify",
    "phase",
    "prompt",
    "workflow",
]

SUBCOMMANDS = {
    "docs": ["validate", "index", "show"],
    "task": ["create", "list", "show", "status", "validate", "close"],
    "adapter": ["list", "show"],
    "orchestrate": ["scope", "plan", "accept"],
    "context": ["build", "show", "export"],
    "model": ["show", "select", "escalate"],
    "review": ["check", "handoff", "summary"],
    "verify": ["submit", "status", "ingest"],
    "phase": ["next"],
    "prompt": ["show"],
    "workflow": ["next", "run", "explain", "loop"],
}


def test_init_help():
    result = runner.invoke(main, ["init", "--help"])
    assert result.exit_code == 0


def test_onboard_help():
    result = runner.invoke(main, ["onboard", "--help"])
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
