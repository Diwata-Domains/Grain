# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Domain models and selection logic for model-class routing."""

from dataclasses import dataclass, field
import re

_OPEN_MODEL = "open_model"
_FRONTIER_MODEL = "frontier_model"
_REVIEWER_MODEL = "reviewer_model"

_STAGE_MODEL_MAP: dict[str, str] = {
    "stage 1 canonical design": _FRONTIER_MODEL,
    "canonical design": _FRONTIER_MODEL,
    "stage 2 execution planning": _FRONTIER_MODEL,
    "execution planning": _FRONTIER_MODEL,
    "stage 3 task packet generation": _OPEN_MODEL,
    "task packet generation": _OPEN_MODEL,
    "stage 4 task execution": _OPEN_MODEL,
    "task execution": _OPEN_MODEL,
    "stage 5 review and reconciliation": _REVIEWER_MODEL,
    "review and reconciliation": _REVIEWER_MODEL,
    "stage 6 closure and handoff": _REVIEWER_MODEL,
    "closure and handoff": _REVIEWER_MODEL,
    "select": _OPEN_MODEL,
    "packetize": _OPEN_MODEL,
    "prepare context": _OPEN_MODEL,
    "execute": _OPEN_MODEL,
    "review": _REVIEWER_MODEL,
    "record": _OPEN_MODEL,
    "close or continue": _REVIEWER_MODEL,
}

_REVIEW_KEYWORDS: tuple[str, ...] = (
    "review",
    "accept",
    "acceptance",
    "critique",
    "consistency",
    "validate",
    "validation",
    "complete",
    "completion",
    "handoff",
    "release",
    "gate",
)

_FRONTIER_KEYWORDS: tuple[str, ...] = (
    "architecture",
    "design",
    "ambigu",
    "tradeoff",
    "coordination",
    "cross file",
    "workflow logic",
    "planning",
    "complex",
    "difficult",
    "debug",
    "conflict",
)


@dataclass
class EscalationRule:
    """Represents one escalation rule between model classes."""

    source_class: str
    target_class: str
    conditions: list[str] = field(default_factory=list)


@dataclass
class ModelProfile:
    """Represents one model class profile and routing-relevant metadata."""

    model_class: str
    use_for: list[str] = field(default_factory=list)
    avoid_for: list[str] = field(default_factory=list)
    preferred_models: list[str] = field(default_factory=list)
    escalation_targets: list[str] = field(default_factory=list)


@dataclass
class ModelRoutingConfig:
    """Container for all parsed model profiles and escalation rules."""

    profiles: list[ModelProfile]
    escalation_rules: list[EscalationRule]
    source_path: str = "docs/runtime/agent_profiles.md"

    def by_class(self, model_class: str) -> ModelProfile | None:
        """Return the profile for one model class, or None if missing."""
        for profile in self.profiles:
            if profile.model_class == model_class:
                return profile
        return None

    def model_classes(self) -> list[str]:
        """Return model classes in stored profile order."""
        return [profile.model_class for profile in self.profiles]


@dataclass
class ModelSelection:
    """Routing decision for one stage/role selection query."""

    selected_class: str
    reason: str
    stage: str = ""
    role: str = ""


def select_model_class(
    config: ModelRoutingConfig,
    stage: str | None = None,
    role: str | None = None,
) -> ModelSelection:
    """Select the best model class for a workflow stage or task role."""
    stage_text = (stage or "").strip()
    role_text = (role or "").strip()
    normalized_stage = _normalize_text(stage_text)
    normalized_role = _normalize_text(role_text)
    combined = " ".join(part for part in [normalized_stage, normalized_role] if part).strip()

    if normalized_stage in _STAGE_MODEL_MAP:
        chosen = _STAGE_MODEL_MAP[normalized_stage]
        return ModelSelection(
            selected_class=chosen,
            reason=f"stage mapping matched '{stage_text}'",
            stage=stage_text,
            role=role_text,
        )

    if _matches_any(combined, _REVIEW_KEYWORDS):
        return ModelSelection(
            selected_class=_REVIEWER_MODEL,
            reason="review-oriented signal matched routing rules",
            stage=stage_text,
            role=role_text,
        )

    if _matches_any(combined, _FRONTIER_KEYWORDS):
        return ModelSelection(
            selected_class=_FRONTIER_MODEL,
            reason="ambiguity/architecture signal matched escalation profile",
            stage=stage_text,
            role=role_text,
        )

    profile_match = _match_profile_use_for(config, combined)
    if profile_match is not None:
        return ModelSelection(
            selected_class=profile_match,
            reason="matched model profile capabilities from runtime config",
            stage=stage_text,
            role=role_text,
        )

    default_class = _OPEN_MODEL if _OPEN_MODEL in config.model_classes() else (
        config.model_classes()[0] if config.model_classes() else _OPEN_MODEL
    )
    return ModelSelection(
        selected_class=default_class,
        reason="defaulted to simplest safe model class",
        stage=stage_text,
        role=role_text,
    )


def get_escalation_target(
    config: ModelRoutingConfig,
    current_class: str,
    reason: str | None = None,  # noqa: ARG001 — reserved for future condition matching
) -> str | None:
    """Return the escalation target class for the given model class.

    Checks class-specific rules first, then wildcard ('*') rules.
    Returns None when no escalation path is defined.
    """
    for rule in config.escalation_rules:
        if rule.source_class == current_class:
            return rule.target_class
    for rule in config.escalation_rules:
        if rule.source_class == "*" and rule.target_class != current_class:
            return rule.target_class
    return None


def _match_profile_use_for(config: ModelRoutingConfig, query: str) -> str | None:
    """Match query text against profile use_for phrases with class priority."""
    if not query:
        return None

    # Prefer stronger/specialized classes when both could match.
    for model_class in (_REVIEWER_MODEL, _FRONTIER_MODEL, _OPEN_MODEL):
        profile = config.by_class(model_class)
        if profile is None:
            continue
        for phrase in profile.use_for:
            normalized_phrase = _normalize_text(phrase)
            if not normalized_phrase:
                continue
            if normalized_phrase in query or query in normalized_phrase:
                return model_class
    return None


def _normalize_text(value: str) -> str:
    """Lowercase and normalize separators to simple spaces."""
    lowered = (
        value.lower()
        .replace("_", " ")
        .replace("-", " ")
        .replace("—", " ")
    )
    return re.sub(r"\s+", " ", lowered).strip()


def _matches_any(text: str, keywords: tuple[str, ...]) -> bool:
    """Return True if text contains any keyword fragment."""
    return any(keyword in text for keyword in keywords if keyword)
