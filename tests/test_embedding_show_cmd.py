"""Tests for `grain embedding show`."""

import json

from click.testing import CliRunner

from grain.cli import main
from grain.cli.output import CommandResult
from grain.domain.embedding import EmbeddingProviderStatus, ResolvedEmbeddingProvider


def _resolved(
    *,
    configured_provider: str = "openai",
    active_provider: str = "none",
    configured_model: str = "text-embedding-3-small",
    active_model: str = "bm25",
    fallback_active: bool = True,
    fallback_reason: str = "provider 'openai' failed; falling back to bm25",
    available: bool = True,
    detail: str = "deterministic lexical scoring baseline",
) -> ResolvedEmbeddingProvider:
    return ResolvedEmbeddingProvider(
        configured_provider=configured_provider,
        active_provider=active_provider,
        configured_model=configured_model,
        active_model=active_model,
        fallback_active=fallback_active,
        fallback_reason=fallback_reason,
        provider_status=EmbeddingProviderStatus(
            provider_id=active_provider,
            model_name=active_model,
            available=available,
            detail=detail,
        ),
    )


def test_embedding_show_text_output(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "grain.cli.embedding.inspect_embedding_provider",
        lambda root: (CommandResult(ok=True, command="embedding show", repo=str(root)), _resolved()),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "embedding", "show"])

    assert result.exit_code == 0, result.output
    assert "embedding show: ok" in result.output
    assert "configured_provider  openai" in result.output
    assert "active_provider      none" in result.output
    assert "fallback_active      yes" in result.output
    assert "available            yes" in result.output


def test_embedding_show_json_output(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "grain.cli.embedding.inspect_embedding_provider",
        lambda root: (
            CommandResult(ok=True, command="embedding show", repo=str(root)),
            _resolved(active_provider="local", active_model="mini", fallback_active=False, fallback_reason=""),
        ),
    )

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "--format", "json", "embedding", "show"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["embedding"]["configured_provider"] == "openai"
    assert data["embedding"]["active_provider"] == "local"
    assert data["embedding"]["fallback_active"] is False
    assert data["embedding"]["provider_status"]["available"] is True
