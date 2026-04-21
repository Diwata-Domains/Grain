"""Tests for semantic-scoring domain contracts."""

from grain.domain.embedding import (
    DEFAULT_BM25_MODEL,
    EmbeddingProviderStatus,
    ResolvedEmbeddingProvider,
    ScoredCandidate,
)


def test_scored_candidate_defaults_metadata_to_distinct_dicts():
    first = ScoredCandidate(candidate="a.py", score=0.8, provider_id="none")
    second = ScoredCandidate(candidate="b.py", score=0.1, provider_id="none")

    first.metadata["matched_terms"] = ["auth"]

    assert second.metadata == {}


def test_resolved_embedding_provider_preserves_resolution_fields():
    status = EmbeddingProviderStatus(
        provider_id="none",
        model_name=DEFAULT_BM25_MODEL,
        available=True,
    )
    resolved = ResolvedEmbeddingProvider(
        configured_provider="openai",
        active_provider="none",
        configured_model="text-embedding-3-small",
        active_model=DEFAULT_BM25_MODEL,
        fallback_active=True,
        fallback_reason="missing API key",
        provider_status=status,
    )

    assert resolved.configured_provider == "openai"
    assert resolved.active_provider == "none"
    assert resolved.fallback_active is True
    assert resolved.provider_status is status
