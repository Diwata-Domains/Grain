# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Resolver for semantic-scoring provider configuration."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from grain.adapters.manifest import GrainConfig, load_grain_config
from grain.domain.embedding import (
    DEFAULT_BM25_MODEL,
    EmbeddingProvider,
    ResolvedEmbeddingProvider,
)
from grain.services.bm25_provider import BM25Provider
from grain.services.local_provider import LocalProvider
from grain.services.ollama_provider import OllamaProvider
from grain.services.openai_provider import OpenAIProvider

ProviderFactory = Callable[[GrainConfig], EmbeddingProvider]


def _build_ollama_provider(config: GrainConfig) -> EmbeddingProvider:
    provider = OllamaProvider(model_name=config.ollama_embedding_model)
    status = provider.describe_status()
    if not status.available:
        raise RuntimeError(status.detail or "Ollama provider is unavailable")
    return provider


def _build_local_provider(config: GrainConfig) -> EmbeddingProvider:
    provider = LocalProvider(model_name=config.local_embedding_model)
    status = provider.describe_status()
    if not status.available:
        raise RuntimeError(status.detail or "Local provider is unavailable")
    return provider


def _build_openai_provider(config: GrainConfig) -> EmbeddingProvider:
    provider = OpenAIProvider(model_name=config.openai_embedding_model)
    status = provider.describe_status()
    if not status.available:
        raise RuntimeError(status.detail or "OpenAI provider is unavailable")
    return provider


class EmbeddingProviderResolver:
    """Resolve the configured semantic-scoring provider with BM25 fallback."""

    def __init__(self, factories: dict[str, ProviderFactory] | None = None):
        self._factories: dict[str, ProviderFactory] = {
            "ollama": _build_ollama_provider,
            "local": _build_local_provider,
            "openai": _build_openai_provider,
            **dict(factories or {}),
        }

    def resolve_root(self, root: Path) -> tuple[EmbeddingProvider, ResolvedEmbeddingProvider]:
        return self.resolve_config(load_grain_config(root))

    def resolve_config(self, config: GrainConfig) -> tuple[EmbeddingProvider, ResolvedEmbeddingProvider]:
        configured_provider = config.embedding_provider
        configured_model = _configured_model(config, configured_provider)

        if configured_provider == "none":
            provider = BM25Provider()
            return provider, ResolvedEmbeddingProvider(
                configured_provider=configured_provider,
                active_provider=provider.provider_id,
                configured_model=configured_model,
                active_model=provider.model_name,
                provider_status=provider.describe_status(),
            )

        factory = self._factories.get(configured_provider)
        if factory is None:
            return self._fallback_resolution(
                configured_provider=configured_provider,
                configured_model=configured_model,
                reason=f"provider '{configured_provider}' is not available in this build",
            )

        try:
            provider = factory(config)
        except Exception as exc:
            return self._fallback_resolution(
                configured_provider=configured_provider,
                configured_model=configured_model,
                reason=f"provider '{configured_provider}' failed to initialize: {exc}",
            )

        return provider, ResolvedEmbeddingProvider(
            configured_provider=configured_provider,
            active_provider=provider.provider_id,
            configured_model=configured_model,
            active_model=provider.model_name,
            fallback_active=(provider.provider_id != configured_provider),
            fallback_reason=(
                "" if provider.provider_id == configured_provider else
                f"provider '{configured_provider}' resolved to '{provider.provider_id}'"
            ),
            provider_status=provider.describe_status(),
        )

    def _fallback_resolution(
        self,
        *,
        configured_provider: str,
        configured_model: str,
        reason: str,
    ) -> tuple[EmbeddingProvider, ResolvedEmbeddingProvider]:
        provider = BM25Provider()
        return provider, ResolvedEmbeddingProvider(
            configured_provider=configured_provider,
            active_provider=provider.provider_id,
            configured_model=configured_model,
            active_model=provider.model_name,
            fallback_active=True,
            fallback_reason=f"{reason}; falling back to {provider.model_name}",
            provider_status=provider.describe_status(),
        )


def _configured_model(config: GrainConfig, provider_id: str) -> str:
    if provider_id == "ollama":
        return config.ollama_embedding_model
    if provider_id == "local":
        return config.local_embedding_model
    if provider_id == "openai":
        return config.openai_embedding_model
    return DEFAULT_BM25_MODEL
