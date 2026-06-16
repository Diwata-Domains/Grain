# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Ollama-backed semantic scoring provider."""

from __future__ import annotations

import json
import math
from collections.abc import Callable
from urllib import error, request

from grain.domain.embedding import (
    EmbeddingProviderStatus,
    ScoredCandidate,
)

EmbeddingRequest = Callable[[str], list[float]]


class OllamaProvider:
    """Semantic scoring provider backed by a local Ollama server."""

    provider_id = "ollama"

    def __init__(
        self,
        model_name: str,
        base_url: str = "http://localhost:11434",
        embedding_request: EmbeddingRequest | None = None,
    ) -> None:
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self._embedding_request = embedding_request or self._request_embedding

    def score(self, query: str, candidates: list[str]) -> list[ScoredCandidate]:
        query_embedding = self._embedding_request(query)
        ranked: list[ScoredCandidate] = []

        for candidate in candidates:
            candidate_embedding = self._embedding_request(candidate)
            ranked.append(
                ScoredCandidate(
                    candidate=candidate,
                    score=_cosine_similarity(query_embedding, candidate_embedding),
                    provider_id=self.provider_id,
                )
            )

        return sorted(ranked, key=lambda item: (-item.score, item.candidate))

    def describe_status(self) -> EmbeddingProviderStatus:
        try:
            self._embedding_request("status probe")
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
            detail="reachable local Ollama embedding server",
        )

    def _request_embedding(self, text: str) -> list[float]:
        payload = json.dumps({"model": self.model_name, "prompt": text}).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/api/embeddings",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=2.0) as response:
                data = json.loads(response.read().decode("utf-8"))
        except error.URLError as exc:
            raise RuntimeError(f"Ollama server unavailable at {self.base_url}: {exc.reason}") from exc

        embedding = data.get("embedding")
        if not isinstance(embedding, list) or not embedding:
            raise RuntimeError("Ollama response did not include a usable embedding vector")
        return [float(value) for value in embedding]


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0

    numerator = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return numerator / (left_norm * right_norm)
