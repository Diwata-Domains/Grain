# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""OpenAI-backed semantic scoring provider."""

from __future__ import annotations

import math
import os
from collections.abc import Callable
from importlib import import_module
from typing import Any

from grain.domain.embedding import EmbeddingProviderStatus, ScoredCandidate

ClientFactory = Callable[[str], Any]


class OpenAIProvider:
    """Semantic scoring provider backed by the OpenAI embeddings API."""

    provider_id = "openai"

    def __init__(
        self,
        model_name: str,
        api_key: str | None = None,
        client_factory: ClientFactory | None = None,
    ) -> None:
        self.model_name = model_name
        self.api_key = api_key if api_key is not None else os.getenv("GRAIN_OPENAI_API_KEY", "")
        self._client_factory = client_factory or _default_client_factory
        self._client: Any | None = None

    def score(self, query: str, candidates: list[str]) -> list[ScoredCandidate]:
        inputs = [query, *candidates]
        response = self._ensure_client().embeddings.create(model=self.model_name, input=inputs)
        embeddings = [[float(value) for value in item.embedding] for item in response.data]
        query_embedding = embeddings[0]
        ranked: list[ScoredCandidate] = []

        for candidate, embedding in zip(candidates, embeddings[1:], strict=False):
            ranked.append(
                ScoredCandidate(
                    candidate=candidate,
                    score=_cosine_similarity(query_embedding, embedding),
                    provider_id=self.provider_id,
                )
            )

        return sorted(ranked, key=lambda item: (-item.score, item.candidate))

    def describe_status(self) -> EmbeddingProviderStatus:
        if not self.api_key:
            return EmbeddingProviderStatus(
                provider_id=self.provider_id,
                model_name=self.model_name,
                available=False,
                detail="GRAIN_OPENAI_API_KEY is not set",
            )

        try:
            self._ensure_client()
        except Exception as exc:
            return EmbeddingProviderStatus(
                provider_id=self.provider_id,
                model_name=self.model_name,
                available=False,
                detail=str(exc),
            )

        return EmbeddingProviderStatus(
            provider_id=self.provider_id,
            model_name=self.model_name,
            available=True,
            detail="OpenAI client configured",
        )

    def _ensure_client(self) -> Any:
        if not self.api_key:
            raise RuntimeError("GRAIN_OPENAI_API_KEY is not set")
        if self._client is None:
            self._client = self._client_factory(self.api_key)
        return self._client


def _default_client_factory(api_key: str) -> Any:
    openai = import_module("openai")
    return openai.OpenAI(api_key=api_key)


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0

    numerator = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return numerator / (left_norm * right_norm)
