# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""Domain models for adapter profile configuration and capability surface protocol."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# Capability result types
# ---------------------------------------------------------------------------


@dataclass
class ScopeSignal:
    """Output of the detect_scope capability.

    Identifies file patterns and relevant operational areas for a described
    work item. Empty lists indicate no signal from this adapter.
    """

    file_patterns: list[str] = field(default_factory=list)
    relevant_areas: list[str] = field(default_factory=list)


@dataclass
class ContextHint:
    """Output of the collect_context capability.

    Provides domain-specific file patterns and context priority rules for
    assembling a task execution context. Empty lists indicate no hints.
    """

    file_patterns: list[str] = field(default_factory=list)
    priority_rules: list[str] = field(default_factory=list)


@dataclass
class ImpactSignal:
    """Output of the analyze_impact capability.

    Surfaces likely affected files and downstream areas given a set of
    touched files. Empty lists indicate no impact signals.
    """

    affected_files: list[str] = field(default_factory=list)
    downstream_areas: list[str] = field(default_factory=list)


@dataclass
class ValidationRequirement:
    """Output of the validate_changes capability.

    Reports domain-specific validation requirements for outputs in this
    domain. Empty list indicates no additional requirements.
    """

    requirements: list[str] = field(default_factory=list)


@dataclass
class ArtifactPattern:
    """Output of the export_artifacts capability.

    Describes expected deliverable patterns for tasks in this domain.
    Empty list indicates no patterns defined.
    """

    patterns: list[str] = field(default_factory=list)


@dataclass
class FollowupSuggestion:
    """Output of the suggest_followups capability.

    Identifies likely follow-up work in this domain given an execution
    outcome. Empty list indicates no suggestions.
    """

    followups: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Capability protocol and null implementation
# ---------------------------------------------------------------------------


@runtime_checkable
class AdapterCapabilityProtocol(Protocol):
    """Protocol for optional adapter capability functions.

    Adapters may optionally provide implementations of these methods. The
    orchestration service queries capabilities through this interface.
    Adapters that do not implement capabilities remain fully valid — the
    orchestration service degrades gracefully via NullAdapterCapability.

    All capability outputs are advisory inputs to the orchestration service.
    No capability method may mutate state.
    """

    def detect_scope(self, scope_description: str) -> ScopeSignal:
        """Identify file patterns and operational areas relevant to a work item."""
        ...

    def collect_context(self, task_description: str) -> ContextHint:
        """Provide domain-specific context selection hints for a task."""
        ...

    def analyze_impact(self, touched_files: list[str]) -> ImpactSignal:
        """Surface likely affected files and downstream areas."""
        ...

    def validate_changes(self, task_description: str) -> ValidationRequirement:
        """Report domain-specific validation requirements."""
        ...

    def export_artifacts(self, task_description: str) -> ArtifactPattern:
        """Describe expected deliverable patterns for this domain."""
        ...

    def suggest_followups(self, execution_outcome: str) -> FollowupSuggestion:
        """Identify likely follow-up work given an execution outcome."""
        ...


class NullAdapterCapability:
    """No-op adapter capability implementation for graceful degradation.

    Returned by AdapterProfile.get_capabilities() when no capabilities are
    registered. All methods return structurally valid empty results so the
    orchestration service can call them unconditionally.
    """

    def detect_scope(self, scope_description: str) -> ScopeSignal:
        return ScopeSignal()

    def collect_context(self, task_description: str) -> ContextHint:
        return ContextHint()

    def analyze_impact(self, touched_files: list[str]) -> ImpactSignal:
        return ImpactSignal()

    def validate_changes(self, task_description: str) -> ValidationRequirement:
        return ValidationRequirement()

    def export_artifacts(self, task_description: str) -> ArtifactPattern:
        return ArtifactPattern()

    def suggest_followups(self, execution_outcome: str) -> FollowupSuggestion:
        return FollowupSuggestion()


# ---------------------------------------------------------------------------
# Adapter profile domain model
# ---------------------------------------------------------------------------


@dataclass
class AdapterProfile:
    """Represents one adapter profile and its optional guidance hints."""

    adapter_id: str
    domain_type: str
    applies_to: list[str]
    relevant_file_patterns: list[str] = field(default_factory=list)
    ignore_file_patterns: list[str] = field(default_factory=list)
    build_or_run_hints: list[str] = field(default_factory=list)
    test_or_validation_hints: list[str] = field(default_factory=list)
    review_focus_hints: list[str] = field(default_factory=list)
    context_priority_rules: list[str] = field(default_factory=list)
    default_model_bias: list[str] = field(default_factory=list)
    capabilities: AdapterCapabilityProtocol | None = field(
        default=None, compare=False, repr=False
    )

    def get_capabilities(self) -> AdapterCapabilityProtocol:
        """Return registered capabilities or NullAdapterCapability for graceful degradation."""
        return self.capabilities if self.capabilities is not None else NullAdapterCapability()
