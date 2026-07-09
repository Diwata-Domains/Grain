# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Context service — packet context source discovery and assembly operations."""

from dataclasses import asdict
from datetime import datetime, timezone
import fnmatch
from math import ceil
from pathlib import Path
import re

from grain.adapters.adapter_config import load_adapter_profiles
from grain.adapters.manifest import load_manifest
from grain.cli.output import CommandResult
from grain.domain.context import (
    ContextBundle,
    ContextStats,
    PacketSourceSet,
    SourceStats,
    discover_packet_files,
    select_canonical_docs,
    select_working_docs,
)
from grain.domain.adapters import AdapterProfile
from grain.domain.documents import DocumentRecord, build_registry
from grain.domain.embedding import ResolvedEmbeddingProvider, ScoredCandidate
from grain.domain.errors import ForgeError
from grain.domain.packets import find_packet_dir, parse_task_metadata
from grain.domain.ranking import RankedCandidate
from grain.services.embedding_resolver import EmbeddingProviderResolver
from grain.services.graph_service import build_knowledge_graph
from grain.services.ranking_service import RankingCandidateInput, rank_candidates

_NO_ADAPTER_VALUES: frozenset[str] = frozenset({"", "none", "null", "n/a"})
_ADAPTER_SOURCE_LIMIT = 20
_TOKEN_WARN_THRESHOLD = 8000
_TRIM_HINT_LIMIT = 3
_OBJECTIVE_SECTION = re.compile(
    r"^## Objective\s*\n(.*?)(?=^## |\Z)",
    re.MULTILINE | re.DOTALL,
)
_PLACEHOLDER_LINE = re.compile(r"^\[.*\]$")
_OBSIDIAN_WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")


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
    embedding_resolver: EmbeddingProviderResolver | None = None,
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
    packet_source_paths = [str(packet_file.path.relative_to(root)) for packet_file in present_files]
    adapter_candidates = _adapter_candidate_paths(root, adapter_profile)
    if adapter_profile is not None:
        adapter_candidates = _apply_context_priority_rules(
            adapter_candidates,
            adapter_profile.context_priority_rules,
        )
    adapter_sources, selection_trace = _select_adapter_source_paths(
        root,
        packet_source_paths,
        adapter_candidates,
        require_graph_trace=_requires_graph_trace(adapter_profile),
    )
    if adapter_profile is not None and adapter_profile.adapter_id == "obsidian_adapter":
        objective = _read_task_objective(source_set.packet_dir / "task.md")
        adapter_sources, selection_trace = _apply_obsidian_link_priority(
            root,
            adapter_sources,
            selection_trace,
            objective=objective,
        )
    if adapter_profile is not None and adapter_profile.adapter_id == "database_adapter":
        objective = _read_task_objective(source_set.packet_dir / "task.md")
        adapter_sources = _apply_database_source_priority(
            adapter_sources,
            objective=objective,
        )
    if adapter_profile is not None and adapter_profile.adapter_id == "crawler_adapter":
        objective = _read_task_objective(source_set.packet_dir / "task.md")
        adapter_sources = _apply_crawler_source_priority(
            adapter_sources,
            objective=objective,
        )
    semantic_resolution: ResolvedEmbeddingProvider | None = None
    semantic_scores: list[dict[str, object]] = []
    ranked_scores: list[dict[str, object]] = []
    if adapter_sources:
        (
            adapter_sources,
            semantic_resolution,
            semantic_scores,
            ranked_scores,
        ) = _rerank_adapter_sources(
            root=root,
            packet_dir=source_set.packet_dir,
            adapter_sources=adapter_sources,
            selection_trace=selection_trace,
            embedding_resolver=embedding_resolver,
        )
    if adapter_profile is not None and adapter_profile.adapter_id == "obsidian_adapter":
        objective = _read_task_objective(source_set.packet_dir / "task.md")
        adapter_sources, selection_trace = _apply_obsidian_link_priority(
            root,
            adapter_sources,
            selection_trace,
            objective=objective,
        )
    if adapter_profile is not None and adapter_profile.adapter_id == "database_adapter":
        objective = _read_task_objective(source_set.packet_dir / "task.md")
        adapter_sources = _apply_database_source_priority(
            adapter_sources,
            objective=objective,
        )
    if adapter_profile is not None and adapter_profile.adapter_id == "crawler_adapter":
        objective = _read_task_objective(source_set.packet_dir / "task.md")
        adapter_sources = _apply_crawler_source_priority(
            adapter_sources,
            objective=objective,
        )

    sources = list(packet_source_paths)
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
        "selection_trace": {},
        "semantic_ranking": {},
    }
    if adapter_profile is not None:
        adapter_context = {
            "primary_adapter": adapter_profile.adapter_id,
            "applied": bool(adapter_sources),
            "selected_sources": adapter_sources,
            "context_priority_rules": adapter_profile.context_priority_rules,
            "review_focus_hints": adapter_profile.review_focus_hints,
            "test_or_validation_hints": adapter_profile.test_or_validation_hints,
            "selection_trace": selection_trace,
            "semantic_ranking": _semantic_ranking_metadata(
                semantic_resolution,
                semantic_scores,
                ranked_scores,
            ),
        }

    stats = _compute_context_stats(
        root=root,
        packet_paths=packet_source_paths,
        adapter_sources=adapter_sources,
        selection_trace=selection_trace,
        canonical_docs=canonical_docs,
        working_docs=working_docs,
    )

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
            "context_stats": {
                "total_sources": stats.total_sources,
                "total_lines": stats.total_lines,
                "packet_sources": stats.packet_sources,
                "graph_traced_sources": stats.graph_traced_sources,
                "glob_only_sources": stats.glob_only_sources,
                "canonical_sources": stats.canonical_sources,
                "working_sources": stats.working_sources,
                "per_file": [
                    {
                        "path": s.path,
                        "lines": s.lines,
                        "bytes": _count_file_bytes(root, s.path),
                        "estimated_tokens": _estimate_tokens_from_size(_count_file_bytes(root, s.path)),
                        "selection_method": s.selection_method,
                        "graph_depth": s.graph_depth,
                    }
                    for s in stats.per_file
                ],
            },
            "context_budget": _build_context_budget(root, stats),
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


def _adapter_candidate_paths(root: Path, profile: AdapterProfile | None) -> list[str]:
    """Return adapter-biased candidate file paths before graph filtering."""
    if profile is None or not profile.relevant_file_patterns:
        return []
    candidates: list[str] = []
    for pattern in profile.relevant_file_patterns:
        for matched_path in _iter_adapter_matches(root, pattern):
            if not matched_path.is_file():
                continue
            relative = matched_path.relative_to(root).as_posix()
            if _is_ignored_by_adapter(relative, profile.ignore_file_patterns):
                continue
            candidates.append(relative)
    return _dedupe_preserve_order(candidates)


def _iter_adapter_matches(root: Path, pattern: str):
    """Yield matches for one adapter context pattern.

    Bare recursive directory patterns like `src/**` should contribute files,
    not just intermediate directories.
    """
    if pattern.endswith("/**"):
        base = root / pattern[:-3]
        if not base.exists():
            return []
        return base.rglob("*")
    return root.glob(pattern)


def _select_adapter_source_paths(
    root: Path,
    packet_paths: list[str],
    candidate_paths: list[str],
    *,
    require_graph_trace: bool = True,
) -> tuple[list[str], dict[str, list[str]]]:
    """Select graph-connected adapter sources plus trace paths.

    Every selected source must have a traceable path to packet-local files.
    """
    if not candidate_paths:
        return [], {}

    if not require_graph_trace:
        return _dedupe_preserve_order(candidate_paths), {}

    if not packet_paths:
        return [], {}

    graph_sources = _dedupe_preserve_order(packet_paths + candidate_paths)
    result, artifact = build_knowledge_graph(root, graph_sources, produced_by="context_service.graph_select")
    if not result.ok or artifact is None:
        return [], {}

    adjacency = _build_graph_adjacency(artifact.edges)
    packet_nodes = {_file_node_id(path) for path in packet_paths}

    selected: list[str] = []
    trace: dict[str, list[str]] = {}
    for candidate in candidate_paths:
        candidate_node = _file_node_id(candidate)
        path_nodes = _shortest_path_to_any(candidate_node, packet_nodes, adjacency)
        if not path_nodes:
            continue
        selected.append(candidate)
        trace[candidate] = [_node_to_path_or_id(node) for node in path_nodes]

    return _dedupe_preserve_order(selected), trace


def _rerank_adapter_sources(
    *,
    root: Path,
    packet_dir: Path,
    adapter_sources: list[str],
    selection_trace: dict[str, list[str]],
    embedding_resolver: EmbeddingProviderResolver | None,
) -> tuple[list[str], ResolvedEmbeddingProvider | None, list[dict[str, object]], list[dict[str, object]]]:
    graph_derived_sources = [path for path in adapter_sources if path in selection_trace]
    ranking_sources = graph_derived_sources or adapter_sources
    if not ranking_sources:
        return adapter_sources[:_ADAPTER_SOURCE_LIMIT], None, [], []

    query = _read_task_objective(packet_dir / "task.md")
    if not query:
        return adapter_sources[:_ADAPTER_SOURCE_LIMIT], None, [], []

    resolver = embedding_resolver or EmbeddingProviderResolver()
    provider, resolved = resolver.resolve_root(root)

    candidate_texts = {
        path: _build_candidate_text(root, path)
        for path in ranking_sources
    }
    text_to_path = {text: path for path, text in candidate_texts.items()}
    ranked = provider.score(query, list(candidate_texts.values()))
    semantic_scores = _serialize_scored_candidates(ranked, text_to_path)
    semantic_by_path = {item["path"]: item["score"] for item in semantic_scores}
    ranked_candidates = rank_candidates(
        [
            RankingCandidateInput(
                candidate=path,
                graph_depth=_graph_depth_for_path(path, selection_trace),
                semantic_score=float(semantic_by_path.get(path, 0.0)),
                authority=_context_authority_for_path(path),
                packet_priority=_packet_priority_for_path(path),
                metadata={"selection_trace": selection_trace.get(path, [])},
            )
            for path in ranking_sources
        ]
    )
    ranked_paths = [item.candidate for item in ranked_candidates]
    ranked_set = set(ranked_paths)
    reranked_sources = ranked_paths + [
        path
        for path in adapter_sources
        if path not in ranked_set
    ]

    return (
        reranked_sources[:_ADAPTER_SOURCE_LIMIT],
        resolved,
        semantic_scores,
        _serialize_ranked_candidates(ranked_candidates),
    )


def _apply_obsidian_link_priority(
    root: Path,
    adapter_sources: list[str],
    selection_trace: dict[str, list[str]],
    *,
    objective: str,
) -> tuple[list[str], dict[str, list[str]]]:
    if not adapter_sources or not objective.strip():
        return adapter_sources, selection_trace

    objective_lower = objective.lower()
    stem_to_paths: dict[str, list[str]] = {}
    for path in adapter_sources:
        stem_to_paths.setdefault(Path(path).stem.lower(), []).append(path)

    anchor_paths = [
        path
        for path in adapter_sources
        if Path(path).stem.lower() in objective_lower
    ]
    if not anchor_paths:
        anchor_paths = [
            path
            for path in adapter_sources
            if _extract_obsidian_wikilinks(root, path)
        ]
    if not anchor_paths:
        return adapter_sources, selection_trace

    linked_paths: list[str] = []
    updated_trace = dict(selection_trace)
    for anchor in anchor_paths:
        for linked_stem in _extract_obsidian_wikilinks(root, anchor):
            for candidate in stem_to_paths.get(linked_stem.lower(), []):
                if candidate == anchor or candidate in linked_paths:
                    continue
                linked_paths.append(candidate)
                updated_trace[candidate] = ["obsidian_link", anchor, candidate]

    prioritized = anchor_paths + linked_paths + [
        path for path in adapter_sources if path not in anchor_paths and path not in linked_paths
    ]
    return _dedupe_preserve_order(prioritized), updated_trace


def _extract_obsidian_wikilinks(root: Path, relative_path: str) -> list[str]:
    path = root / relative_path
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return _dedupe_preserve_order([match.group(1).strip() for match in _OBSIDIAN_WIKILINK.finditer(text) if match.group(1).strip()])


def _apply_database_source_priority(
    adapter_sources: list[str],
    *,
    objective: str,
) -> list[str]:
    if not adapter_sources:
        return adapter_sources

    objective_lower = objective.lower()
    prefers_persistence = any(
        token in objective_lower
        for token in (
            "query",
            "sql",
            "orm",
            "repository",
            "persistence",
            "persist",
            "database access",
        )
    )

    def _database_priority(path: str) -> tuple[int, int, str]:
        lowered = path.lower()
        is_migration = any(token in lowered for token in ("migrations/", "alembic/"))
        is_schema = lowered.endswith(".sql") or lowered.endswith("schema.prisma") or "/schema." in lowered
        is_model = "/models/" in lowered or lowered.startswith("models/")
        is_repository = "/repositories/" in lowered or lowered.startswith("repositories/")
        is_db_layer = "/db/" in lowered or lowered.startswith("db/")
        is_query = (
            "/queries/" in lowered
            or lowered.startswith("queries/")
            or (lowered.endswith(".sql") and not is_schema and not is_migration)
        )

        objective_boost = 0
        if ("migration" in objective_lower and is_migration) or ("schema" in objective_lower and is_schema):
            objective_boost = -1

        if is_schema or is_migration:
            bucket = 0
        elif prefers_persistence and (is_query or is_repository or is_db_layer):
            bucket = 1
        elif is_model or is_query or is_repository or is_db_layer:
            bucket = 2
        else:
            bucket = 3
        return (bucket, objective_boost, path)

    return sorted(adapter_sources, key=_database_priority)


def _apply_crawler_source_priority(
    adapter_sources: list[str],
    *,
    objective: str,
) -> list[str]:
    if not adapter_sources:
        return adapter_sources

    objective_lower = objective.lower()
    prefers_extraction = any(
        token in objective_lower
        for token in (
            "extract",
            "extraction",
            "output",
            "normalize",
            "normalization",
            "validation",
            "quality",
            "schema",
        )
    )
    prefers_quality = any(
        token in objective_lower
        for token in (
            "output",
            "normalize",
            "normalization",
            "validation",
            "quality",
        )
    )

    def _crawler_priority(path: str) -> tuple[int, int, str]:
        lowered = path.lower()
        is_config = any(token in lowered for token in ("crawl", "scrapy.cfg", "playwright.config", "robots.txt"))
        is_selector = "selector" in lowered or "/selectors/" in lowered or lowered.startswith("selectors/")
        is_schema = "/schemas/" in lowered or lowered.startswith("schemas/") or "schema" in lowered
        is_extractor = any(token in lowered for token in ("/extractors/", "/parsers/")) or lowered.startswith(("extractors/", "parsers/"))
        is_fixture = any(token in lowered for token in ("/fixtures/", "/outputs/")) or lowered.startswith(("fixtures/", "outputs/"))
        is_normalizer = (
            "/normalizers/" in lowered
            or lowered.startswith("normalizers/")
            or "normalizer" in lowered
            or "normalize" in lowered
        )

        objective_boost = 0
        if ("selector" in objective_lower and is_selector) or ("crawl" in objective_lower and is_config):
            objective_boost = -1

        if is_config or is_selector:
            bucket = 0
        elif prefers_quality and (is_fixture or is_normalizer):
            bucket = 1
        elif prefers_extraction and (is_schema or is_extractor or is_fixture or is_normalizer):
            bucket = 2
        elif is_schema or is_extractor or is_fixture or is_normalizer:
            bucket = 3
        else:
            bucket = 4
        return (bucket, objective_boost, path)

    return sorted(adapter_sources, key=_crawler_priority)


def _semantic_ranking_metadata(
    resolved: ResolvedEmbeddingProvider | None,
    semantic_scores: list[dict[str, object]],
    ranked_scores: list[dict[str, object]],
) -> dict[str, object]:
    if resolved is None:
        return {}

    provider_status = asdict(resolved.provider_status) if resolved.provider_status is not None else None
    return {
        "configured_provider": resolved.configured_provider,
        "active_provider": resolved.active_provider,
        "configured_model": resolved.configured_model,
        "active_model": resolved.active_model,
        "fallback_active": resolved.fallback_active,
        "fallback_reason": resolved.fallback_reason,
        "provider_status": provider_status,
        "applied": bool(ranked_scores),
        "scores": semantic_scores,
        "ranked_scores": ranked_scores,
    }


def _serialize_scored_candidates(
    ranked: list[ScoredCandidate],
    text_to_path: dict[str, str],
) -> list[dict[str, object]]:
    return [
        {
            "path": text_to_path[item.candidate],
            "score": item.score,
            "provider_id": item.provider_id,
            "metadata": item.metadata,
        }
        for item in ranked
        if item.candidate in text_to_path
    ]


def _serialize_ranked_candidates(ranked: list[RankedCandidate]) -> list[dict[str, object]]:
    return [
        {
            "path": item.candidate,
            "total_score": item.total_score,
            "components": [
                {
                    "signal_id": component.signal_id,
                    "raw_score": component.raw_score,
                    "weight": component.weight,
                    "weighted_score": component.weighted_score,
                    "detail": component.detail,
                }
                for component in item.components
            ],
            "metadata": item.metadata,
        }
        for item in ranked
    ]


def _graph_depth_for_path(path: str, selection_trace: dict[str, list[str]]) -> int | None:
    trace = selection_trace.get(path, [])
    if not trace:
        return None
    return max(0, len(trace) - 1)


def _context_authority_for_path(path: str) -> str:
    if path.startswith("docs/canonical/"):
        return "highest"
    if path.startswith("docs/runtime/"):
        return "highest_runtime"
    if path.startswith("docs/working/"):
        return "secondary"
    return ""


def _packet_priority_for_path(path: str) -> float:
    return 0.5 if _is_test_path(path) else 1.0


def _read_task_objective(task_md_path: Path) -> str:
    if not task_md_path.exists():
        return ""

    text = task_md_path.read_text(encoding="utf-8")
    match = _OBJECTIVE_SECTION.search(text)
    if match is None:
        return ""

    lines = [line.strip() for line in match.group(1).splitlines()]
    cleaned = [line for line in lines if line and not _PLACEHOLDER_LINE.match(line)]
    return " ".join(cleaned).strip()


def _build_candidate_text(root: Path, path: str) -> str:
    preview = _read_candidate_preview(root, path)
    return f"path: {path}\ncontent:\n{preview}".strip()


def _read_candidate_preview(root: Path, path: str, max_lines: int = 40, max_chars: int = 2000) -> str:
    try:
        with (root / path).open(encoding="utf-8", errors="replace") as handle:
            lines: list[str] = []
            total_chars = 0
            for index, raw_line in enumerate(handle):
                if index >= max_lines or total_chars >= max_chars:
                    break
                line = raw_line.rstrip()
                remaining = max_chars - total_chars
                if len(line) > remaining:
                    line = line[:remaining]
                lines.append(line)
                total_chars += len(line)
    except OSError:
        return ""
    return "\n".join(lines)


def _requires_graph_trace(profile: AdapterProfile | None) -> bool:
    """Return whether adapter source selection should require graph connectivity."""
    if profile is None:
        return True
    return profile.adapter_id not in {
        "spreadsheet_adapter",
        "docs_adapter",
        "obsidian_adapter",
        "data_adapter",
        "database_adapter",
        "crawler_adapter",
    }


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


def _build_graph_adjacency(edges: list[object]) -> dict[str, set[str]]:
    adjacency: dict[str, set[str]] = {}
    for edge in edges:
        source = getattr(edge, "source", "")
        target = getattr(edge, "target", "")
        if not source or not target:
            continue
        adjacency.setdefault(source, set()).add(target)
        adjacency.setdefault(target, set()).add(source)
    return adjacency


def _file_node_id(path: str) -> str:
    return f"file::{path}"


def _shortest_path_to_any(
    start: str,
    targets: set[str],
    adjacency: dict[str, set[str]],
) -> list[str]:
    if start in targets:
        return [start]
    if start not in adjacency:
        return []

    queue: list[list[str]] = [[start]]
    seen: set[str] = {start}
    while queue:
        path = queue.pop(0)
        node = path[-1]
        for neighbor in sorted(adjacency.get(node, set())):
            if neighbor in seen:
                continue
            next_path = path + [neighbor]
            if neighbor in targets:
                return next_path
            seen.add(neighbor)
            queue.append(next_path)
    return []


def _node_to_path_or_id(node_id: str) -> str:
    if node_id.startswith("file::"):
        return node_id.removeprefix("file::")
    return node_id


def _count_file_lines(root: Path, path: str) -> int:
    """Return the line count for a file, or 0 if unreadable."""
    try:
        return sum(1 for _ in (root / path).open(encoding="utf-8", errors="replace"))
    except OSError:
        return 0


def _count_file_bytes(root: Path, path: str) -> int:
    try:
        return (root / path).stat().st_size
    except OSError:
        return 0


def _estimate_tokens_from_size(byte_count: int) -> int:
    if byte_count <= 0:
        return 0
    return ceil(byte_count / 4)


def _build_context_budget(root: Path, stats: ContextStats) -> dict[str, object]:
    per_file_budget: list[dict[str, object]] = []
    total_bytes = 0
    total_estimated_tokens = 0

    for item in stats.per_file:
        byte_count = _count_file_bytes(root, item.path)
        estimated_tokens = _estimate_tokens_from_size(byte_count)
        total_bytes += byte_count
        total_estimated_tokens += estimated_tokens
        per_file_budget.append(
            {
                "path": item.path,
                "selection_method": item.selection_method,
                "lines": item.lines,
                "bytes": byte_count,
                "estimated_tokens": estimated_tokens,
            }
        )

    trim_candidates = sorted(
        (
            item for item in per_file_budget
            if item["selection_method"] != "packet"
        ),
        key=lambda item: (
            _trim_priority(str(item["selection_method"])),
            -int(item["estimated_tokens"]),
            str(item["path"]),
        ),
    )
    trim_hints = [
        {
            "path": item["path"],
            "estimated_tokens": item["estimated_tokens"],
            "reason": _trim_reason(str(item["selection_method"])),
        }
        for item in trim_candidates[:_TRIM_HINT_LIMIT]
    ]

    return {
        "source_count": stats.total_sources,
        "total_bytes": total_bytes,
        "estimated_tokens": total_estimated_tokens,
        "warning_threshold_tokens": _TOKEN_WARN_THRESHOLD,
        "warning_active": total_estimated_tokens >= _TOKEN_WARN_THRESHOLD,
        "trim_hints": trim_hints,
    }


def _trim_priority(selection_method: str) -> int:
    order = {
        "working": 0,
        "canonical": 1,
        "glob_only": 2,
        "graph_traced": 3,
        "wiki_linked": 4,
    }
    return order.get(selection_method, 5)


def _trim_reason(selection_method: str) -> str:
    reasons = {
        "working": "working doc can usually be dropped first",
        "canonical": "canonical doc is often broader than packet-local sources",
        "glob_only": "glob-only source has weaker structural justification",
        "graph_traced": "graph-traced source is a secondary dependency candidate",
        "wiki_linked": "wiki-linked note may be optional if the objective is narrow",
    }
    return reasons.get(selection_method, "non-packet source is the safest first trim candidate")


def _compute_context_stats(
    root: Path,
    packet_paths: list[str],
    adapter_sources: list[str],
    selection_trace: dict[str, list[str]],
    canonical_docs: list,
    working_docs: list,
) -> ContextStats:
    """Compute per-file line counts and selection method for a context bundle."""
    per_file: list[SourceStats] = []
    packet_set = set(packet_paths)
    adapter_set = set(adapter_sources)
    traced_set = set(selection_trace.keys())

    for path in packet_paths:
        per_file.append(SourceStats(
            path=path,
            lines=_count_file_lines(root, path),
            selection_method="packet",
            graph_depth=-1,
        ))

    for path in adapter_sources:
        if path in traced_set:
            trace = selection_trace[path]
            if trace and trace[0] == "obsidian_link":
                depth = 1
                method = "wiki_linked"
            else:
                depth = max(0, len(trace) - 1)
                method = "graph_traced"
        else:
            depth = -1
            method = "glob_only"
        per_file.append(SourceStats(
            path=path,
            lines=_count_file_lines(root, path),
            selection_method=method,
            graph_depth=depth,
        ))

    for record in canonical_docs:
        path = record.path
        if path not in packet_set and path not in adapter_set:
            per_file.append(SourceStats(
                path=path,
                lines=_count_file_lines(root, path),
                selection_method="canonical",
                graph_depth=-1,
            ))

    for record in working_docs:
        path = record.path
        if path not in packet_set and path not in adapter_set:
            per_file.append(SourceStats(
                path=path,
                lines=_count_file_lines(root, path),
                selection_method="working",
                graph_depth=-1,
            ))

    return ContextStats(
        total_sources=len(per_file),
        total_lines=sum(s.lines for s in per_file),
        packet_sources=sum(1 for s in per_file if s.selection_method == "packet"),
        graph_traced_sources=sum(1 for s in per_file if s.selection_method == "graph_traced"),
        glob_only_sources=sum(1 for s in per_file if s.selection_method == "glob_only"),
        canonical_sources=sum(1 for s in per_file if s.selection_method == "canonical"),
        working_sources=sum(1 for s in per_file if s.selection_method == "working"),
        per_file=per_file,
    )
