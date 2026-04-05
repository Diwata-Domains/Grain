"""Context service — packet context source discovery and assembly operations."""

from datetime import datetime, timezone
from pathlib import Path

from forge.adapters.manifest import load_manifest
from forge.cli.output import CommandResult
from forge.domain.context import (
    ContextBundle,
    PacketSourceSet,
    discover_packet_files,
    select_canonical_docs,
    select_working_docs,
)
from forge.domain.documents import DocumentRecord, build_registry
from forge.domain.errors import ForgeError
from forge.domain.packets import find_packet_dir


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
    sources = [
        str(packet_file.path.relative_to(root))
        for packet_file in present_files
    ]
    sources.extend(record.path for record in canonical_docs)
    sources.extend(record.path for record in working_docs)

    bundle = ContextBundle(
        task_id=task_id,
        packet_dir=source_set.packet_dir,
        packet_files=present_files,
        selected_canonical_docs=canonical_docs,
        selected_working_docs=working_docs,
        export_metadata={
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "sources": sources,
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
