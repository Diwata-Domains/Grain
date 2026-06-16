# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Domain models for existing-project onboarding scaffold."""

from dataclasses import dataclass, field


@dataclass
class ScaffoldManifest:
    """Scaffold results for onboard command."""

    created: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    root: str = ""
    agents_md_action: str = ""   # "created" | "updated" | "appended" | "skipped"
    claude_md_exists: bool = False
