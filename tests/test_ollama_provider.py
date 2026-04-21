"""Tests for the Ollama semantic provider."""

from grain.adapters.manifest import GrainConfig
from grain.services.embedding_resolver import EmbeddingProviderResolver
from grain.services.ollama_provider import OllamaProvider


def test_ollama_provider_scores_by_embedding_similarity():
    embeddings = {
        "status probe": [1.0, 0.0],
        "auth middleware": [1.0, 0.0],
        "auth token middleware": [0.9, 0.1],
        "middleware auth checks": [0.8, 0.2],
        "database migrations": [0.0, 1.0],
    }
    provider = OllamaProvider(
        model_name="nomic-embed-text",
        embedding_request=lambda text: embeddings[text],
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
    assert ranked[0].provider_id == "ollama"


def test_ollama_provider_reports_unavailable_when_request_fails():
    provider = OllamaProvider(
        model_name="nomic-embed-text",
        embedding_request=lambda text: (_ for _ in ()).throw(RuntimeError("connection refused")),
    )

    status = provider.describe_status()

    assert status.provider_id == "ollama"
    assert status.available is False
    assert "connection refused" in status.detail


def test_resolver_uses_built_in_ollama_factory_when_available(monkeypatch):
    monkeypatch.setattr(
        "grain.services.embedding_resolver._build_ollama_provider",
        lambda config: OllamaProvider(
            model_name=config.ollama_embedding_model,
            embedding_request=lambda text: [1.0, 0.0],
        ),
    )

    resolver = EmbeddingProviderResolver()
    provider, resolved = resolver.resolve_config(
        GrainConfig(
            embedding_provider="ollama",
            ollama_embedding_model="nomic-embed-text",
        )
    )

    assert provider.provider_id == "ollama"
    assert resolved.active_provider == "ollama"
    assert resolved.fallback_active is False
