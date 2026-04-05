import json
import click
from click.testing import CliRunner
from forge.cli.output import CommandResult, print_result
from forge.cli import main

runner = CliRunner()


def test_text_output_contains_command():
    result = CommandResult(ok=True, command="init", files_created=["docs/canonical"])

    @click.command()
    def cmd():
        print_result(result, fmt="text")

    r = runner.invoke(cmd)
    assert r.exit_code == 0
    assert "init: ok" in r.output
    assert "created" in r.output
    assert "docs/canonical" in r.output


def test_json_output_is_valid():
    result = CommandResult(ok=True, command="init", files_created=["docs/canonical"])

    @click.command()
    def cmd():
        print_result(result, fmt="json")

    r = runner.invoke(cmd)
    data = json.loads(r.output)
    assert data["ok"] is True
    assert data["command"] == "init"
    assert "docs/canonical" in data["files_created"]


def test_empty_result_prints_cleanly():
    result = CommandResult()

    @click.command()
    def cmd():
        print_result(result, fmt="text")

    r = runner.invoke(cmd)
    assert r.exit_code == 0


def test_init_format_json(tmp_path):
    result = runner.invoke(main, ["--repo", str(tmp_path), "--format", "json", "init"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["command"] == "init"
    assert isinstance(data["files_created"], list)
