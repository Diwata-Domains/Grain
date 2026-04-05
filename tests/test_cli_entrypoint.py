from click.testing import CliRunner
from forge.cli import main


def test_help_exits_zero():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Forge" in result.output


def test_unknown_group_exits_two():
    runner = CliRunner()
    result = runner.invoke(main, ["unknown-group"])
    assert result.exit_code == 2
