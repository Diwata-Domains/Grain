"""Validation helpers for OrchestratorPlan artifacts."""

from __future__ import annotations

from grain.domain.orchestrator import VALID_PLAN_STATUSES


def validate_orchestrator_plan_dict(
    plan: dict[str, object],
    *,
    known_adapter_ids: set[str] | None = None,
) -> list[str]:
    """Validate an OrchestratorPlan-like mapping against minimum contract rules.

    Contract source: data_contracts.md §18.3.
    """
    errors: list[str] = []

    plan_id = plan.get("plan_id")
    if not isinstance(plan_id, str) or not plan_id.strip():
        errors.append("plan_id is required and must be a non-empty string")

    status = plan.get("status")
    if not isinstance(status, str) or status not in VALID_PLAN_STATUSES:
        errors.append(
            f"status must be one of {sorted(VALID_PLAN_STATUSES)}"
        )

    packet_candidates = plan.get("packet_candidates")
    if not isinstance(packet_candidates, list):
        errors.append("packet_candidates must be a list")
    else:
        for index, candidate in enumerate(packet_candidates):
            if not isinstance(candidate, dict):
                errors.append(f"packet_candidates[{index}] must be a mapping")
                continue
            candidate_id = candidate.get("candidate_id")
            title = candidate.get("title")
            if not isinstance(candidate_id, str) or not candidate_id.strip():
                errors.append(
                    f"packet_candidates[{index}].candidate_id is required"
                )
            if not isinstance(title, str) or not title.strip():
                errors.append(f"packet_candidates[{index}].title is required")

    active_adapters = plan.get("active_adapters", [])
    if not isinstance(active_adapters, list):
        errors.append("active_adapters must be a list")
    elif known_adapter_ids is not None:
        unknown = [
            adapter_id
            for adapter_id in active_adapters
            if adapter_id not in known_adapter_ids
        ]
        for adapter_id in unknown:
            errors.append(f"active_adapter unknown: {adapter_id}")

    return errors
