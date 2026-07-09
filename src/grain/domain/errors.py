# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Domain-level error types for Forge.

Exit codes are defined in cli_spec.md Section 5. Each exception class maps
to exactly one exit code. The CLI layer is responsible for the mapping.
"""


class ForgeError(Exception):
    """Base exception for all Forge errors."""

    def __init__(self, message: str, detail: str = ""):
        self.message = message
        self.detail = detail
        super().__init__(message)


class GeneralError(ForgeError):
    """General command failure. Exit code 1."""


class UsageError(ForgeError):
    """Invalid arguments or usage. Exit code 2."""


class ValidationError(ForgeError):
    """Validation failure. Exit code 3."""


class MissingPathError(ForgeError):
    """Missing required file or path. Exit code 4."""


class InvalidTransitionError(ForgeError):
    """State transition not allowed. Exit code 5."""


class ConfigError(ForgeError):
    """Configuration or manifest error. Exit code 6."""


class AdapterError(ForgeError):
    """External adapter or integration error. Exit code 7."""
