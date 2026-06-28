# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""Domain contracts for semantic-scoring providers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

EMBEDDING_PROVIDER_IDS: tuple[str, ...] = ("none", "ollama", "local", "openai")

DEFAULT_BM25_MODEL = "bm25"
DEFAULT_OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"
DEFAULT_LOCAL_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"


@dataclass
class ScoredCandidate:
    """One scored semantic candidate returned by an embedding provider."""

    candidate: str
    score: float
    provider_id: str
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class EmbeddingProviderStatus:
    """Availability and runtime details for one provider."""

    provider_id: str
    model_name: str
    available: bool
    detail: str = ""


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Protocol implemented by semantic-scoring providers."""

    provider_id: str
    model_name: str

    def score(self, query: str, candidates: list[str]) -> list[ScoredCandidate]:
        """Return ranked candidates for a semantic-scoring query."""
        ...

    def describe_status(self) -> EmbeddingProviderStatus:
        """Return the provider's availability and runtime details."""
        ...


@dataclass
class ResolvedEmbeddingProvider:
    """Resolved provider selection after config and fallback rules are applied."""

    configured_provider: str
    active_provider: str
    configured_model: str
    active_model: str
    fallback_active: bool = False
    fallback_reason: str = ""
    provider_status: EmbeddingProviderStatus | None = None

