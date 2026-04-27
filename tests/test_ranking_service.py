"""Tests for the deterministic ranking service."""

from grain.domain.ranking import RankingWeights
from grain.services.ranking_service import (
    RankingCandidateInput,
    graph_distance_score,
    rank_candidates,
)


def test_graph_distance_score_prefers_nearer_candidates():
    assert graph_distance_score(0) == 1.0
    assert graph_distance_score(1) > graph_distance_score(2)
    assert graph_distance_score(None) == 0.0
    assert graph_distance_score(-1) == 0.0


def test_rank_candidates_combines_all_signals_deterministically():
    ranked = rank_candidates(
        [
            RankingCandidateInput(
                candidate="tests/test_auth.py",
                graph_depth=1,
                semantic_score=0.6,
                authority="secondary",
                packet_priority=0.5,
            ),
            RankingCandidateInput(
                candidate="src/auth.py",
                graph_depth=0,
                semantic_score=0.8,
                authority="highest",
                packet_priority=1.0,
            ),
            RankingCandidateInput(
                candidate="docs/notes.md",
                graph_depth=3,
                semantic_score=0.2,
                authority="informational",
                packet_priority=0.0,
            ),
        ]
    )

    assert [item.candidate for item in ranked] == [
        "src/auth.py",
        "tests/test_auth.py",
        "docs/notes.md",
    ]
    assert ranked[0].component("graph_distance") is not None
    assert ranked[0].component("semantic_similarity") is not None
    assert ranked[0].component("authority") is not None
    assert ranked[0].component("packet_priority") is not None


def test_rank_candidates_breaks_ties_by_candidate_name():
    ranked = rank_candidates(
        [
            RankingCandidateInput(candidate="b.py"),
            RankingCandidateInput(candidate="a.py"),
        ],
        weights=RankingWeights(
            graph_distance=0.0,
            semantic_similarity=0.0,
            authority=0.0,
            packet_priority=0.0,
        ),
    )

    assert [item.candidate for item in ranked] == ["a.py", "b.py"]


def test_rank_candidates_clamps_semantic_and_packet_scores():
    ranked = rank_candidates(
        [
            RankingCandidateInput(
                candidate="src/auth.py",
                semantic_score=4.2,
                packet_priority=-1.0,
            )
        ]
    )

    semantic = ranked[0].component("semantic_similarity")
    packet = ranked[0].component("packet_priority")

    assert semantic is not None
    assert packet is not None
    assert semantic.raw_score == 1.0
    assert packet.raw_score == 0.0
