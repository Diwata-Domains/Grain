# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""CommandResult — the shared, CLI-agnostic result payload returned by services.

Lives in the domain layer (no click, no CLI imports) so services can import it
without pulling in the whole ``grain.cli`` package. ``grain.cli.output`` re-exports
it for backwards compatibility and adds the click-based ``print_result`` renderer.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CommandResult:
    ok: bool = True
    command: str = ""
    repo: str = ""
    task_id: str = ""
    status: str = ""
    files_created: list[str] = field(default_factory=list)
    files_updated: list[str] = field(default_factory=list)
    files_skipped: list[str] = field(default_factory=list)
    files_blocked: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    primary_adapter: str = ""
    secondary_adapters: list[str] = field(default_factory=list)
    bootstrapped_task_id: str = ""
