"""Upgrade service — updates Grain-managed files to the current bundled versions."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

# Bundled data root — mirrors init_service resolution.
_BUNDLED_DATA_ROOT = Path(__file__).resolve().parents[1] / "data"
_SOURCE_ROOT = (
    _BUNDLED_DATA_ROOT
    if _BUNDLED_DATA_ROOT.exists()
    else Path(__file__).resolve().parents[3]
)

# Files Grain owns — always updated to the current bundled version.
# Keys: destination path relative to project root.
# Values: source path relative to _SOURCE_ROOT.
_UPGRADE_TARGETS: dict[str, str] = {
    "prompts/task.execute.md": "prompts/task.execute.md",
    "prompts/task.review.md": "prompts/task.review.md",
    "prompts/task.close.md": "prompts/task.close.md",
    "prompts/task.plan.next.md": "prompts/task.plan.next.md",
    "prompts/tasks.next_and_implement.md": "prompts/tasks.next_and_implement.md",
    "prompts/tasks.review.md": "prompts/tasks.review.md",
    "prompts/tasks.close.md": "prompts/tasks.close.md",
    "prompts/tasks.plan.next.md": "prompts/tasks.plan.next.md",
    "prompts/workflow.onboard.new.md": "prompts/workflow.onboard.new.md",
    "prompts/workflow.onboard.existing.md": "prompts/workflow.onboard.existing.md",
    "prompts/workflow.init.md": "prompts/workflow.init.md",
    "prompts/phase.plan.next.md": "prompts/phase.plan.next.md",
    "prompts/phase.review.md": "prompts/phase.review.md",
    "prompts/phase.review_and_close.md": "prompts/phase.review_and_close.md",
    "templates/tasks/task.md": "templates/tasks/task.md",
    "templates/tasks/context.md": "templates/tasks/context.md",
    "templates/tasks/plan.md": "templates/tasks/plan.md",
    "templates/tasks/deliverable_spec.md": "templates/tasks/deliverable_spec.md",
    "templates/tasks/results.md": "templates/tasks/results.md",
    "templates/tasks/handoff.md": "templates/tasks/handoff.md",
    "templates/tasks/task_packet.md": "templates/tasks/task_packet.md",
    "docs/runtime/PROJECT_RULES.md": "runtime/PROJECT_RULES.md",
    "docs/runtime/context_loading.md": "runtime/context_loading.md",
    "docs/runtime/agent_profiles.md": "runtime/agent_profiles.md",
    "docs/runtime/docs_index.md": "runtime/docs_index.md",
    "docs/runtime/workflow_loop.yaml": "runtime/workflow_loop.yaml",
}

# Files seeded if missing but never overwritten — user may have customized these.
_ADDITIVE_TARGETS: dict[str, str] = {
    "docs/working/implementation_plan.md": "runtime/implementation_plan.md",
}

# Files Grain never touches — user-owned.
_PROTECTED: frozenset[str] = frozenset(
    {
        "docs/runtime/docs_manifest.yaml",
        "docs/runtime/adapter_profiles.md",
    }
)


@dataclass
class UpgradeResult:
    updated: list[str] = field(default_factory=list)
    added: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    protected: list[str] = field(default_factory=list)


def upgrade_repo(root: Path, *, dry_run: bool = False) -> UpgradeResult:
    """Update Grain-managed files to the current bundled versions.

    - Updates prompts, task templates, and safe runtime docs.
    - Adds files that are missing entirely.
    - Never touches user-owned files (canonical docs, working docs, task packets,
      docs_manifest.yaml, adapter_profiles.md).
    """
    result = UpgradeResult()

    for rel, source_rel in _UPGRADE_TARGETS.items():
        source = _SOURCE_ROOT / source_rel
        if not source.exists():
            continue
        bundled = source.read_text(encoding="utf-8")
        target = root / rel
        if target.exists():
            current = target.read_text(encoding="utf-8")
            if current == bundled:
                result.unchanged.append(rel)
            else:
                result.updated.append(rel)
                if not dry_run:
                    target.write_text(bundled, encoding="utf-8")
        else:
            result.added.append(rel)
            if not dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(bundled, encoding="utf-8")

    for rel, source_rel in _ADDITIVE_TARGETS.items():
        source = _SOURCE_ROOT / source_rel
        if not source.exists():
            continue
        target = root / rel
        if target.exists():
            result.unchanged.append(rel)
        else:
            result.added.append(rel)
            if not dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    result.protected = sorted(_PROTECTED)
    return result
