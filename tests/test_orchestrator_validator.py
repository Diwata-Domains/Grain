"""Tests for OrchestratorPlan validator helpers."""

from grain.validators.orchestrator_validator import validate_orchestrator_plan_dict


def _valid_plan() -> dict:
    return {
        "plan_id": "OP-001",
        "scope_summary": "add checkout flow",
        "produced_by": "orchestration_service",
        "status": "draft",
        "active_adapters": ["code_adapter"],
        "packet_candidates": [
            {
                "candidate_id": "C-001",
                "title": "code_adapter: add checkout flow",
                "scope_summary": "add checkout flow",
                "primary_adapter": "code_adapter",
                "depends_on": [],
            }
        ],
        "dependency_links": [],
        "cross_domain_flags": [],
        "split_recommendations": [],
    }


def test_validate_orchestrator_plan_dict_valid_payload_passes():
    errors = validate_orchestrator_plan_dict(
        _valid_plan(),
        known_adapter_ids={"code_adapter", "frontend_adapter"},
    )
    assert errors == []


def test_validate_orchestrator_plan_dict_requires_plan_id():
    plan = _valid_plan()
    plan["plan_id"] = ""
    errors = validate_orchestrator_plan_dict(plan)
    assert any("plan_id is required" in error for error in errors)


def test_validate_orchestrator_plan_dict_rejects_invalid_status():
    plan = _valid_plan()
    plan["status"] = "active"
    errors = validate_orchestrator_plan_dict(plan)
    assert any("status must be one of" in error for error in errors)


def test_validate_orchestrator_plan_dict_requires_candidate_fields():
    plan = _valid_plan()
    plan["packet_candidates"] = [{"candidate_id": "", "title": ""}]
    errors = validate_orchestrator_plan_dict(plan)
    assert any("candidate_id is required" in error for error in errors)
    assert any(".title is required" in error for error in errors)


def test_validate_orchestrator_plan_dict_checks_known_adapters():
    plan = _valid_plan()
    plan["active_adapters"] = ["unknown_adapter"]
    errors = validate_orchestrator_plan_dict(
        plan,
        known_adapter_ids={"code_adapter"},
    )
    assert errors == ["active_adapter unknown: unknown_adapter"]
