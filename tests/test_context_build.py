"""Tests for context bundle assembly and source selection."""

import yaml

from grain.domain.embedding import EmbeddingProviderStatus, ResolvedEmbeddingProvider, ScoredCandidate
from grain.services.context_service import build_context_bundle, build_source_metadata
from grain.services.task_service import create_packet_directory


def _write_manifest_file(repo_root, manifest_dict):
    manifest_path = repo_root / "docs" / "runtime" / "docs_manifest.yaml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(yaml.dump(manifest_dict), encoding="utf-8")


def _write_file(repo_root, relative_path, content):
    file_path = repo_root / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")


def _write_context_docs(repo_root):
    _write_file(repo_root, "docs/canonical/workflow_spec.md", "# Workflow Spec\nRunning tasks.\n")
    _write_file(repo_root, "docs/canonical/architecture.md", "# Architecture\nDesigning features.\n")
    _write_file(repo_root, "docs/working/backlog.md", "# Backlog\nSelecting tasks.\n")


def _write_adapter_profiles(repo_root):
    _write_file(
        repo_root,
        "docs/runtime/adapter_profiles.md",
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
  - `build/**`
- `ignore_file_patterns`:
  - `build/**`
- `context_priority_rules`:
  - prioritize touched source files, then nearby tests
- `test_or_validation_hints`:
  - run focused tests before full suite
- `review_focus_hints`:
  - behavior regressions
""",
    )


def _write_manifest(repo_root):
    _write_manifest_file(
        repo_root,
        {
            "canonical": [
                {
                    "id": "workflow_spec",
                    "path": "docs/canonical/workflow_spec.md",
                    "purpose": "Workflow guidance",
                    "authority": "highest",
                    "editable_by_agents": False,
                    "read_when": ["running_tasks"],
                },
                {
                    "id": "architecture",
                    "path": "docs/canonical/architecture.md",
                    "purpose": "Architecture guidance",
                    "authority": "highest",
                    "editable_by_agents": False,
                    "read_when": ["designing_features"],
                },
            ],
            "working": [
                {
                    "id": "backlog",
                    "path": "docs/working/backlog.md",
                    "purpose": "Task inventory",
                    "authority": "secondary",
                    "editable_by_agents": True,
                    "read_when": ["selecting_tasks"],
                }
            ],
            "runtime": [],
            "tasks": {},
            "rules": {},
        },
    )


def test_build_context_bundle_defaults_to_running_tasks_and_excludes_working(packet_repo):
    _write_manifest(packet_repo)
    _write_context_docs(packet_repo)
    create_packet_directory(packet_repo, phase=4, task_num=13)

    result, bundle = build_context_bundle(packet_repo, "TASK-0001")

    assert result.ok is True
    assert bundle is not None
    assert bundle.task_id == "TASK-0001"
    assert [packet_file.name for packet_file in bundle.packet_files] == [
        "task.md",
        "context.md",
        "plan.md",
        "deliverable_spec.md",
    ]
    assert [record.id for record in bundle.selected_canonical_docs] == [
        "workflow_spec",
    ]
    assert bundle.selected_working_docs == []
    packet_dir_name = bundle.packet_dir.name
    assert bundle.export_metadata["sources"] == [
        f"tasks/{packet_dir_name}/task.md",
        f"tasks/{packet_dir_name}/context.md",
        f"tasks/{packet_dir_name}/plan.md",
        f"tasks/{packet_dir_name}/deliverable_spec.md",
        "docs/canonical/workflow_spec.md",
    ]


def test_build_context_bundle_can_include_working_docs(packet_repo):
    _write_manifest(packet_repo)
    _write_context_docs(packet_repo)
    create_packet_directory(packet_repo, phase=4, task_num=13)

    result, bundle = build_context_bundle(
        packet_repo,
        "TASK-0001",
        include_working_docs=True,
        context_tags={"selecting_tasks"},
    )

    assert result.ok is True
    assert bundle is not None
    assert [record.id for record in bundle.selected_working_docs] == ["backlog"]
    assert bundle.export_metadata["sources"][-1] == "docs/working/backlog.md"


def test_build_source_metadata_labels_each_source_kind(packet_repo):
    _write_manifest(packet_repo)
    _write_context_docs(packet_repo)
    create_packet_directory(packet_repo, phase=4, task_num=13)

    result, bundle = build_context_bundle(
        packet_repo,
        "TASK-0001",
        include_working_docs=True,
        context_tags={"running_tasks", "selecting_tasks"},
    )

    assert result.ok is True
    assert bundle is not None

    metadata = build_source_metadata(packet_repo, bundle)
    kinds_by_path = {entry["path"]: entry["kind"] for entry in metadata}
    exists_by_path = {entry["path"]: entry["exists"] for entry in metadata}
    packet_dir_name = bundle.packet_dir.name

    assert kinds_by_path[f"tasks/{packet_dir_name}/task.md"] == "packet"
    assert kinds_by_path["docs/canonical/workflow_spec.md"] == "canonical"
    assert kinds_by_path["docs/working/backlog.md"] == "working"
    assert all(exists_by_path.values())


def test_build_context_bundle_applies_primary_adapter_source_bias(packet_repo):
    _write_manifest(packet_repo)
    _write_context_docs(packet_repo)
    _write_adapter_profiles(packet_repo)
    _write_file(packet_repo, "src/main.py", "print('hello')\n")
    _write_file(packet_repo, "tests/test_main.py", "def test_main():\n    assert True\n")
    _write_file(packet_repo, "build/generated.py", "print('generated')\n")
    create_packet_directory(packet_repo, phase=6, task_num=5)

    task_md = packet_repo / "tasks" / "P6-T05-TASK-0001" / "task.md"
    task_md.write_text(
        task_md.read_text(encoding="utf-8").replace(
            "- **Primary Adapter:** none",
            "- **Primary Adapter:** code_adapter",
        ),
        encoding="utf-8",
    )

    result, bundle = build_context_bundle(packet_repo, "TASK-0001")

    assert result.ok is True
    assert bundle is not None
    sources = bundle.export_metadata["sources"]
    assert "src/main.py" in sources
    assert "tests/test_main.py" in sources
    assert "build/generated.py" not in sources
    assert sources.index("src/main.py") < sources.index("tests/test_main.py")

    adapter_context = bundle.export_metadata["adapter_context"]
    assert adapter_context["primary_adapter"] == "code_adapter"
    assert adapter_context["applied"] is True
    assert adapter_context["selected_sources"] == ["src/main.py", "tests/test_main.py"]
    assert set(adapter_context["selection_trace"].keys()) == {"src/main.py", "tests/test_main.py"}
    for source_path, trace in adapter_context["selection_trace"].items():
        assert trace[0] == source_path
        assert any(path.startswith("tasks/P6-T05-TASK-0001/") for path in trace)
    assert adapter_context["review_focus_hints"] == ["behavior regressions"]
    assert adapter_context["test_or_validation_hints"] == ["run focused tests before full suite"]


class _SemanticProvider:
    provider_id = "openai"
    model_name = "semantic-test"

    def score(self, query: str, candidates: list[str]) -> list[ScoredCandidate]:
        assert "authentication middleware" in query
        scored: list[ScoredCandidate] = []
        for candidate in candidates:
            score = 0.1
            if "src/auth_middleware.py" in candidate:
                score = 0.9
            elif "tests/test_auth.py" in candidate:
                score = 0.5
            scored.append(
                ScoredCandidate(
                    candidate=candidate,
                    score=score,
                    provider_id=self.provider_id,
                )
            )
        return sorted(scored, key=lambda item: (-item.score, item.candidate))

    def describe_status(self) -> EmbeddingProviderStatus:
        return EmbeddingProviderStatus(
            provider_id=self.provider_id,
            model_name=self.model_name,
            available=True,
            detail="test provider",
        )


class _SemanticResolver:
    def resolve_root(self, root):
        provider = _SemanticProvider()
        return provider, ResolvedEmbeddingProvider(
            configured_provider="openai",
            active_provider="openai",
            configured_model="semantic-test",
            active_model="semantic-test",
            provider_status=provider.describe_status(),
        )


def test_build_context_bundle_reranks_graph_traced_sources_semantically(packet_repo):
    _write_manifest(packet_repo)
    _write_context_docs(packet_repo)
    _write_adapter_profiles(packet_repo)
    _write_file(packet_repo, "src/auth_middleware.py", "def auth_middleware(request):\n    return request\n")
    _write_file(packet_repo, "src/database.py", "def run_migrations():\n    return True\n")
    _write_file(packet_repo, "tests/test_auth.py", "def test_auth_middleware():\n    assert True\n")
    create_packet_directory(packet_repo, phase=6, task_num=5)

    packet_dir = packet_repo / "tasks" / "P6-T05-TASK-0001"
    task_md = packet_dir / "task.md"
    task_md.write_text(
        """# Task: Improve auth middleware

## Metadata
- **ID:** TASK-0001
- **Status:** draft
- **Phase:** Phase 6
- **Backlog:** P6-T05
- **Packet Path:** tasks/P6-T05-TASK-0001/
- **Dependencies:** none
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
Improve authentication middleware behavior and keep nearby auth tests aligned.

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

    result, bundle = build_context_bundle(
        packet_repo,
        "TASK-0001",
        embedding_resolver=_SemanticResolver(),
    )

    assert result.ok is True
    assert bundle is not None
    sources = bundle.export_metadata["sources"]
    auth_index = sources.index("src/auth_middleware.py")
    test_index = sources.index("tests/test_auth.py")
    db_index = sources.index("src/database.py")
    assert auth_index < test_index < db_index

    adapter_context = bundle.export_metadata["adapter_context"]
    semantic = adapter_context["semantic_ranking"]
    assert semantic["active_provider"] == "openai"
    assert semantic["applied"] is True
    assert [item["path"] for item in semantic["scores"]] == [
        "src/auth_middleware.py",
        "tests/test_auth.py",
        "src/database.py",
    ]
    assert [item["path"] for item in semantic["ranked_scores"]] == [
        "src/auth_middleware.py",
        "tests/test_auth.py",
        "src/database.py",
    ]
    assert semantic["ranked_scores"][0]["components"][0]["signal_id"] == "graph_distance"
    assert any(
        component["signal_id"] == "semantic_similarity"
        for component in semantic["ranked_scores"][0]["components"]
    )
