"""Tests for ranking domain contracts."""

from grain.domain.ranking import (
    AUTHORITY_SIGNAL_SCORES,
    DEFAULT_RANKING_WEIGHTS,
    RANK_SIGNAL_IDS,
    RankedCandidate,
    RankingComponent,
    RankingWeights,
    authority_signal_score,
)


def test_ranking_weights_default_total_is_one():
    weights = RankingWeights()

    assert weights.as_dict() == DEFAULT_RANKING_WEIGHTS
    assert weights.total_weight() == 1.0


def test_ranked_candidate_can_find_component_by_signal():
    candidate = RankedCandidate(
        candidate="src/auth.py",
        total_score=0.82,
        components=[
            RankingComponent(
                signal_id="graph_distance",
                raw_score=0.9,
                weight=0.35,
                weighted_score=0.315,
            ),
            RankingComponent(
                signal_id="authority",
                raw_score=1.0,
                weight=0.20,
                weighted_score=0.20,
            ),
        ],
    )

    authority = candidate.component("authority")

    assert authority is not None
    assert authority.raw_score == 1.0
    assert candidate.component("semantic_similarity") is None


def test_component_and_candidate_metadata_default_to_distinct_dicts():
    first = RankingComponent(
        signal_id="authority",
        raw_score=1.0,
        weight=0.2,
        weighted_score=0.2,
    )
    second = RankingComponent(
        signal_id="authority",
        raw_score=0.5,
        weight=0.2,
        weighted_score=0.1,
    )
    left = RankedCandidate(candidate="a", total_score=0.2, components=[first])
    right = RankedCandidate(candidate="b", total_score=0.1, components=[second])

    first.detail["authority"] = "highest"
    left.metadata["kind"] = "canonical"

    assert second.detail == {}
    assert right.metadata == {}


def test_authority_signal_score_preserves_expected_ordering():
    assert authority_signal_score("highest") == AUTHORITY_SIGNAL_SCORES["highest"]
    assert authority_signal_score("highest") > authority_signal_score("secondary")
    assert authority_signal_score("secondary") > authority_signal_score("advisory")
    assert authority_signal_score("unknown") == 0.0


def test_rank_signal_ids_match_default_weight_keys():
    assert set(RANK_SIGNAL_IDS) == set(DEFAULT_RANKING_WEIGHTS)
