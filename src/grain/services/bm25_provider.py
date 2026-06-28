# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""Deterministic lexical scoring provider for semantic enrichment."""

from __future__ import annotations

import math
import re
from collections import Counter

from grain.domain.embedding import (
    DEFAULT_BM25_MODEL,
    EmbeddingProviderStatus,
    ScoredCandidate,
)

_TOKEN_RE = re.compile(r"[a-z0-9]+")


class BM25Provider:
    """Always-available baseline provider with deterministic lexical scoring."""

    provider_id = "none"
    model_name = DEFAULT_BM25_MODEL

    def score(self, query: str, candidates: list[str]) -> list[ScoredCandidate]:
        query_terms = Counter(_tokenize(query))
        ranked: list[ScoredCandidate] = []

        for candidate in candidates:
            doc_terms = Counter(_tokenize(candidate))
            overlap = sorted(set(query_terms) & set(doc_terms))
            ranked.append(
                ScoredCandidate(
                    candidate=candidate,
                    score=_lexical_score(query_terms, doc_terms),
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
            detail="deterministic lexical scoring baseline",
        )


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
