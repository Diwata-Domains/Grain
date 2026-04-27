"""Tests for the deterministic BM25 provider."""

from grain.services.bm25_provider import BM25Provider


def test_bm25_provider_scores_candidates_deterministically():
    provider = BM25Provider()

    ranked = provider.score(
        "auth middleware",
        ["middleware auth checks", "database migrations", "auth token middleware"],
    )

    assert [item.candidate for item in ranked] == [
        "auth token middleware",
        "middleware auth checks",
        "database migrations",
    ]
    assert ranked[0].score >= ranked[1].score >= ranked[2].score
    assert ranked[0].provider_id == "none"


def test_bm25_provider_reports_available_status():
    provider = BM25Provider()

    status = provider.describe_status()

    assert status.provider_id == "none"
    assert status.model_name == "bm25"
    assert status.available is True
