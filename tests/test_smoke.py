"""Subprocess-level smoke tests for the installed `forge` entrypoint.

These tests invoke `forge` as a real process to verify the full stack —
entrypoint registration, group loading, version, and exit codes.
"""
import subprocess
import sys
from pathlib import Path

# Resolve the forge executable from the same environment running pytest
_ABT = str(Path(sys.executable).parent / "forge")

GROUPS = ["init", "docs", "task", "context", "model", "review"]


def _run(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [_ABT, *args],
        capture_output=True,
        text=True,
    )


def test_help_exits_zero():
    result = _run("--help")
    assert result.returncode == 0


def test_help_lists_all_groups():
    result = _run("--help")
    for group in GROUPS:
        assert group in result.stdout, f"'{group}' missing from forge --help"


def test_version_exits_zero():
    result = _run("--version")
    assert result.returncode == 0


def test_version_output_contains_version_string():
    result = _run("--version")
    # Should contain a semver-like string (e.g. "0.1.0")
    assert any(char.isdigit() for char in result.stdout)


def test_unknown_command_exits_two():
    result = _run("unknown-command")
    assert result.returncode == 2


def test_docs_help_exits_zero():
    result = _run("docs", "--help")
    assert result.returncode == 0


def test_task_help_exits_zero():
    result = _run("task", "--help")
    assert result.returncode == 0
