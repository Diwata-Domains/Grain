"""Tests for proposal-only task advice helpers."""

from pathlib import Path

from grain.domain.embedding import EmbeddingProviderStatus
from grain.services.task_advice_service import advise_next_tasks


class _FakeProvider:
    provider_id = "openai"
    model_name = "semantic-test"

    def score(self, query: str, candidates: list[str]) -> list:
        ranked = []
        for candidate in candidates:
            score = 0.1
            if "P17-T04" in candidate:
                score = 0.9
            elif "P17-T06" in candidate:
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


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_advise_next_tasks_ranks_current_phase_eligible_tasks(tmp_path: Path):
    _write(
        tmp_path / "docs" / "working" / "current_focus.md",
        "# Current Focus\n\n## Current Phase\nPhase 17 — Ranking and Decision Layer\n",
    )
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 20. Phase 17 — Ranking and Decision Layer\n\n"
            "### P17-T04 — Add ranked next-task advisory signals\n"
            "- **Status:** draft\n\n"
            "### P17-T05 — Add ranked impacted-file advisory signals\n"
            "- **Status:** done\n\n"
            "### P17-T06 — Phase 17 integration tests\n"
            "- **Status:** draft\n"
        ),
    )

    payload = advise_next_tasks(
        tmp_path,
        "rank next-task suggestions",
        embedding_resolver=_Resolver(),
    )

    assert payload["phase"] == "17"
    assert payload["candidate_pool_status"] == "draft"
    assert [item["task_ref"] for item in payload["ranked_tasks"]] == [
        "P17-T04",
        "P17-T06",
    ]
    assert any(
        component["signal_id"] == "semantic_similarity"
        for component in payload["ranked_tasks"][0]["components"]
    )


def test_advise_next_tasks_prefers_ready_pool_when_present(tmp_path: Path):
    _write(
        tmp_path / "docs" / "working" / "current_focus.md",
        "# Current Focus\n\n## Current Phase\nPhase 17 — Ranking and Decision Layer\n",
    )
    _write(
        tmp_path / "docs" / "working" / "backlog.md",
        (
            "## 20. Phase 17 — Ranking and Decision Layer\n\n"
            "### P17-T04 — Add ranked next-task advisory signals\n"
            "- **Status:** ready\n\n"
            "### P17-T06 — Phase 17 integration tests\n"
            "- **Status:** draft\n"
        ),
    )

    payload = advise_next_tasks(
        tmp_path,
        "rank next-task suggestions",
        embedding_resolver=_Resolver(),
    )

    assert payload["candidate_pool_status"] == "ready"
    assert [item["task_ref"] for item in payload["ranked_tasks"]] == ["P17-T04"]
