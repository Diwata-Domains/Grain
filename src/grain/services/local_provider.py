# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""Sentence-transformers-backed semantic scoring provider."""

from __future__ import annotations

import math
from collections.abc import Callable
from importlib import import_module
from typing import Any

from grain.domain.embedding import EmbeddingProviderStatus, ScoredCandidate

ModelLoader = Callable[[str], Any]


class LocalProvider:
    """Semantic scoring provider backed by a local sentence-transformers model."""

    provider_id = "local"

    def __init__(
        self,
        model_name: str,
        model_loader: ModelLoader | None = None,
    ) -> None:
        self.model_name = model_name
        self._model_loader = model_loader or _default_model_loader
        self._model: Any | None = None

    def score(self, query: str, candidates: list[str]) -> list[ScoredCandidate]:
        embeddings = self._encode([query, *candidates])
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
        try:
            self._ensure_model()
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
            detail="local sentence-transformers model available",
        )

    def _ensure_model(self) -> Any:
        if self._model is None:
            self._model = self._model_loader(self.model_name)
        return self._model

    def _encode(self, texts: list[str]) -> list[list[float]]:
        raw_embeddings = self._ensure_model().encode(texts)
        return [[float(value) for value in embedding] for embedding in raw_embeddings]


def _default_model_loader(model_name: str) -> Any:
    sentence_transformers = import_module("sentence_transformers")
    return sentence_transformers.SentenceTransformer(model_name)


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0

    numerator = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return numerator / (left_norm * right_norm)
