"""Context service — packet context source discovery and assembly operations."""

from datetime import datetime, timezone
import fnmatch
from pathlib import Path

from forge.adapters.adapter_config import load_adapter_profiles
from forge.adapters.manifest import load_manifest
from forge.cli.output import CommandResult
from forge.domain.context import (
    ContextBundle,
    PacketSourceSet,
    discover_packet_files,
    select_canonical_docs,
    select_working_docs,
)
from forge.domain.adapters import AdapterProfile
from forge.domain.documents import DocumentRecord, build_registry
from forge.domain.errors import ForgeError
from forge.domain.packets import find_packet_dir, parse_task_metadata

_NO_ADAPTER_VALUES: frozenset[str] = frozenset({"", "none", "null", "n/a"})
_ADAPTER_SOURCE_LIMIT = 20


def discover_packet_sources(
    root: Path, task_id: str
) -> tuple[CommandResult, PacketSourceSet | None]:
    """Discover packet-local file sources for a given task ID.

    Locates the packet directory under tasks/, enumerates all known packet
    filenames, and reports their presence status.

    Returns:
        (CommandResult, PacketSourceSet) on success — ok=True.
        (CommandResult, None) when the packet is not found — ok=False.
    """
    packet_dir = find_packet_dir(root / "tasks", task_id)

    if packet_dir is None:
        return (
            CommandResult(
                ok=False,
                command="context discover",
                errors=[f"packet '{task_id}' not found"],
            ),
            None,
        )

    files = discover_packet_files(packet_dir)
    source_set = PacketSourceSet(
        task_id=task_id,
        packet_dir=packet_dir,
        files=files,
    )

    return (
        CommandResult(
            ok=True,
            command="context discover",
            repo=str(root),
            task_id=task_id,
        ),
        source_set,
    )


def select_canonical_docs_for_packet(
    root: Path,
    task_id: str,
    context_tags: set[str],
) -> tuple[CommandResult, list[DocumentRecord]]:
    """Select relevant canonical docs for a packet given a set of context tags.

    Loads the manifest, builds the document registry, verifies the packet
    exists, then delegates to select_canonical_docs().

    Returns:
        (CommandResult, list[DocumentRecord]) on success — ok=True.
        (CommandResult, []) on failure — ok=False with errors.
    """
    try:
        manifest = load_manifest(root)
    except ForgeError as exc:
        return CommandResult(
            ok=False,
            command="context select",
            errors=[exc.message],
        ), []

    packet_dir = find_packet_dir(root / "tasks", task_id)
    if packet_dir is None:
        return CommandResult(
            ok=False,
            command="context select",
            errors=[f"packet '{task_id}' not found"],
        ), []

    registry = build_registry(manifest)
    selected = select_canonical_docs(registry, context_tags)

    return CommandResult(
        ok=True,
        command="context select",
        repo=str(root),
        task_id=task_id,
    ), selected


def select_working_docs_for_packet(
    root: Path,
    task_id: str,
    context_tags: set[str],
    include_working_docs: bool = False,
) -> tuple[CommandResult, list[DocumentRecord]]:
    """Select working docs for a packet when explicitly opted in.

    Returns an empty selection unless include_working_docs is True. The
    manifest and packet checks mirror the canonical-doc selector.
    """
    try:
        manifest = load_manifest(root)
    except ForgeError as exc:
        return CommandResult(
            ok=False,
            command="context select",
            errors=[exc.message],
        ), []

    packet_dir = find_packet_dir(root / "tasks", task_id)
    if packet_dir is None:
        return CommandResult(
            ok=False,
            command="context select",
            errors=[f"packet '{task_id}' not found"],
        ), []

    registry = build_registry(manifest)
    selected = select_working_docs(
        registry,
        context_tags,
        include_working_docs=include_working_docs,
    )

    return CommandResult(
        ok=True,
        command="context select",
        repo=str(root),
        task_id=task_id,
    ), selected


def build_context_bundle(
    root: Path,
    task_id: str,
    include_working_docs: bool = False,
    context_tags: set[str] | None = None,
) -> tuple[CommandResult, ContextBundle | None]:
    """Assemble a packet-scoped ContextBundle for one task ID.

    Uses packet-local present files plus canonical docs selected by context tags.
    Working docs are only included when include_working_docs=True.
    """
    discover_result, source_set = discover_packet_sources(root, task_id)
    if not discover_result.ok or source_set is None:
        return CommandResult(
            ok=False,
            command="context build",
            errors=discover_result.errors,
        ), None

    try:
        manifest = load_manifest(root)
    except ForgeError as exc:
        return CommandResult(
            ok=False,
            command="context build",
            errors=[exc.message],
        ), None

    tags = context_tags if context_tags is not None else {"running_tasks"}
    registry = build_registry(manifest)
    canonical_docs = select_canonical_docs(registry, tags)
    working_docs = select_working_docs(
        registry,
        tags,
        include_working_docs=include_working_docs,
    )

    present_files = source_set.present_files()
    primary_adapter = _read_primary_adapter(source_set.packet_dir)
    adapter_profile = _load_adapter_profile(root, primary_adapter)
    adapter_sources = _select_adapter_source_paths(root, adapter_profile)

    sources = [str(packet_file.path.relative_to(root)) for packet_file in present_files]
    sources.extend(adapter_sources)
    sources.extend(record.path for record in canonical_docs)
    sources.extend(record.path for record in working_docs)
    sources = _dedupe_preserve_order(sources)

    adapter_context: dict[str, object] = {
        "primary_adapter": primary_adapter or "none",
        "applied": False,
        "selected_sources": [],
        "context_priority_rules": [],
        "review_focus_hints": [],
        "test_or_validation_hints": [],
    }
    if adapter_profile is not None:
        adapter_context = {
            "primary_adapter": adapter_profile.adapter_id,
            "applied": bool(adapter_sources),
            "selected_sources": adapter_sources,
            "context_priority_rules": adapter_profile.context_priority_rules,
            "review_focus_hints": adapter_profile.review_focus_hints,
            "test_or_validation_hints": adapter_profile.test_or_validation_hints,
        }

    bundle = ContextBundle(
        task_id=task_id,
        packet_dir=source_set.packet_dir,
        packet_files=present_files,
        selected_canonical_docs=canonical_docs,
        selected_working_docs=working_docs,
        export_metadata={
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "sources": sources,
            "adapter_context": adapter_context,
        },
    )

    return CommandResult(
        ok=True,
        command="context build",
        repo=str(root),
        task_id=task_id,
    ), bundle


def build_source_metadata(root: Path, bundle: ContextBundle) -> list[dict[str, object]]:
    """Return structured metadata for selected bundle sources."""
    source_paths = [str(path) for path in bundle.export_metadata.get("sources", [])]
    packet_paths = {
        str(packet_file.path.relative_to(root))
        for packet_file in bundle.packet_files
    }
    canonical_paths = {record.path for record in bundle.selected_canonical_docs}
    working_paths = {record.path for record in bundle.selected_working_docs}

    metadata: list[dict[str, object]] = []
    for source in source_paths:
        kind = "unknown"
        if source in packet_paths:
            kind = "packet"
        elif source in canonical_paths:
            kind = "canonical"
        elif source in working_paths:
            kind = "working"

        metadata.append(
            {
                "path": source,
                "kind": kind,
                "exists": (root / source).exists(),
            }
        )

    return metadata


def _read_primary_adapter(packet_dir: Path) -> str:
    """Return packet primary_adapter value from task.md metadata."""
    task_md = packet_dir / "task.md"
    if not task_md.exists():
        return ""
    metadata = parse_task_metadata(task_md)
    raw = metadata.get("primary_adapter", "").strip()
    return "" if raw.lower() in _NO_ADAPTER_VALUES else raw


def _load_adapter_profile(root: Path, adapter_id: str) -> AdapterProfile | None:
    """Load one adapter profile by adapter_id, or None when unavailable."""
    if not adapter_id:
        return None
    try:
        profiles = load_adapter_profiles(root)
    except ForgeError:
        return None
    for profile in profiles:
        if profile.adapter_id == adapter_id:
            return profile
    return None


def _select_adapter_source_paths(root: Path, profile: AdapterProfile | None) -> list[str]:
    """Return repository-relative source files biased by adapter patterns."""
    if profile is None or not profile.relevant_file_patterns:
        return []

    candidates: list[str] = []
    for pattern in profile.relevant_file_patterns:
        for matched_path in root.glob(pattern):
            if not matched_path.is_file():
                continue
            relative = matched_path.relative_to(root).as_posix()
            if _is_ignored_by_adapter(relative, profile.ignore_file_patterns):
                continue
            candidates.append(relative)

    ordered = _dedupe_preserve_order(candidates)
    ordered = _apply_context_priority_rules(ordered, profile.context_priority_rules)
    return ordered[:_ADAPTER_SOURCE_LIMIT]


def _is_ignored_by_adapter(path: str, ignore_patterns: list[str]) -> bool:
    """Return True if path should be excluded by adapter ignore patterns."""
    return any(fnmatch.fnmatch(path, pattern) for pattern in ignore_patterns)


def _apply_context_priority_rules(paths: list[str], rules: list[str]) -> list[str]:
    """Apply simple priority ordering from adapter context priority hints."""
    rule_text = " ".join(rules).lower()
    if "source files" in rule_text and "tests" in rule_text:
        return sorted(paths, key=lambda path: (_is_test_path(path), path))
    return sorted(paths)


def _is_test_path(path: str) -> bool:
    """Return True for common test-file path patterns."""
    lowered = path.lower()
    return lowered.startswith("tests/") or "/tests/" in lowered or lowered.endswith("_test.py")


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    """Remove duplicates while preserving original order."""
    seen: set[str] = set()
    deduped: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped
