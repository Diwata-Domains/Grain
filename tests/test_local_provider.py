"""Tests for the local semantic provider."""

from grain.adapters.manifest import GrainConfig
from grain.services.embedding_resolver import EmbeddingProviderResolver
from grain.services.local_provider import LocalProvider


class _FakeModel:
    def encode(self, texts: list[str]) -> list[list[float]]:
        embeddings = {
            "auth middleware": [1.0, 0.0],
            "auth token middleware": [0.9, 0.1],
            "middleware auth checks": [0.8, 0.2],
            "database migrations": [0.0, 1.0],
        }
        return [embeddings[text] for text in texts]


def test_local_provider_scores_by_embedding_similarity():
    provider = LocalProvider(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_loader=lambda model_name: _FakeModel(),
    )

    ranked = provider.score(
        "auth middleware",
        ["middleware auth checks", "database migrations", "auth token middleware"],
    )

    assert [item.candidate for item in ranked] == [
        "auth token middleware",
        "middleware auth checks",
        "database migrations",
    ]
    assert ranked[0].provider_id == "local"


def test_local_provider_reports_unavailable_when_dependency_is_missing():
    provider = LocalProvider(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_loader=lambda model_name: (_ for _ in ()).throw(ImportError("sentence_transformers missing")),
    )

    status = provider.describe_status()

    assert status.provider_id == "local"
    assert status.available is False
    assert "sentence_transformers missing" in status.detail


def test_resolver_uses_built_in_local_factory_when_available(monkeypatch):
    monkeypatch.setattr(
        "grain.services.embedding_resolver._build_local_provider",
        lambda config: LocalProvider(
            model_name=config.local_embedding_model,
            model_loader=lambda model_name: _FakeModel(),
        ),
    )

    resolver = EmbeddingProviderResolver()
    provider, resolved = resolver.resolve_config(
        GrainConfig(
            embedding_provider="local",
            local_embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        )
    )

    assert provider.provider_id == "local"
    assert resolved.active_provider == "local"
    assert resolved.fallback_active is False
