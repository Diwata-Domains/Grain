"""Tests for semantic-scoring provider resolution."""

from grain.adapters.manifest import GrainConfig
from grain.domain.embedding import EmbeddingProviderStatus
from grain.services.bm25_provider import BM25Provider
from grain.services.embedding_resolver import EmbeddingProviderResolver


class _FakeProvider:
    provider_id = "openai"
    model_name = "test-model"

    def score(self, query: str, candidates: list[str]) -> list:
        return []

    def describe_status(self) -> EmbeddingProviderStatus:
        return EmbeddingProviderStatus(
            provider_id=self.provider_id,
            model_name=self.model_name,
            available=True,
            detail="fake",
        )


def test_resolver_uses_bm25_by_default():
    resolver = EmbeddingProviderResolver()

    provider, resolved = resolver.resolve_config(GrainConfig())

    assert isinstance(provider, BM25Provider)
    assert provider.provider_id == "none"
    assert resolved.active_provider == "none"
    assert resolved.configured_model == "bm25"
    assert resolved.fallback_active is False


def test_resolver_falls_back_when_provider_factory_is_missing():
    resolver = EmbeddingProviderResolver()

    provider, resolved = resolver.resolve_config(
        GrainConfig(
            embedding_provider="ollama",
            ollama_embedding_model="custom-ollama-model",
        )
    )

    assert provider.provider_id == "none"
    assert resolved.configured_provider == "ollama"
    assert resolved.configured_model == "custom-ollama-model"
    assert resolved.fallback_active is True
    assert "not available" in resolved.fallback_reason


def test_resolver_uses_registered_factory_for_provider():
    resolver = EmbeddingProviderResolver(
        factories={"openai": lambda config: _FakeProvider()}
    )

    provider, resolved = resolver.resolve_config(
        GrainConfig(
            embedding_provider="openai",
            openai_embedding_model="text-embedding-3-large",
        )
    )

    assert provider.provider_id == "openai"
    assert resolved.active_provider == "openai"
    assert resolved.configured_model == "text-embedding-3-large"
    assert resolved.fallback_active is False


def test_resolver_fallback_provider_scores_deterministically():
    resolver = EmbeddingProviderResolver()
    provider, _ = resolver.resolve_config(GrainConfig())

    assert isinstance(provider, BM25Provider)
    ranked = provider.score(
        "auth middleware",
        ["middleware auth checks", "database migrations", "auth token middleware"],
    )

    assert [item.candidate for item in ranked] == [
        "auth token middleware",
        "middleware auth checks",
        "database migrations",
    ]
    assert ranked[0].score >= ranked[1].score >= ranked[2].score
