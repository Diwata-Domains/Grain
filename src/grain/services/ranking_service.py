"""Deterministic weighted ranking service for advisory scoring."""

from __future__ import annotations

from dataclasses import dataclass, field

from grain.domain.ranking import (
    RankedCandidate,
    RankingComponent,
    RankingWeights,
    authority_signal_score,
)


@dataclass
class RankingCandidateInput:
    """Normalized inputs consumed by the ranking service."""

    candidate: str
    graph_depth: int | None = None
    semantic_score: float = 0.0
    authority: str = ""
    packet_priority: float = 0.0
    metadata: dict[str, object] = field(default_factory=dict)


def rank_candidates(
    candidates: list[RankingCandidateInput],
    weights: RankingWeights | None = None,
) -> list[RankedCandidate]:
    """Return candidates ranked by deterministic weighted scoring."""
    active_weights = weights or RankingWeights()
    ranked: list[RankedCandidate] = []

    for candidate in candidates:
        graph_score = graph_distance_score(candidate.graph_depth)
        semantic_score = _clamp_score(candidate.semantic_score)
        authority_score = authority_signal_score(candidate.authority)
        packet_score = _clamp_score(candidate.packet_priority)

        components = [
            RankingComponent(
                signal_id="graph_distance",
                raw_score=graph_score,
                weight=active_weights.graph_distance,
                weighted_score=graph_score * active_weights.graph_distance,
                detail={"graph_depth": candidate.graph_depth},
            ),
            RankingComponent(
                signal_id="semantic_similarity",
                raw_score=semantic_score,
                weight=active_weights.semantic_similarity,
                weighted_score=semantic_score * active_weights.semantic_similarity,
            ),
            RankingComponent(
                signal_id="authority",
                raw_score=authority_score,
                weight=active_weights.authority,
                weighted_score=authority_score * active_weights.authority,
                detail={"authority": candidate.authority or "unknown"},
            ),
            RankingComponent(
                signal_id="packet_priority",
                raw_score=packet_score,
                weight=active_weights.packet_priority,
                weighted_score=packet_score * active_weights.packet_priority,
            ),
        ]

        total_score = sum(component.weighted_score for component in components)
        ranked.append(
            RankedCandidate(
                candidate=candidate.candidate,
                total_score=total_score,
                components=components,
                metadata=dict(candidate.metadata),
            )
        )

    return sorted(ranked, key=lambda item: (-item.total_score, item.candidate))


def graph_distance_score(graph_depth: int | None) -> float:
    """Convert graph hop depth into a normalized score in [0, 1]."""
    if graph_depth is None or graph_depth < 0:
        return 0.0
    return 1.0 / (1.0 + float(graph_depth))


def _clamp_score(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value
