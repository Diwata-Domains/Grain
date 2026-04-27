"""Phase 17 integration coverage."""

from __future__ import annotations

from pathlib import Path

import yaml

from grain.domain.embedding import EmbeddingProviderStatus, ScoredCandidate
from grain.services.context_service import build_context_bundle
from grain.services.orchestration_service import analyze_scope_signals
from grain.services.task_advice_service import advise_next_tasks
from grain.services.task_service import create_packet_directory


class _RankedProvider:
    def __init__(self, provider_id: str, model_name: str) -> None:
        self.provider_id = provider_id
        self.model_name = model_name

    def score(self, query: str, candidates: list[str]) -> list[ScoredCandidate]:
        ranked: list[ScoredCandidate] = []
        for candidate in candidates:
            score = 0.1
            if "P17-T04" in candidate or "src/auth_middleware.py" in candidate:
                score = 0.95
            elif "P17-T06" in candidate or "tests/test_auth.py" in candidate:
                score = 0.55
            elif "src/database.py" in candidate:
                score = 0.2
            ranked.append(
                ScoredCandidate(
                    candidate=candidate,
                    score=score,
                    provider_id=self.provider_id,
                )
            )
        return sorted(ranked, key=lambda item: (-item.score, item.candidate))

    def describe_status(self) -> EmbeddingProviderStatus:
        return EmbeddingProviderStatus(
            provider_id=self.provider_id,
            model_name=self.model_name,
            available=True,
            detail=f"{self.provider_id} ready",
        )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_manifest(repo_root, embedding_provider="openai", model_name="semantic-test"):
    manifest = {
        "canonical": [
            {
                "id": "workflow_spec",
                "path": "docs/canonical/workflow_spec.md",
                "purpose": "Workflow guidance",
                "authority": "highest",
                "editable_by_agents": False,
                "read_when": ["running_tasks"],
            }
        ],
        "working": [],
        "runtime": [],
        "tasks": {},
        "rules": {},
        "grain": {
            "embedding_provider": embedding_provider,
            "ollama_embedding_model": model_name,
            "local_embedding_model": model_name,
            "openai_embedding_model": model_name,
        },
    }
    manifest_path = repo_root / "docs" / "runtime" / "docs_manifest.yaml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(yaml.dump(manifest), encoding="utf-8")


def _write_adapter_profiles(repo_root):
    _write(
        repo_root / "docs" / "runtime" / "adapter_profiles.md",
        """# Adapter Profiles

## 5. Adapter Profiles

### code_adapter
- `adapter_id`: `code_adapter`
- `domain_type`: `code`
- `applies_to`:
  - python
  - backend
  - cli
- `relevant_file_patterns`:
  - `src/**`
  - `tests/**`
- `context_priority_rules`:
  - prioritize touched source files, then nearby tests
- `test_or_validation_hints`:
  - run focused tests before full suite
- `review_focus_hints`:
  - behavior regressions
""",
    )


def _write_current_focus(repo_root):
    _write(
        repo_root / "docs" / "working" / "current_focus.md",
        "# Current Focus\n\n## Current Phase\nPhase 17 — Ranking and Decision Layer\n",
    )


def _write_phase17_backlog(repo_root):
    _write(
        repo_root / "docs" / "working" / "backlog.md",
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


def _write_context_fixture(repo_root):
    _write(repo_root / "docs" / "canonical" / "workflow_spec.md", "# Workflow Spec\n")
    _write(
        repo_root / "src" / "auth_middleware.py",
        "def auth_middleware(request):\n    # auth middleware auth middleware\n    return request\n",
    )
    _write(repo_root / "src" / "database.py", "def run_migrations():\n    return True\n")
    _write(repo_root / "tests" / "test_auth.py", "def test_auth_middleware():\n    assert True\n")
    create_packet_directory(repo_root, phase=17, task_num=6)
    task_md = repo_root / "tasks" / "P17-T06-TASK-0001" / "task.md"
    task_md.write_text(
        """# Task: Improve auth middleware

## Metadata
- **ID:** TASK-0001
- **Status:** draft
- **Phase:** Phase 17
- **Backlog:** P17-T06
- **Packet Path:** tasks/P17-T06-TASK-0001/
- **Dependencies:** none
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
Improve auth middleware behavior in the auth middleware implementation and keep nearby auth tests aligned.

## Why This Task Exists
Task fixture.

## Scope
- update auth logic

## Constraints
- deterministic selection only

## Escalation Conditions
- none
""",
        encoding="utf-8",
    )


def _prepare_repo(repo_root):
    _write_manifest(repo_root)
    _write_adapter_profiles(repo_root)
    _write_current_focus(repo_root)
    _write_phase17_backlog(repo_root)
    _write_context_fixture(repo_root)


def _patch_provider(monkeypatch, provider_id="openai"):
    if provider_id == "openai":
        monkeypatch.setattr(
            "grain.services.embedding_resolver._build_openai_provider",
            lambda config: _RankedProvider("openai", config.openai_embedding_model),
        )
    elif provider_id == "local":
        monkeypatch.setattr(
            "grain.services.embedding_resolver._build_local_provider",
            lambda config: _RankedProvider("local", config.local_embedding_model),
        )


def test_phase17_context_selection_exposes_ranked_scores(packet_repo, monkeypatch):
    _prepare_repo(packet_repo)
    _patch_provider(monkeypatch, "openai")

    result, bundle = build_context_bundle(packet_repo, "TASK-0001")

    assert result.ok is True
    assert bundle is not None
    semantic = bundle.export_metadata["adapter_context"]["semantic_ranking"]
    assert semantic["active_provider"] == "openai"
    assert [item["path"] for item in semantic["ranked_scores"]] == [
        "src/auth_middleware.py",
        "tests/test_auth.py",
        "src/database.py",
    ]


def test_phase17_task_advice_ranks_eligible_phase_tasks(packet_repo, monkeypatch):
    _prepare_repo(packet_repo)
    _patch_provider(monkeypatch, "openai")

    payload = advise_next_tasks(packet_repo, "rank next-task suggestions")

    assert payload["candidate_pool_status"] == "draft"
    assert [item["task_ref"] for item in payload["ranked_tasks"]] == [
        "P17-T04",
        "P17-T06",
    ]


def test_phase17_orchestration_scope_exposes_task_and_impact_ranking(packet_repo, monkeypatch):
    _prepare_repo(packet_repo)
    _patch_provider(monkeypatch, "openai")

    result, payload = analyze_scope_signals(packet_repo, "add python cli and improve auth middleware")

    assert result.ok is True
    assert payload is not None
    assert payload["task_advice"]["ranked_tasks"][0]["task_ref"] == "P17-T04"
    impact = payload["adapter_signals"][0]["impact"]
    assert impact["ranking"]["active_provider"] == "openai"
    assert impact["ranking"]["ranked_affected_files"][0]["path"] == "src/auth_middleware.py"


def test_phase17_task_advice_uses_ready_pool_when_present(packet_repo, monkeypatch):
    _prepare_repo(packet_repo)
    _patch_provider(monkeypatch, "local")
    backlog_path = packet_repo / "docs" / "working" / "backlog.md"
    backlog_path.write_text(
        backlog_path.read_text(encoding="utf-8").replace(
            "- **Status:** draft",
            "- **Status:** ready",
            1,
        ),
        encoding="utf-8",
    )

    payload = advise_next_tasks(packet_repo, "rank next-task suggestions")

    assert payload["candidate_pool_status"] == "ready"
    assert [item["task_ref"] for item in payload["ranked_tasks"]] == ["P17-T04"]
