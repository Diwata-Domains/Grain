"""Domain models for the orchestration service planning layer.

All types here represent proposal artifacts. They must pass through the
Review/Gate Layer before any accepted candidates are converted to task packets.
Schema defined in data_contracts.md §18.
"""

from __future__ import annotations

from dataclasses import dataclass, field

VALID_PLAN_STATUSES: frozenset[str] = frozenset(
    {"draft", "under_review", "accepted", "rejected", "deferred"}
)


@dataclass
class PacketCandidate:
    """A proposed task packet within an OrchestratorPlan.

    data_contracts.md §18.2 — packet_candidates entry schema.
    """

    candidate_id: str
    title: str
    scope_summary: str = ""
    primary_adapter: str | None = None
    depends_on: list[str] = field(default_factory=list)


@dataclass
class CrossDomainDependency:
    """A dependency relationship between two packet candidates spanning adapter domains.

    Used to populate OrchestratorPlan.dependency_links.
    """

    from_candidate: str
    to_candidate: str
    adapter_domains: list[str] = field(default_factory=list)


@dataclass
class OrchestratorPlan:
    """Structured planning proposal produced by the orchestration service.

    All instances are proposals until explicitly accepted via the Review/Gate Layer.
    Direct task packet creation from an OrchestratorPlan is prohibited — accepted
    candidates must be converted through `forge task create`.

    data_contracts.md §18.2 — OrchestratorPlan schema.
    """

    plan_id: str
    scope_summary: str
    produced_by: str
    status: str
    active_adapters: list[str] = field(default_factory=list)
    packet_candidates: list[PacketCandidate] = field(default_factory=list)
    dependency_links: list[CrossDomainDependency] = field(default_factory=list)
    cross_domain_flags: list[str] = field(default_factory=list)
    split_recommendations: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.status not in VALID_PLAN_STATUSES:
            raise ValueError(
                f"Invalid OrchestratorPlan status {self.status!r}. "
                f"Must be one of: {sorted(VALID_PLAN_STATUSES)}"
            )
