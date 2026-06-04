"""Tests for impacted-file ranking helpers."""

from grain.domain.embedding import EmbeddingProviderStatus
from grain.services.impact_ranking_service import rank_impacted_files


class _FakeProvider:
    provider_id = "openai"
    model_name = "semantic-test"

    def score(self, query: str, candidates: list[str]) -> list:
        ranked = []
        for candidate in candidates:
            score = 0.1
            if "src/a.py" in candidate:
                score = 0.9
            elif "src/b.py" in candidate:
                score = 0.4
            ranked.append(
                type(
                    "Score",
                    (),
                    {
                        "candidate": candidate,
                        "score": score,
                        "provider_id": self.provider_id,
                        "metadata": {},
                    },
                )()
            )
        return sorted(ranked, key=lambda item: (-item.score, item.candidate))

    def describe_status(self):
        return EmbeddingProviderStatus(
            provider_id=self.provider_id,
            model_name=self.model_name,
            available=True,
            detail="fake provider",
        )


class _Resolver:
    def resolve_root(self, root):
        provider = _FakeProvider()
        return provider, type(
            "Resolved",
            (),
            {
                "configured_provider": "openai",
                "active_provider": "openai",
                "configured_model": "semantic-test",
                "active_model": "semantic-test",
                "fallback_active": False,
                "fallback_reason": "",
                "provider_status": provider.describe_status(),
            },
        )()


def test_rank_impacted_files_returns_ranked_breakdowns(tmp_path):
    (tmp_path / "src").mkdir(parents=True, exist_ok=True)
    (tmp_path / "src" / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
    (tmp_path / "src" / "b.py").write_text("def b():\n    return 2\n", encoding="utf-8")

    ranking = rank_impacted_files(
        tmp_path,
        ["src/a.py"],
        ["src/a.py", "src/b.py"],
        embedding_resolver=_Resolver(),
    )

    assert ranking["active_provider"] == "openai"
    assert [item["path"] for item in ranking["ranked_affected_files"]] == [
        "src/a.py",
        "src/b.py",
    ]
    assert any(
        component["signal_id"] == "semantic_similarity"
        for component in ranking["ranked_affected_files"][0]["components"]
    )


def test_rank_impacted_files_returns_empty_payload_without_candidates(tmp_path):
    ranking = rank_impacted_files(tmp_path, ["src/a.py"], [])

    assert ranking == {}
