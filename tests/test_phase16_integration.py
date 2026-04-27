"""Phase 16 integration coverage."""

from __future__ import annotations

import yaml

from grain.domain.embedding import EmbeddingProviderStatus, ScoredCandidate
from grain.services.context_service import build_context_bundle
from grain.services.embedding_service import inspect_embedding_provider
from grain.services.task_service import create_packet_directory


class _RankedProvider:
    def __init__(self, provider_id: str, model_name: str) -> None:
        self.provider_id = provider_id
        self.model_name = model_name

    def score(self, query: str, candidates: list[str]) -> list[ScoredCandidate]:
        ranked: list[ScoredCandidate] = []
        for candidate in candidates:
            score = 0.1
            if "src/auth_middleware.py" in candidate:
                score = 0.95
            elif "tests/test_auth.py" in candidate:
                score = 0.6
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


def _write_manifest(repo_root, embedding_provider="none", model_name="test-model"):
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
    path = repo_root / "docs" / "runtime" / "adapter_profiles.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """# Adapter Profiles

## 5. Adapter Profiles

### code_adapter
- `adapter_id`: `code_adapter`
- `domain_type`: `code`
- `applies_to`:
  - Python
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
        encoding="utf-8",
    )


def _write_context_fixture(repo_root):
    workflow_spec = repo_root / "docs" / "canonical" / "workflow_spec.md"
    workflow_spec.parent.mkdir(parents=True, exist_ok=True)
    workflow_spec.write_text("# Workflow Spec\n", encoding="utf-8")

    (repo_root / "src").mkdir(parents=True, exist_ok=True)
    (repo_root / "tests").mkdir(parents=True, exist_ok=True)
    (repo_root / "src" / "auth_middleware.py").write_text(
        (
            "def auth_middleware(request):\n"
            "    # auth middleware auth middleware\n"
            "    return request\n"
        ),
        encoding="utf-8",
    )
    (repo_root / "src" / "database.py").write_text(
        "def run_migrations():\n    return True\n",
        encoding="utf-8",
    )
    (repo_root / "tests" / "test_auth.py").write_text(
        "def test_auth_middleware():\n    assert True\n",
        encoding="utf-8",
    )

    create_packet_directory(repo_root, phase=16, task_num=8)
    task_md = repo_root / "tasks" / "P16-T08-TASK-0001" / "task.md"
    task_md.write_text(
        """# Task: Improve auth middleware

## Metadata
- **ID:** TASK-0001
- **Status:** draft
- **Phase:** Phase 16
- **Backlog:** P16-T08
- **Packet Path:** tasks/P16-T08-TASK-0001/
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


def _prepare_repo(repo_root, embedding_provider="none", model_name="test-model"):
    _write_manifest(repo_root, embedding_provider=embedding_provider, model_name=model_name)
    _write_adapter_profiles(repo_root)
    _write_context_fixture(repo_root)


def test_phase16_defaults_to_bm25_resolution(packet_repo):
    _prepare_repo(packet_repo, embedding_provider="none")

    result, resolved = inspect_embedding_provider(packet_repo)

    assert result.ok is True
    assert resolved.configured_provider == "none"
    assert resolved.active_provider == "none"
    assert resolved.fallback_active is False


def test_phase16_falls_back_cleanly_when_ollama_is_unavailable(packet_repo, monkeypatch):
    _prepare_repo(packet_repo, embedding_provider="ollama", model_name="nomic-embed-text")
    monkeypatch.setattr(
        "grain.services.embedding_resolver._build_ollama_provider",
        lambda config: (_ for _ in ()).throw(RuntimeError("offline")),
    )

    _, resolved = inspect_embedding_provider(packet_repo)

    assert resolved.configured_provider == "ollama"
    assert resolved.active_provider == "none"
    assert resolved.fallback_active is True
    assert "offline" in resolved.fallback_reason


def test_phase16_uses_local_provider_when_available(packet_repo, monkeypatch):
    _prepare_repo(packet_repo, embedding_provider="local", model_name="mini-local")
    monkeypatch.setattr(
        "grain.services.embedding_resolver._build_local_provider",
        lambda config: _RankedProvider("local", config.local_embedding_model),
    )

    _, resolved = inspect_embedding_provider(packet_repo)

    assert resolved.active_provider == "local"
    assert resolved.active_model == "mini-local"
    assert resolved.fallback_active is False


def test_phase16_uses_openai_provider_when_available(packet_repo, monkeypatch):
    _prepare_repo(packet_repo, embedding_provider="openai", model_name="text-embedding-3-small")
    monkeypatch.setattr(
        "grain.services.embedding_resolver._build_openai_provider",
        lambda config: _RankedProvider("openai", config.openai_embedding_model),
    )

    _, resolved = inspect_embedding_provider(packet_repo)

    assert resolved.active_provider == "openai"
    assert resolved.active_model == "text-embedding-3-small"
    assert resolved.fallback_active is False


def test_phase16_context_selection_records_bm25_semantic_metadata(packet_repo):
    _prepare_repo(packet_repo, embedding_provider="none")

    result, bundle = build_context_bundle(packet_repo, "TASK-0001")

    assert result.ok is True
    assert bundle is not None
    semantic = bundle.export_metadata["adapter_context"]["semantic_ranking"]
    assert semantic["active_provider"] == "none"
    assert semantic["fallback_active"] is False
    assert semantic["scores"][0]["path"] == "src/auth_middleware.py"


def test_phase16_context_selection_uses_ollama_provider(packet_repo, monkeypatch):
    _prepare_repo(packet_repo, embedding_provider="ollama", model_name="nomic-embed-text")
    monkeypatch.setattr(
        "grain.services.embedding_resolver._build_ollama_provider",
        lambda config: _RankedProvider("ollama", config.ollama_embedding_model),
    )

    result, bundle = build_context_bundle(packet_repo, "TASK-0001")

    assert result.ok is True
    assert bundle is not None
    semantic = bundle.export_metadata["adapter_context"]["semantic_ranking"]
    assert semantic["active_provider"] == "ollama"
    assert semantic["scores"][0]["provider_id"] == "ollama"


def test_phase16_context_selection_uses_local_provider(packet_repo, monkeypatch):
    _prepare_repo(packet_repo, embedding_provider="local", model_name="mini-local")
    monkeypatch.setattr(
        "grain.services.embedding_resolver._build_local_provider",
        lambda config: _RankedProvider("local", config.local_embedding_model),
    )

    result, bundle = build_context_bundle(packet_repo, "TASK-0001")

    assert result.ok is True
    assert bundle is not None
    semantic = bundle.export_metadata["adapter_context"]["semantic_ranking"]
    assert semantic["active_provider"] == "local"
    assert semantic["scores"][0]["provider_id"] == "local"


def test_phase16_context_selection_uses_openai_provider(packet_repo, monkeypatch):
    _prepare_repo(packet_repo, embedding_provider="openai", model_name="text-embedding-3-small")
    monkeypatch.setattr(
        "grain.services.embedding_resolver._build_openai_provider",
        lambda config: _RankedProvider("openai", config.openai_embedding_model),
    )

    result, bundle = build_context_bundle(packet_repo, "TASK-0001")

    assert result.ok is True
    assert bundle is not None
    semantic = bundle.export_metadata["adapter_context"]["semantic_ranking"]
    assert semantic["active_provider"] == "openai"
    assert semantic["scores"][0]["provider_id"] == "openai"
