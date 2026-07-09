# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass, field
import tomllib
from pathlib import Path
from importlib.metadata import PackageNotFoundError, version

from grain.domain.scaffold import (
    PROMPT_SEED_SOURCES,
    REQUIRED_DIRS as _REQUIRED_DIRS,
    RUNTIME_SEED_SOURCES,
)

# Paths treated as canonical — never overwritten without --force, always reported
_CANONICAL_PREFIX = "docs/canonical"

# Bundled data directory: src/grain/data/ — included in the package via package-data.
# Falls back to the repo root for development workflows where the package is not installed.
_BUNDLED_DATA_ROOT = Path(__file__).resolve().parents[1] / "data"
_SOURCE_REPO_ROOT = (
    _BUNDLED_DATA_ROOT
    if _BUNDLED_DATA_ROOT.exists()
    else Path(__file__).resolve().parents[3]
)

# Baseline seed files written during init when missing.
# Keys: destination path relative to the new project root.
# Values: source path relative to _SOURCE_REPO_ROOT.
# The runtime and prompt maps are shared with onboard via grain.domain.scaffold;
# the working/canonical/root entries below are init-specific (onboard writes DRAFT
# stubs for those instead of copying bundled templates).
_SEED_FILE_SOURCES = {
    **RUNTIME_SEED_SOURCES,
    **PROMPT_SEED_SOURCES,
    # working docs
    "docs/working/implementation_plan.md": "runtime/implementation_plan.md",
    "docs/working/tooling_notes.md": "runtime/tooling_notes.md",
    "docs/working/backlog.md": "runtime/backlog.md",
    "docs/working/current_focus.md": "runtime/current_focus.md",
    "docs/working/open_questions.md": "runtime/open_questions.md",
    "docs/working/change_proposals.md": "runtime/change_proposals.md",
    "docs/working/roadmap.md": "runtime/roadmap.md",
    "docs/working/current_task.md": "runtime/current_task_template.md",
    "docs/working/landscape.md": "runtime/landscape_working.md",
    "docs/working/workflow_metrics.md": "runtime/workflow_metrics.md",
    # canonical docs
    "docs/canonical/product_scope.md": "runtime/product_scope.md",
    "docs/canonical/architecture.md": "runtime/architecture.md",
    "docs/canonical/decisions.md": "runtime/decisions.md",
    "docs/canonical/landscape.md": "runtime/landscape_canonical.md",
    # root files
    "CHANGELOG.md": "runtime/CHANGELOG.md",
}

_GRAIN_VERSION_PLACEHOLDER = "__GRAIN_VERSION__"
_PROJECT_NAME_PLACEHOLDER = "[Your Project Name]"
_PROJECT_TYPE_PLACEHOLDER = "[project type — e.g. web_app, cli_tool, service, data_pipeline]"


@dataclass
class InitResult:
    created: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    blocked: list[str] = field(default_factory=list)
    primary_adapter: str = ""
    secondary_adapters: list[str] = field(default_factory=list)
    adapter_warnings: list[str] = field(default_factory=list)
    bootstrapped_task_id: str = ""
    agents_md_action: str = ""   # "created" | "updated" | "appended" | "skipped"
    claude_md_exists: bool = False


def init_repo(
    root: Path,
    force: bool = False,
    dry_run: bool = False,
    primary_adapter: str = "",
    secondary_adapters: list[str] | None = None,
    bootstrap: bool = False,
    update_agents: bool = False,
    project_name: str = "",
    project_type: str = "",
) -> InitResult:
    """Scaffold the required repository structure under `root`.

    - Creates missing directories and placeholder files.
    - Skips items that already exist (unless force=True).
    - Never overwrites canonical docs silently; reports them as blocked.
    - In dry_run mode, computes and returns intended actions without writing.
    """
    result = InitResult()

    created_dirs: list[str] = []

    for rel in _REQUIRED_DIRS:
        target = root / rel
        if target.exists():
            result.skipped.append(rel)
        else:
            result.created.append(rel)
            created_dirs.append(rel)
            if not dry_run:
                target.mkdir(parents=True, exist_ok=True)

    for rel, source_rel in _SEED_FILE_SOURCES.items():
        target = root / rel
        source = _SOURCE_REPO_ROOT / source_rel

        if not source.exists():
            result.blocked.append(rel)
            continue

        text = source.read_text(encoding="utf-8")
        if rel == "docs/runtime/docs_manifest.yaml":
            text = text.replace(_GRAIN_VERSION_PLACEHOLDER, _current_grain_version())
            if project_type:
                text = text.replace(_PROJECT_TYPE_PLACEHOLDER, project_type)
            text = _stamp_phase_close_policy(text)
        if project_name:
            text = text.replace(_PROJECT_NAME_PLACEHOLDER, project_name)

        if target.exists():
            if force and not rel.startswith(_CANONICAL_PREFIX):
                result.updated.append(rel)
                if not dry_run:
                    target.write_text(text, encoding="utf-8")
            else:
                result.skipped.append(rel)
            continue

        result.created.append(rel)
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")

    # Write a .gitkeep placeholder into each newly created directory
    for rel in created_dirs:
        placeholder = root / rel / ".gitkeep"
        if not dry_run:
            placeholder.touch()

    if primary_adapter or secondary_adapters:
        _apply_adapter_selection(
            primary_adapter,
            secondary_adapters or [],
            result,
        )

    if bootstrap:
        _run_bootstrap(root, result, dry_run)

    # Always write/update AGENTS.md unless this is a pure --update-agents call
    # (update_agents=True means only do the agents block, skip the rest — but
    # here we run it regardless since init always includes it).
    from grain.services.agents_md_service import write_agents_md
    agents_result = write_agents_md(root, dry_run=dry_run)
    result.agents_md_action = agents_result.action
    result.claude_md_exists = agents_result.claude_md_exists

    return result


def update_agents_only(root: Path, dry_run: bool = False) -> InitResult:
    """Update only the AGENTS.md grain block without re-running full init."""
    from grain.services.agents_md_service import write_agents_md
    result = InitResult()
    agents_result = write_agents_md(root, dry_run=dry_run)
    result.agents_md_action = agents_result.action
    result.claude_md_exists = agents_result.claude_md_exists
    return result


def _apply_adapter_selection(
    primary_adapter: str,
    secondary_adapters: list[str],
    result: InitResult,
) -> None:
    """Validate declared adapters against source adapter profiles and record selections."""
    from grain.domain.errors import ConfigError, MissingPathError

    known_ids: set[str] = set()
    try:
        # Resolve adapter profiles from bundled data (runtime/adapter_profiles.md)
        # or fall back to the repo-root layout (docs/runtime/adapter_profiles.md).
        bundled_path = _SOURCE_REPO_ROOT / "runtime" / "adapter_profiles.md"
        repo_path = _SOURCE_REPO_ROOT / "docs" / "runtime" / "adapter_profiles.md"
        profiles_path = bundled_path if bundled_path.exists() else repo_path
        from grain.adapters.adapter_config import parse_adapter_profiles_markdown
        text = profiles_path.read_text(encoding="utf-8")
        profiles = parse_adapter_profiles_markdown(text)
        known_ids = {p.adapter_id for p in profiles}
    except (ConfigError, MissingPathError, Exception):
        result.adapter_warnings.append(
            "adapter profiles not available: adapter selection recorded without validation"
        )
        result.primary_adapter = primary_adapter
        result.secondary_adapters = list(secondary_adapters)
        return

    if primary_adapter:
        if primary_adapter in known_ids:
            result.primary_adapter = primary_adapter
        else:
            result.adapter_warnings.append(
                f"unknown primary adapter '{primary_adapter}': not found in adapter profiles"
            )

    validated_secondary: list[str] = []
    for aid in secondary_adapters:
        if aid in known_ids:
            validated_secondary.append(aid)
        else:
            result.adapter_warnings.append(
                f"unknown secondary adapter '{aid}': not found in adapter profiles"
            )
    result.secondary_adapters = validated_secondary


_PHASE_CLOSE_ANCHOR = "# Grain configuration — project-level defaults for the grain CLI."
_PHASE_CLOSE_BLOCK = (
    "# Phase-close gate: the phase number from which `grain phase close` sealing is\n"
    "# enforced. New workspaces enforce from phase 1, so `grain workflow next` refuses\n"
    "# to route into phase N until phase N-1 carries a verified `Phase N-1 closed:`\n"
    "# marker. Absent, the gate falls back to a legacy grandfather threshold (15).\n"
    "phase_close_enforced_from: 1\n"
)


def _stamp_phase_close_policy(text: str) -> str:
    """Stamp ``phase_close_enforced_from: 1`` into a freshly seeded manifest.

    New workspaces gate every phase boundary; legacy workspaces without the key
    grandfather early phases (see workflow_service.phase_close_enforced_threshold).
    Idempotent: leaves an already-stamped manifest untouched. Anchors above the
    ``grain:`` config block; falls back to appending if the anchor is absent.
    """
    if "phase_close_enforced_from:" in text:
        return text
    if _PHASE_CLOSE_ANCHOR in text:
        return text.replace(
            _PHASE_CLOSE_ANCHOR,
            _PHASE_CLOSE_BLOCK + "\n" + _PHASE_CLOSE_ANCHOR,
            1,
        )
    suffix = "" if text.endswith("\n") else "\n"
    return text + suffix + "\n" + _PHASE_CLOSE_BLOCK


def _current_grain_version() -> str:
    try:
        return version("grain-kit")
    except PackageNotFoundError:
        try:
            pyproject_path = Path(__file__).resolve().parents[3] / "pyproject.toml"
            with pyproject_path.open("rb") as f:
                return tomllib.load(f)["project"]["version"]
        except Exception:
            return "0.0.0"


def _run_bootstrap(root: Path, result: InitResult, dry_run: bool) -> None:
    """Create a starter task packet and initialize current_task.md."""
    from grain.domain.packets import next_task_id
    from grain.services.task_service import create_packet_directory

    tasks_root = root / "tasks"
    current_task_path = root / "docs" / "working" / "current_task.md"

    if dry_run:
        predicted_id = next_task_id(tasks_root)
        result.bootstrapped_task_id = predicted_id
        result.created.append(f"tasks/P1-T01-{predicted_id}")
        if current_task_path.exists():
            result.updated.append("docs/working/current_task.md")
        else:
            result.created.append("docs/working/current_task.md")
        return

    create_result = create_packet_directory(root, phase=1, task_num=1, title="Starter Task")
    if not create_result.ok:
        result.adapter_warnings.extend(create_result.errors)
        return

    task_id = create_result.task_id
    result.bootstrapped_task_id = task_id
    result.created.extend(create_result.files_created)

    if result.primary_adapter:
        _patch_task_adapter(tasks_root, task_id, result.primary_adapter)

    content = (
        "# Current Task\n\n"
        f"Task ID: {task_id}\n"
        f"Task Path: tasks/P1-T01-{task_id}/\n"
        "Status: ready\n"
    )
    current_task_path.parent.mkdir(parents=True, exist_ok=True)
    if current_task_path.exists():
        result.updated.append("docs/working/current_task.md")
    else:
        result.created.append("docs/working/current_task.md")
    current_task_path.write_text(content, encoding="utf-8")


def _patch_task_adapter(tasks_root: Path, task_id: str, primary_adapter: str) -> None:
    """Set Primary Adapter in a starter task.md."""
    from grain.domain.packets import find_packet_dir

    packet_dir = find_packet_dir(tasks_root, task_id)
    if packet_dir is None:
        return
    task_md = packet_dir / "task.md"
    if not task_md.exists():
        return
    content = task_md.read_text(encoding="utf-8")
    content = content.replace(
        "- **Primary Adapter:** none",
        f"- **Primary Adapter:** {primary_adapter}",
    )
    task_md.write_text(content, encoding="utf-8")
