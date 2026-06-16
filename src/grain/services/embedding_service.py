# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Service helpers for embedding-provider inspection."""

from __future__ import annotations

from pathlib import Path

from grain.cli.output import CommandResult
from grain.domain.embedding import ResolvedEmbeddingProvider
from grain.services.embedding_resolver import EmbeddingProviderResolver


def inspect_embedding_provider(
    root: Path,
    resolver: EmbeddingProviderResolver | None = None,
) -> tuple[CommandResult, ResolvedEmbeddingProvider]:
    """Resolve and return the active embedding provider state for a repo."""
    active_resolver = resolver or EmbeddingProviderResolver()
    _, resolved = active_resolver.resolve_root(root)
    return CommandResult(
        ok=True,
        command="embedding show",
        repo=str(root),
    ), resolved
