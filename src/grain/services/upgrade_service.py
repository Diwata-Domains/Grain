# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Upgrade service — updates Grain-managed files to the current bundled versions."""

from __future__ import annotations

import difflib
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
    "docs/working/tooling_notes.md": "runtime/tooling_notes.md",
    "docs/working/workflow_metrics.md": "runtime/workflow_metrics.md",
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
    diffs: dict[str, str] = field(default_factory=dict)  # rel_path -> unified diff string
    customized: list[str] = field(default_factory=list)  # stale files with user-added content
    skipped_customized: list[str] = field(default_factory=list)  # customized files skipped in non-interactive mode
    absent: list[str] = field(default_factory=list)  # seeded files not present in workspace


def _unified_diff(rel: str, current: str, bundled: str) -> str:
    lines = list(
        difflib.unified_diff(
            current.splitlines(keepends=True),
            bundled.splitlines(keepends=True),
            fromfile=f"current/{rel}",
            tofile=f"bundled/{rel}",
        )
    )
    return "".join(lines)


def _has_user_additions(diff_text: str) -> bool:
    """Return True if the diff contains lines the user added (present in current, absent in bundled).

    In unified diff format, lines starting with '-' (excluding '---' headers) are content
    in the current file that the bundled version does not have — i.e. user-added content.
    """
    for line in diff_text.splitlines():
        if line.startswith("-") and not line.startswith("---"):
            return True
    return False


def upgrade_repo(
    root: Path,
    *,
    dry_run: bool = False,
    include_diffs: bool = False,
    allow_customized_updates: bool = False,
    add_missing: bool = False,
) -> UpgradeResult:
    """Update Grain-managed files to the current bundled versions.

    - Updates prompts, task templates, and safe runtime docs.
    - Adds files that are missing entirely.
    - Never touches user-owned files (canonical docs, working docs, task packets,
      docs_manifest.yaml, adapter_profiles.md).

    Args:
        dry_run: Preview changes without writing.
        include_diffs: Populate ``result.diffs`` with unified diff strings for stale files.
        add_missing: Seed absent seeded files; never overwrites existing files.
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
                diff_text = _unified_diff(rel, current, bundled)
                result.updated.append(rel)
                if include_diffs:
                    result.diffs[rel] = diff_text
                if _has_user_additions(diff_text):
                    result.customized.append(rel)
                    if not allow_customized_updates:
                        result.skipped_customized.append(rel)
                        continue
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

    # Absent-file detection: check which seeded files are missing from the workspace.
    _scan_absent_seeded_files(root, result, dry_run=dry_run, seed=add_missing)

    result.protected = sorted(_PROTECTED)
    return result


def write_upgrade_policy_min_version(root: Path, new_version: str) -> bool:
    """Ratchet upgrade_policy.min_version and min_version_set_at in docs_manifest.yaml.

    Uses surgical line-based replacement to preserve comments and formatting.
    Appends an upgrade_policy block with defaults if the block is absent.
    Returns True if the manifest was written.
    """
    from datetime import date

    manifest_path = root / "docs" / "runtime" / "docs_manifest.yaml"
    if not manifest_path.exists():
        return False

    today = date.today().isoformat()
    text = manifest_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    in_block = False
    updated: list[str] = []
    set_version = False
    set_date = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("upgrade_policy:"):
            in_block = True
            updated.append(line)
            continue

        if in_block:
            if line and not line[0].isspace() and stripped and not stripped.startswith("#"):
                in_block = False
                updated.append(line)
                continue

            # min_version_set_at must be checked before min_version (it's a superstring)
            if not set_date and "min_version_set_at:" in line:
                indent = " " * (len(line) - len(line.lstrip()))
                # preserve inline comment if present
                comment_part = ""
                if "#" in line:
                    comment_part = "  " + line[line.index("#"):]
                updated.append(f'{indent}min_version_set_at: "{today}"{comment_part.rstrip()}\n')
                set_date = True
                continue

            if not set_version and "min_version:" in line and "min_version_set_at" not in line:
                indent = " " * (len(line) - len(line.lstrip()))
                comment_part = ""
                if "#" in line:
                    comment_part = "  " + line[line.index("#"):]
                updated.append(f'{indent}min_version: "{new_version}"{comment_part.rstrip()}\n')
                set_version = True
                continue

        updated.append(line)

    if set_version or set_date:
        manifest_path.write_text("".join(updated), encoding="utf-8")
        return True

    # upgrade_policy block not found — append with defaults
    block = (
        "\nupgrade_policy:\n"
        f'  min_version: "{new_version}"\n'
        f'  min_version_set_at: "{today}"\n'
        "  enforce: false\n"
        "  enforce_after_days: 0\n"
        '  message: ""\n'
    )
    manifest_path.write_text(text.rstrip() + block, encoding="utf-8")
    return True


def _scan_absent_seeded_files(
    root: Path,
    result: UpgradeResult,
    *,
    dry_run: bool,
    seed: bool,
) -> None:
    """Populate result.absent with seeded files not present in the workspace.

    When seed=True, writes absent files (never overwrites existing ones).
    """
    from grain.services.init_service import _SEED_FILE_SOURCES, _SOURCE_REPO_ROOT

    already_handled = set(result.updated + result.added + result.unchanged + result.skipped_customized)

    for rel, source_rel in _SEED_FILE_SOURCES.items():
        if rel in already_handled or rel in _PROTECTED:
            continue
        target = root / rel
        if not target.exists():
            result.absent.append(rel)
            if seed and not dry_run:
                source = _SOURCE_REPO_ROOT / source_rel
                if source.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
                    result.added.append(rel)
