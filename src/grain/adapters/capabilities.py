# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Adapter capability implementations backed by structural graph outputs."""

from __future__ import annotations

import fnmatch
from pathlib import Path

from grain.domain.adapters import (
    AdapterProfile,
    ArtifactPattern,
    ContextHint,
    FollowupSuggestion,
    ImpactSignal,
    ScopeSignal,
    ValidationRequirement,
)
from grain.services.graph_service import build_knowledge_graph

_GRAPH_HOPS_FOR_IMPACT = 2
_CANDIDATE_LIMIT = 80


class GraphAwareAdapterCapability:
    """Adapter capability implementation using graph outputs when available.

    Falls back to deterministic static profile signals when graph construction
    does not provide useful data.
    """

    def __init__(self, root: Path, profile: AdapterProfile):
        self.root = root
        self.profile = profile

    def detect_scope(self, scope_description: str) -> ScopeSignal:
        candidates = _candidate_files(self.root, self.profile)
        if not candidates:
            return _static_scope_signal(self.profile)

        result, artifact = build_knowledge_graph(
            self.root,
            candidates,
            produced_by=f"adapter_capability.detect_scope.{self.profile.adapter_id}",
        )
        if not result.ok or artifact is None:
            return _fallback_scope_signal(self.profile, candidates)

        file_paths = _graph_file_paths(artifact)
        if not file_paths:
            return _fallback_scope_signal(self.profile, candidates)

        relevant_areas = sorted(
            {self.profile.domain_type, *self.profile.applies_to, *[node.kind for node in artifact.nodes]}
        )
        return ScopeSignal(
            file_patterns=file_paths,
            relevant_areas=relevant_areas,
        )

    def collect_context(self, task_description: str) -> ContextHint:
        return ContextHint(
            file_patterns=self.profile.relevant_file_patterns,
            priority_rules=self.profile.context_priority_rules,
        )

    def analyze_impact(self, touched_files: list[str]) -> ImpactSignal:
        candidates = _candidate_files(self.root, self.profile)
        graph_sources = _dedupe_preserve_order([*touched_files, *candidates])
        if not graph_sources:
            return ImpactSignal(affected_files=[], downstream_areas=[self.profile.domain_type])

        result, artifact = build_knowledge_graph(
            self.root,
            graph_sources,
            produced_by=f"adapter_capability.analyze_impact.{self.profile.adapter_id}",
        )
        if not result.ok or artifact is None:
            return ImpactSignal(
                affected_files=_dedupe_preserve_order(touched_files),
                downstream_areas=[self.profile.domain_type],
            )

        adjacency = _graph_adjacency(artifact)
        file_node_to_path = {
            node.id: str(node.metadata.get("path", ""))
            for node in artifact.nodes
            if node.kind in {"file", "canonical_doc", "runtime_doc"}
            and isinstance(node.metadata.get("path", ""), str)
            and str(node.metadata.get("path", ""))
        }
        start_nodes = [
            f"file::{path}"
            for path in touched_files
            if f"file::{path}" in file_node_to_path
        ]
        if not start_nodes:
            return ImpactSignal(
                affected_files=_dedupe_preserve_order(touched_files),
                downstream_areas=[self.profile.domain_type],
            )

        impacted_nodes = _reachable_within_hops(adjacency, start_nodes, _GRAPH_HOPS_FOR_IMPACT)
        impacted_paths = _dedupe_preserve_order(
            [file_node_to_path[node_id] for node_id in impacted_nodes if node_id in file_node_to_path]
        )
        downstream_areas = sorted(
            {self.profile.domain_type, *[node.kind for node in artifact.nodes if node.id in impacted_nodes]}
        )
        return ImpactSignal(
            affected_files=impacted_paths,
            downstream_areas=downstream_areas,
        )

    def validate_changes(self, task_description: str) -> ValidationRequirement:
        return ValidationRequirement(requirements=self.profile.test_or_validation_hints)

    def export_artifacts(self, task_description: str) -> ArtifactPattern:
        patterns = [f"adapter:{self.profile.adapter_id}", *self.profile.relevant_file_patterns]
        return ArtifactPattern(patterns=_dedupe_preserve_order(patterns))

    def suggest_followups(self, execution_outcome: str) -> FollowupSuggestion:
        followups = []
        if self.profile.review_focus_hints:
            followups.append(f"review-focus:{self.profile.review_focus_hints[0]}")
        if self.profile.test_or_validation_hints:
            followups.append(f"validate:{self.profile.test_or_validation_hints[0]}")
        return FollowupSuggestion(followups=followups)


def _candidate_files(root: Path, profile: AdapterProfile) -> list[str]:
    if not profile.relevant_file_patterns:
        return []
    candidates: list[str] = []
    for pattern in profile.relevant_file_patterns:
        for matched in _iter_profile_matches(root, pattern):
            if not matched.is_file():
                continue
            rel = matched.relative_to(root).as_posix()
            if any(fnmatch.fnmatch(rel, pat) for pat in profile.ignore_file_patterns):
                continue
            candidates.append(rel)
    return _dedupe_preserve_order(candidates)[:_CANDIDATE_LIMIT]


def _iter_profile_matches(root: Path, pattern: str):
    """Yield matches for one adapter pattern.

    `Path.glob("src/**")` is not reliable for file discovery across Python
    versions because it primarily enumerates directories. Treat bare recursive
    directory patterns as "all files under this subtree" explicitly.
    """
    if pattern.endswith("/**"):
        base = root / pattern[:-3]
        if not base.exists():
            return []
        return base.rglob("*")
    return root.glob(pattern)


def _static_scope_signal(profile: AdapterProfile) -> ScopeSignal:
    return ScopeSignal(
        file_patterns=profile.relevant_file_patterns,
        relevant_areas=sorted({profile.domain_type, *profile.applies_to}),
    )


def _fallback_scope_signal(profile: AdapterProfile, candidates: list[str]) -> ScopeSignal:
    return ScopeSignal(
        file_patterns=candidates or profile.relevant_file_patterns,
        relevant_areas=sorted({profile.domain_type, *profile.applies_to}),
    )


def _graph_file_paths(artifact) -> list[str]:
    paths: list[str] = []
    for node in artifact.nodes:
        if node.kind not in {"file", "canonical_doc", "runtime_doc"}:
            continue
        path = node.metadata.get("path", "")
        if isinstance(path, str) and path:
            paths.append(path)
    return _dedupe_preserve_order(paths)


def _graph_adjacency(artifact) -> dict[str, set[str]]:
    adjacency: dict[str, set[str]] = {}
    for edge in artifact.edges:
        adjacency.setdefault(edge.source, set()).add(edge.target)
        adjacency.setdefault(edge.target, set()).add(edge.source)
    return adjacency


def _reachable_within_hops(
    adjacency: dict[str, set[str]],
    start_nodes: list[str],
    max_hops: int,
) -> set[str]:
    seen: set[str] = set(start_nodes)
    frontier: set[str] = set(start_nodes)
    for _ in range(max_hops):
        next_frontier: set[str] = set()
        for node in frontier:
            for neighbor in adjacency.get(node, set()):
                if neighbor in seen:
                    continue
                seen.add(neighbor)
                next_frontier.add(neighbor)
        if not next_frontier:
            break
        frontier = next_frontier
    return seen


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out
