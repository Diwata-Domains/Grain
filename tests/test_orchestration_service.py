"""Tests for orchestration service (task and phase level)."""

from pathlib import Path

from grain.services.orchestration_service import (
    analyze_scope_signals,
    build_phase_level_plan,
    build_task_level_plan,
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_adapter_profiles(root: Path) -> None:
    _write(
        root / "docs" / "runtime" / "adapter_profiles.md",
        """# Adapter Profiles

## 5. Adapter Profiles

### code_adapter
- `adapter_id`: `code_adapter`
- `domain_type`: `code`
- `applies_to`:
  - python
  - backend
  - cli
- `context_priority_rules`:
  - prioritize source files

### frontend_adapter
- `adapter_id`: `frontend_adapter`
- `domain_type`: `frontend`
- `applies_to`:
  - react
  - ui
  - browser
- `test_or_validation_hints`:
  - run component tests

### data_adapter
- `adapter_id`: `data_adapter`
- `domain_type`: `data`
- `applies_to`:
  - notebook
  - parquet
  - model
- `relevant_file_patterns`:
  - `**/*.ipynb`
  - `**/*.parquet`
- `test_or_validation_hints`:
  - validate metadata summaries
""",
    )


def test_build_task_level_plan_selects_matching_adapter(tmp_path: Path):
    _write_adapter_profiles(tmp_path)
    result, plan = build_task_level_plan(tmp_path, "add python cli command")

    assert result.ok is True
    assert plan is not None
    assert plan.status == "draft"
    assert "code_adapter" in plan.active_adapters
    assert plan.packet_candidates[0].primary_adapter == "code_adapter"


def test_build_task_level_plan_multidomain_creates_split_and_dependencies(tmp_path: Path):
    _write_adapter_profiles(tmp_path)
    result, plan = build_task_level_plan(tmp_path, "build react ui and python backend api")

    assert result.ok is True
    assert plan is not None
    assert len(plan.active_adapters) == 2
    assert len(plan.packet_candidates) == 2
    assert len(plan.dependency_links) == 1
    assert plan.cross_domain_flags == ["code", "frontend"]
    assert plan.split_recommendations == ["C-001", "C-002"]


def test_build_task_level_plan_degrades_when_no_adapter_signal(tmp_path: Path):
    _write_adapter_profiles(tmp_path)
    result, plan = build_task_level_plan(tmp_path, "organize sprint retrospective notes")

    assert result.ok is True
    assert plan is not None
    assert plan.active_adapters == []
    assert len(plan.packet_candidates) == 1
    assert plan.packet_candidates[0].primary_adapter is None


def test_build_task_level_plan_missing_profiles_returns_error(tmp_path: Path):
    result, plan = build_task_level_plan(tmp_path, "add python cli command")

    assert result.ok is False
    assert plan is None
    assert any("Adapter profile config not found" in err for err in result.errors)


def test_build_task_level_plan_requires_scope_summary(tmp_path: Path):
    _write_adapter_profiles(tmp_path)
    result, plan = build_task_level_plan(tmp_path, "   ")

    assert result.ok is False
    assert plan is None
    assert result.errors == ["scope_summary is required"]


def test_build_phase_level_plan_creates_shape_from_phase_segments(tmp_path: Path):
    _write_adapter_profiles(tmp_path)
    result, plan = build_phase_level_plan(
        tmp_path,
        "backend api and react ui",
    )

    assert result.ok is True
    assert plan is not None
    assert plan.status == "draft"
    assert len(plan.packet_candidates) == 2
    assert len(plan.dependency_links) == 1
    assert plan.split_recommendations == ["C-001", "C-002"]
    assert plan.active_adapters == ["code_adapter", "frontend_adapter"]


def test_build_phase_level_plan_respects_explicit_candidate_titles(tmp_path: Path):
    _write_adapter_profiles(tmp_path)
    result, plan = build_phase_level_plan(
        tmp_path,
        "phase replan for checkout",
        phase_candidates=[
            "stabilize python payment service",
            "refine react checkout ui",
            "document rollout",
        ],
    )

    assert result.ok is True
    assert plan is not None
    assert [candidate.title for candidate in plan.packet_candidates] == [
        "stabilize python payment service",
        "refine react checkout ui",
        "document rollout",
    ]
    assert len(plan.dependency_links) == 2


def test_build_phase_level_plan_requires_summary(tmp_path: Path):
    _write_adapter_profiles(tmp_path)
    result, plan = build_phase_level_plan(tmp_path, "   ")

    assert result.ok is False
    assert plan is None
    assert result.errors == ["phase_summary is required"]


def test_analyze_scope_signals_reports_active_adapters(tmp_path: Path):
    _write_adapter_profiles(tmp_path)
    result, payload = analyze_scope_signals(tmp_path, "build react ui and python cli")

    assert result.ok is True
    assert payload is not None
    assert sorted(payload["active_adapters"]) == ["code_adapter", "frontend_adapter"]
    assert payload["cross_domain_flags"] == ["code", "frontend"]
    assert "impact" in payload["adapter_signals"][0]
    assert "affected_files" in payload["adapter_signals"][0]["impact"]


def test_analyze_scope_signals_includes_ranked_impact_payload(tmp_path: Path, monkeypatch):
    _write_adapter_profiles(tmp_path)
    monkeypatch.setattr(
        "grain.services.orchestration_service.rank_impacted_files",
        lambda root, touched_files, affected_files: {
            "active_provider": "none",
            "ranked_affected_files": [{"path": "src/api.py", "total_score": 1.0, "components": []}],
        },
    )

    result, payload = analyze_scope_signals(tmp_path, "add python cli")

    assert result.ok is True
    assert payload is not None
    impact = payload["adapter_signals"][0]["impact"]
    assert impact["ranking"]["active_provider"] == "none"
    assert impact["ranking"]["ranked_affected_files"][0]["path"] == "src/api.py"


def test_analyze_scope_signals_includes_task_advice_payload(tmp_path: Path, monkeypatch):
    _write_adapter_profiles(tmp_path)
    monkeypatch.setattr(
        "grain.services.orchestration_service.advise_next_tasks",
        lambda root, scope_summary: {
            "phase": "17",
            "candidate_pool_status": "draft",
            "ranked_tasks": [{"task_ref": "P17-T04", "title": "Next task", "status": "draft", "total_score": 1.0, "components": []}],
        },
    )

    result, payload = analyze_scope_signals(tmp_path, "add python cli")

    assert result.ok is True
    assert payload is not None
    assert payload["task_advice"]["phase"] == "17"
    assert payload["task_advice"]["ranked_tasks"][0]["task_ref"] == "P17-T04"


def test_analyze_scope_signals_activates_data_adapter_for_notebook_scope(tmp_path: Path):
    _write_adapter_profiles(tmp_path)
    _write(tmp_path / "analysis.ipynb", '{"cells":[],"metadata":{},"nbformat":4,"nbformat_minor":5}')
    _write(tmp_path / "data" / "train.parquet", "PAR1")

    result, payload = analyze_scope_signals(tmp_path, "review notebook parquet model pipeline")

    assert result.ok is True
    assert payload is not None
    assert "data_adapter" in payload["active_adapters"]
    signal = next(item for item in payload["adapter_signals"] if item["adapter_id"] == "data_adapter")
    assert signal["active"] is True
    assert signal["impact"]["affected_files"]


def test_build_task_level_plan_unknown_adapter_filter_errors(tmp_path: Path):
    _write_adapter_profiles(tmp_path)
    result, plan = build_task_level_plan(
        tmp_path,
        "add python cli command",
        adapter_ids=["missing_adapter"],
    )

    assert result.ok is False
    assert plan is None
    assert result.errors == ["Unknown adapter id: missing_adapter"]
