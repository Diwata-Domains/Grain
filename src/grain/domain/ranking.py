"""Domain contracts for deterministic ranking and score breakdowns."""

from __future__ import annotations

from dataclasses import dataclass, field

RANK_SIGNAL_IDS: tuple[str, ...] = (
    "graph_distance",
    "semantic_similarity",
    "authority",
    "packet_priority",
)

DEFAULT_RANKING_WEIGHTS: dict[str, float] = {
    "graph_distance": 0.35,
    "semantic_similarity": 0.35,
    "authority": 0.20,
    "packet_priority": 0.10,
}

AUTHORITY_SIGNAL_SCORES: dict[str, float] = {
    "advisory": 0.20,
    "informational": 0.35,
    "secondary": 0.55,
    "high_runtime": 0.75,
    "highest_runtime": 0.90,
    "highest": 1.00,
}


@dataclass
class RankingComponent:
    """One inspectable score component contributing to a final rank."""

    signal_id: str
    raw_score: float
    weight: float
    weighted_score: float
    detail: dict[str, object] = field(default_factory=dict)


@dataclass
class RankedCandidate:
    """A deterministically ranked candidate with full score breakdown."""

    candidate: str
    total_score: float
    components: list[RankingComponent]
    metadata: dict[str, object] = field(default_factory=dict)

    def component(self, signal_id: str) -> RankingComponent | None:
        """Return one component by signal_id, or None when absent."""
        for component in self.components:
            if component.signal_id == signal_id:
                return component
        return None


@dataclass
class RankingWeights:
    """Weights applied by the ranking service to each supported signal."""

    graph_distance: float = DEFAULT_RANKING_WEIGHTS["graph_distance"]
    semantic_similarity: float = DEFAULT_RANKING_WEIGHTS["semantic_similarity"]
    authority: float = DEFAULT_RANKING_WEIGHTS["authority"]
    packet_priority: float = DEFAULT_RANKING_WEIGHTS["packet_priority"]

    def as_dict(self) -> dict[str, float]:
        """Return weight values keyed by signal id."""
        return {
            "graph_distance": self.graph_distance,
            "semantic_similarity": self.semantic_similarity,
            "authority": self.authority,
            "packet_priority": self.packet_priority,
        }

    def total_weight(self) -> float:
        """Return the sum of all configured weights."""
        return round(sum(self.as_dict().values()), 12)


def authority_signal_score(authority: str) -> float:
    """Return the normalized authority score for one document authority level."""
    return AUTHORITY_SIGNAL_SCORES.get(authority, 0.0)
