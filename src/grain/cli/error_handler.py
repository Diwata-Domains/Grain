# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""CLI error handling and exit code mapping.

Maps domain exception types to exit codes defined in cli_spec.md Section 5.
"""
import click

from grain.domain.errors import (
    GeneralError,
    UsageError,
    ValidationError,
    MissingPathError,
    InvalidTransitionError,
    ConfigError,
    AdapterError,
    ForgeError,
)

EXIT_CODES: dict[type, int] = {
    GeneralError: 1,
    UsageError: 2,
    ValidationError: 3,
    MissingPathError: 4,
    InvalidTransitionError: 5,
    ConfigError: 6,
    AdapterError: 7,
}


def handle_error(exc: ForgeError) -> int:
    """Print the error message and return the appropriate exit code.

    Error output states what failed, per cli_spec.md Section 4.6.
    """
    code = EXIT_CODES.get(type(exc), 1)
    msg = f"Error: {exc.message}"
    if exc.detail:
        msg += f"\n  {exc.detail}"
    click.echo(msg, err=True)
    return code
