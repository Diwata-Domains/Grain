"""Tests for OrchestratorPlan domain model (data_contracts.md §18)."""

import pytest

from forge.domain.orchestrator import (
    CrossDomainDependency,
    OrchestratorPlan,
    PacketCandidate,
    VALID_PLAN_STATUSES,
)


class TestPacketCandidate:
    def test_required_fields(self):
        c = PacketCandidate(candidate_id="C-001", title="Add auth module")
        assert c.candidate_id == "C-001"
        assert c.title == "Add auth module"

    def test_optional_defaults(self):
        c = PacketCandidate(candidate_id="C-001", title="Add auth module")
        assert c.scope_summary == ""
        assert c.primary_adapter is None
        assert c.depends_on == []

    def test_full_construction(self):
        c = PacketCandidate(
            candidate_id="C-002",
            title="Add payment flow",
            scope_summary="Stripe integration",
            primary_adapter="payments",
            depends_on=["C-001"],
        )
        assert c.primary_adapter == "payments"
        assert c.depends_on == ["C-001"]


class TestCrossDomainDependency:
    def test_required_fields(self):
        d = CrossDomainDependency(from_candidate="C-001", to_candidate="C-002")
        assert d.from_candidate == "C-001"
        assert d.to_candidate == "C-002"

    def test_adapter_domains_default(self):
        d = CrossDomainDependency(from_candidate="C-001", to_candidate="C-002")
        assert d.adapter_domains == []

    def test_full_construction(self):
        d = CrossDomainDependency(
            from_candidate="C-001",
            to_candidate="C-002",
            adapter_domains=["payments", "auth"],
        )
        assert d.adapter_domains == ["payments", "auth"]


class TestOrchestratorPlan:
    def test_minimal_construction(self):
        plan = OrchestratorPlan(
            plan_id="OP-001",
            scope_summary="Add payment integration",
            produced_by="orchestration_service",
            status="draft",
        )
        assert plan.plan_id == "OP-001"
        assert plan.status == "draft"

    def test_all_list_fields_default_empty(self):
        plan = OrchestratorPlan(
            plan_id="OP-001",
            scope_summary="test",
            produced_by="test",
            status="draft",
        )
        assert plan.active_adapters == []
        assert plan.packet_candidates == []
        assert plan.dependency_links == []
        assert plan.cross_domain_flags == []
        assert plan.split_recommendations == []

    def test_valid_statuses(self):
        for status in VALID_PLAN_STATUSES:
            plan = OrchestratorPlan(
                plan_id="OP-001",
                scope_summary="test",
                produced_by="test",
                status=status,
            )
            assert plan.status == status

    def test_invalid_status_raises(self):
        with pytest.raises(ValueError, match="Invalid OrchestratorPlan status"):
            OrchestratorPlan(
                plan_id="OP-001",
                scope_summary="test",
                produced_by="test",
                status="active",
            )

    def test_full_construction(self):
        candidates = [
            PacketCandidate(candidate_id="C-001", title="Auth module"),
            PacketCandidate(candidate_id="C-002", title="Payment flow", depends_on=["C-001"]),
        ]
        links = [CrossDomainDependency(from_candidate="C-001", to_candidate="C-002")]
        plan = OrchestratorPlan(
            plan_id="OP-002",
            scope_summary="Full checkout flow",
            produced_by="orchestration_service",
            status="under_review",
            active_adapters=["payments", "auth"],
            packet_candidates=candidates,
            dependency_links=links,
            cross_domain_flags=["payments", "auth"],
            split_recommendations=["C-002"],
        )
        assert len(plan.packet_candidates) == 2
        assert len(plan.dependency_links) == 1
        assert plan.cross_domain_flags == ["payments", "auth"]
        assert plan.split_recommendations == ["C-002"]

    def test_list_fields_are_independent(self):
        """Each instance should have its own list instances, not shared defaults."""
        plan_a = OrchestratorPlan(
            plan_id="OP-A", scope_summary="a", produced_by="t", status="draft"
        )
        plan_b = OrchestratorPlan(
            plan_id="OP-B", scope_summary="b", produced_by="t", status="draft"
        )
        plan_a.active_adapters.append("payments")
        assert plan_b.active_adapters == []
