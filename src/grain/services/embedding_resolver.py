"""Resolver for semantic-scoring provider configuration."""

from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Callable
from pathlib import Path

from grain.adapters.manifest import GrainConfig, load_grain_config
from grain.domain.embedding import (
    DEFAULT_BM25_MODEL,
    DEFAULT_LOCAL_EMBEDDING_MODEL,
    DEFAULT_OLLAMA_EMBEDDING_MODEL,
    DEFAULT_OPENAI_EMBEDDING_MODEL,
    EmbeddingProvider,
    EmbeddingProviderStatus,
    ResolvedEmbeddingProvider,
    ScoredCandidate,
)

ProviderFactory = Callable[[GrainConfig], EmbeddingProvider]
_TOKEN_RE = re.compile(r"[a-z0-9]+")


class _BM25FallbackProvider:
    """Deterministic lexical fallback used until richer providers are available."""

    provider_id = "none"
    model_name = DEFAULT_BM25_MODEL

    def score(self, query: str, candidates: list[str]) -> list[ScoredCandidate]:
        query_terms = Counter(_tokenize(query))
        ranked: list[ScoredCandidate] = []

        for candidate in candidates:
            doc_terms = Counter(_tokenize(candidate))
            overlap = sorted(set(query_terms) & set(doc_terms))
            score = _lexical_score(query_terms, doc_terms)
            ranked.append(
                ScoredCandidate(
                    candidate=candidate,
                    score=score,
                    provider_id=self.provider_id,
                    metadata={"matched_terms": overlap},
                )
            )

        return sorted(
            ranked,
            key=lambda item: (-item.score, item.candidate),
        )

    def describe_status(self) -> EmbeddingProviderStatus:
        return EmbeddingProviderStatus(
            provider_id=self.provider_id,
            model_name=self.model_name,
            available=True,
            detail="deterministic lexical fallback",
        )


class EmbeddingProviderResolver:
    """Resolve the configured semantic-scoring provider with BM25 fallback."""

    def __init__(self, factories: dict[str, ProviderFactory] | None = None):
        self._factories: dict[str, ProviderFactory] = dict(factories or {})

    def resolve_root(self, root: Path) -> tuple[EmbeddingProvider, ResolvedEmbeddingProvider]:
        return self.resolve_config(load_grain_config(root))

    def resolve_config(self, config: GrainConfig) -> tuple[EmbeddingProvider, ResolvedEmbeddingProvider]:
        configured_provider = config.embedding_provider
        configured_model = _configured_model(config, configured_provider)

        if configured_provider == "none":
            provider = _BM25FallbackProvider()
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
        provider = _BM25FallbackProvider()
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


def _tokenize(value: str) -> list[str]:
    return _TOKEN_RE.findall(value.lower())


def _lexical_score(query_terms: Counter[str], doc_terms: Counter[str]) -> float:
    if not query_terms or not doc_terms:
        return 0.0

    score = 0.0
    for term, qfreq in query_terms.items():
        if term not in doc_terms:
            continue
        score += qfreq * (1.0 + math.log1p(doc_terms[term]))

    return score / (1.0 + math.log1p(sum(doc_terms.values())))
