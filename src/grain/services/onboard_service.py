# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Additive scaffold service for existing-project onboarding."""

from __future__ import annotations

from pathlib import Path

from grain.domain.onboard import ScaffoldManifest
from grain.domain.scaffold import (
    PROMPT_SEED_SOURCES,
    REQUIRED_DIRS as _REQUIRED_DIRS,
    RUNTIME_SEED_SOURCES,
)

_STUB_FILES: dict[str, str] = {
    "docs/canonical/product_scope.md": "# Product Scope\n\n# DRAFT - replace with real content\n",
    "docs/canonical/architecture.md": "# Architecture\n\n# DRAFT - replace with real content\n",
    "docs/canonical/decisions.md": "# Decisions\n\n# DRAFT - replace with real content\n",
    "docs/canonical/landscape.md": "# Landscape\n\n# DRAFT - replace with real content\n",
    "docs/working/backlog.md": "# Backlog\n\n# DRAFT - replace with real content\n",
    "docs/working/roadmap.md": "# Roadmap\n\n# DRAFT - replace with real content\n",
    "docs/working/landscape.md": "# Landscape\n\n# DRAFT - replace with real content\n",
    # current_focus.md uses a parse-safe bootstrap marker so `grain workflow next`
    # returns a structured bootstrap_incomplete state instead of a hard parse error.
    "docs/working/current_focus.md": (
        "# Current Focus\n\n"
        "Phase 0 — Bootstrap\n\n"
        "# DRAFT - run the onboarding prompt to replace with project-specific content\n"
    ),
    # current_task.md requires Task ID / Task Path / Status fields for workflow parsing.
    "docs/working/current_task.md": (
        "# Current Task\n\n"
        "Task ID: none\n"
        "Task Path: none\n"
        "Status: unset\n"
    ),
    "docs/working/open_questions.md": "# Open Questions\n\n# DRAFT - replace with real content\n",
    "docs/working/change_proposals.md": "# Change Proposals\n\n# DRAFT - replace with real content\n",
    "docs/working/implementation_plan.md": "# Implementation Plan\n\n# DRAFT - replace with real content\n",
    # workflow_metrics.md is required by docs_manifest.yaml; must exist for docs validate to pass.
    "docs/working/workflow_metrics.md": "# Workflow Metrics\n\n# DRAFT - replace with project metrics\n",
    # tooling_notes.md: lightweight inbox for workflow friction and tool observations.
    # Agents write here mid-session; user reviews and escalates upstream as needed.
    # Type: bug | friction | question | note
    # Status: open | addressed | wontfix | escalated
    "docs/working/tooling_notes.md": (
        "# Tooling Notes\n\n"
        "Lightweight inbox for workflow friction, tool bugs, or observations noticed mid-session.\n"
        "Agents write here; user reviews and escalates to the appropriate tracker.\n\n"
        "| Date | Type | Command | Observation | Severity | Status |\n"
        "|------|------|---------|-------------|----------|--------|\n"
    ),
}

# Bundled runtime and prompt files seeded additively — mirrors init_service seeding.
# Keys: destination path relative to project root.
# Values: source path relative to the bundled data root.
_BUNDLED_DATA_ROOT = Path(__file__).resolve().parents[1] / "data"
_SOURCE_REPO_ROOT = (
    _BUNDLED_DATA_ROOT
    if _BUNDLED_DATA_ROOT.exists()
    else Path(__file__).resolve().parents[3]
)

# Runtime + prompt seed maps are shared with init via grain.domain.scaffold.
# The canonical/working docs are written as DRAFT stubs above rather than seeded here.
_SEED_FILE_SOURCES: dict[str, str] = {
    **RUNTIME_SEED_SOURCES,
    **PROMPT_SEED_SOURCES,
}


class OnboardService:
    """Scaffold Grain structure into an existing repo additively."""

    def __init__(self, root: Path):
        self.root = root

    def scaffold(self, dry_run: bool = False) -> ScaffoldManifest:
        manifest = ScaffoldManifest(root=str(self.root.resolve()))

        for rel in _REQUIRED_DIRS:
            target = self.root / rel
            if target.exists():
                manifest.skipped.append(rel)
                continue
            manifest.created.append(rel)
            if not dry_run:
                target.mkdir(parents=True, exist_ok=True)

        for rel, content in _STUB_FILES.items():
            target = self.root / rel
            if target.exists():
                manifest.skipped.append(rel)
                continue
            manifest.created.append(rel)
            if not dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")

        for rel, source_rel in _SEED_FILE_SOURCES.items():
            target = self.root / rel
            if target.exists():
                manifest.skipped.append(rel)
                continue
            source = _SOURCE_REPO_ROOT / source_rel
            if not source.exists():
                manifest.skipped.append(rel)
                continue
            manifest.created.append(rel)
            if not dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

        from grain.services.agents_md_service import write_agents_md
        agents_result = write_agents_md(self.root, dry_run=dry_run)
        manifest.agents_md_action = agents_result.action
        manifest.claude_md_exists = agents_result.claude_md_exists

        return manifest
