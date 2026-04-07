"""Domain models for adapter profile configuration."""

from __future__ import annotations

from dataclasses import dataclass, field


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
