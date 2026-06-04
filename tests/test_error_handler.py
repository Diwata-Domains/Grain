import pytest
from grain.cli.error_handler import EXIT_CODES, handle_error
from grain.domain.errors import (
    GeneralError,
    UsageError,
    ValidationError,
    MissingPathError,
    InvalidTransitionError,
    ConfigError,
    AdapterError,
)


# --- Exit code mapping ---

@pytest.mark.parametrize("exc_class,expected_code", [
    (GeneralError, 1),
    (UsageError, 2),
    (ValidationError, 3),
    (MissingPathError, 4),
    (InvalidTransitionError, 5),
    (ConfigError, 6),
    (AdapterError, 7),
])
def test_exit_code_mapping(exc_class, expected_code):
    assert EXIT_CODES[exc_class] == expected_code


# --- handle_error output ---

def test_handle_error_returns_correct_code():
    exc = ValidationError("manifest is invalid")
    code = handle_error(exc)
    assert code == 3


def test_handle_error_includes_detail(capsys):
    exc = MissingPathError("file not found", detail="docs/canonical/architecture.md")
    handle_error(exc)
    captured = capsys.readouterr()
    assert "file not found" in captured.err
    assert "docs/canonical/architecture.md" in captured.err


def test_handle_error_without_detail(capsys):
    exc = GeneralError("something went wrong")
    code = handle_error(exc)
    captured = capsys.readouterr()
    assert "something went wrong" in captured.err
    assert code == 1


# --- All seven codes present ---

def test_all_seven_exit_codes_defined():
    assert len(EXIT_CODES) == 7
    assert set(EXIT_CODES.values()) == {1, 2, 3, 4, 5, 6, 7}
