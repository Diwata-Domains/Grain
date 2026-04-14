"""Tests for CLI help ergonomics and default visibility."""

from click.testing import CliRunner

from grain.cli import main


def test_main_help_shows_format_option():
    result = CliRunner().invoke(main, ["--help"])
    assert result.exit_code == 0, result.output
    assert "--format [text|json]" in result.output
    # default is resolved from grain config; help text describes the fallback chain
    assert "grain.default_format" in result.output


def test_task_validate_help_mentions_default_behavior():
    result = CliRunner().invoke(main, ["task", "validate", "--help"])
    assert result.exit_code == 0, result.output
    assert "default behavior when no selector is" in result.output
    assert "provided" in result.output


def test_model_select_help_mentions_stage_role_requirement():
    result = CliRunner().invoke(main, ["model", "select", "--help"])
    assert result.exit_code == 0, result.output
    assert "At least one of --stage or --role is" in result.output
    assert "required" in result.output


def test_context_and_review_output_help_use_path_metavar():
    context_help = CliRunner().invoke(main, ["context", "export", "--help"])
    assert context_help.exit_code == 0, context_help.output
    assert "--output PATH" in context_help.output

    review_help = CliRunner().invoke(main, ["review", "handoff", "--help"])
    assert review_help.exit_code == 0, review_help.output
    assert "--output PATH" in review_help.output
