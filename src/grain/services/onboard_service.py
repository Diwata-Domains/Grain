"""Additive scaffold service for existing-project onboarding."""

from __future__ import annotations

from pathlib import Path

from grain.domain.onboard import ScaffoldManifest

_REQUIRED_DIRS = [
    "docs/canonical",
    "docs/working",
    "docs/runtime",
    "tasks",
    "prompts",
]

_STUB_FILES: dict[str, str] = {
    "docs/canonical/product_scope.md": "# Product Scope\\n\\n# DRAFT - replace with real content\\n",
    "docs/canonical/architecture.md": "# Architecture\\n\\n# DRAFT - replace with real content\\n",
    "docs/canonical/cli_spec.md": "# CLI Spec\\n\\n# DRAFT - replace with real content\\n",
    "docs/canonical/workflow_spec.md": "# Workflow Spec\\n\\n# DRAFT - replace with real content\\n",
    "docs/canonical/data_contracts.md": "# Data Contracts\\n\\n# DRAFT - replace with real content\\n",
    "docs/working/backlog.md": "# Backlog\\n\\n# DRAFT - replace with real content\\n",
    "docs/working/current_focus.md": "# Current Focus\\n\\n# DRAFT - replace with real content\\n",
    "docs/working/current_task.md": "# Current Task\\n\\n# DRAFT - replace with real content\\n",
    "docs/working/open_questions.md": "# Open Questions\\n\\n# DRAFT - replace with real content\\n",
    "docs/working/change_proposals.md": "# Change Proposals\\n\\n# DRAFT - replace with real content\\n",
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

        return manifest
