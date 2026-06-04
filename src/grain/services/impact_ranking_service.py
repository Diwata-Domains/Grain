"""Proposal-only ranking helpers for impacted-file signals."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from grain.domain.embedding import ScoredCandidate
from grain.domain.ranking import RankedCandidate
from grain.services.embedding_resolver import EmbeddingProviderResolver
from grain.services.ranking_service import RankingCandidateInput, rank_candidates


def rank_impacted_files(
    root: Path,
    touched_files: list[str],
    affected_files: list[str],
    *,
    embedding_resolver: EmbeddingProviderResolver | None = None,
) -> dict[str, object]:
    """Return inspectable ranking metadata for impacted-file candidates."""
    if not affected_files:
        return {}

    resolver = embedding_resolver or EmbeddingProviderResolver()
    provider, resolved = resolver.resolve_root(root)

    candidate_texts = {
        path: _candidate_text(root, path)
        for path in affected_files
    }
    text_to_path = {text: path for path, text in candidate_texts.items()}
    query = " ".join(touched_files).strip()
    semantic_ranked = provider.score(query, list(candidate_texts.values()))
    semantic_scores = _serialize_scored_candidates(semantic_ranked, text_to_path)
    semantic_by_path = {item["path"]: item["score"] for item in semantic_scores}

    ranked = rank_candidates(
        [
            RankingCandidateInput(
                candidate=path,
                graph_depth=_impact_graph_depth(path, touched_files),
                semantic_score=float(semantic_by_path.get(path, 0.0)),
                authority=_authority_for_path(path),
                packet_priority=_packet_priority_for_path(path),
            )
            for path in affected_files
        ]
    )

    provider_status = asdict(resolved.provider_status) if resolved.provider_status is not None else None
    return {
        "configured_provider": resolved.configured_provider,
        "active_provider": resolved.active_provider,
        "configured_model": resolved.configured_model,
        "active_model": resolved.active_model,
        "fallback_active": resolved.fallback_active,
        "fallback_reason": resolved.fallback_reason,
        "provider_status": provider_status,
        "semantic_scores": semantic_scores,
        "ranked_affected_files": _serialize_ranked_candidates(ranked),
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
        }
        for item in ranked
    ]


def _candidate_text(root: Path, path: str) -> str:
    try:
        preview = (root / path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        preview = ""
    return f"path: {path}\ncontent:\n{preview[:2000]}".strip()


def _impact_graph_depth(path: str, touched_files: list[str]) -> int:
    return 0 if path in touched_files else 1


def _authority_for_path(path: str) -> str:
    if path.startswith("docs/canonical/"):
        return "highest"
    if path.startswith("docs/runtime/"):
        return "highest_runtime"
    if path.startswith("docs/working/"):
        return "secondary"
    return ""


def _packet_priority_for_path(path: str) -> float:
    lowered = path.lower()
    return 0.5 if lowered.startswith("tests/") or "/tests/" in lowered else 1.0
