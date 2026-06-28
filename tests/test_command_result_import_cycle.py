# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""Regression: the cli<->services import cycle that suggest accept pick-up relied on.

CommandResult now lives in grain.domain.command_result so services can import it
without triggering the grain.cli package __init__ (which imports the TUI, which
imports workflow_run_service). Previously workflow_run_service could not be
imported first; suggest_service._accept_pickup carried a fragile
`import grain.cli.output` workaround to force the package init ordering.
"""

from __future__ import annotations

import subprocess
import sys


def _import_first(module: str) -> subprocess.CompletedProcess:
    """Import `module` as the very first grain import in a clean interpreter."""
    code = f"import {module}; print('ok')"
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )


def test_workflow_run_service_imports_first_without_cycle():
    res = _import_first("grain.services.workflow_run_service")
    assert res.returncode == 0, res.stderr
    assert "ok" in res.stdout


def test_suggest_service_imports_first_without_cycle():
    res = _import_first("grain.services.suggest_service")
    assert res.returncode == 0, res.stderr
    assert "ok" in res.stdout


def test_command_result_reexport_is_same_object():
    from grain.cli.output import CommandResult as FromCli
    from grain.domain.command_result import CommandResult as FromDomain

    assert FromCli is FromDomain
