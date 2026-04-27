"""Tests for the OpenAI semantic provider."""

from grain.adapters.manifest import GrainConfig
from grain.services.embedding_resolver import EmbeddingProviderResolver
from grain.services.openai_provider import OpenAIProvider


class _FakeEmbeddingsAPI:
    def create(self, *, model: str, input: list[str]):
        embeddings = {
            "auth middleware": [1.0, 0.0],
            "auth token middleware": [0.9, 0.1],
            "middleware auth checks": [0.8, 0.2],
            "database migrations": [0.0, 1.0],
        }

        class _Item:
            def __init__(self, embedding):
                self.embedding = embedding

        class _Response:
            def __init__(self, data):
                self.data = data

        return _Response([_Item(embeddings[text]) for text in input])


class _FakeClient:
    def __init__(self):
        self.embeddings = _FakeEmbeddingsAPI()


def test_openai_provider_scores_by_embedding_similarity():
    provider = OpenAIProvider(
        model_name="text-embedding-3-small",
        api_key="test-key",
        client_factory=lambda api_key: _FakeClient(),
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
    assert ranked[0].provider_id == "openai"


def test_openai_provider_reports_unavailable_without_api_key():
    provider = OpenAIProvider(model_name="text-embedding-3-small", api_key="")

    status = provider.describe_status()

    assert status.provider_id == "openai"
    assert status.available is False
    assert "GRAIN_OPENAI_API_KEY" in status.detail


def test_resolver_uses_built_in_openai_factory_when_available(monkeypatch):
    monkeypatch.setattr(
        "grain.services.embedding_resolver._build_openai_provider",
        lambda config: OpenAIProvider(
            model_name=config.openai_embedding_model,
            api_key="test-key",
            client_factory=lambda api_key: _FakeClient(),
        ),
    )

    resolver = EmbeddingProviderResolver()
    provider, resolved = resolver.resolve_config(
        GrainConfig(
            embedding_provider="openai",
            openai_embedding_model="text-embedding-3-small",
        )
    )

    assert provider.provider_id == "openai"
    assert resolved.active_provider == "openai"
    assert resolved.fallback_active is False
