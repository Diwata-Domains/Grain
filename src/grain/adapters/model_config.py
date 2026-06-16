# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Load and parse model profile configuration from runtime markdown."""

from __future__ import annotations

import re
from pathlib import Path

from grain.domain.errors import ConfigError, MissingPathError
from grain.domain.routing import EscalationRule, ModelProfile, ModelRoutingConfig

AGENT_PROFILES_PATH = "docs/runtime/agent_profiles.md"
_MODEL_CLASSES: tuple[str, ...] = ("open_model", "frontier_model", "reviewer_model")
_CLASS_HEADER = re.compile(r"^###\s+(open_model|frontier_model|reviewer_model)\s*$")
_ESCALATE_FROM = re.compile(r"^Escalate from (\w+) to (\w+) when:\s*$")
_ESCALATE_TO = re.compile(r"^Use (\w+) when:\s*$")


def load_model_profiles(root: Path) -> ModelRoutingConfig:
    """Load model routing profiles from docs/runtime/agent_profiles.md."""
    config_path = root / AGENT_PROFILES_PATH
    if not config_path.exists():
        raise MissingPathError(
            f"Model profile config not found: {AGENT_PROFILES_PATH}",
            detail=str(config_path),
        )

    text = config_path.read_text(encoding="utf-8")
    return parse_agent_profiles_markdown(text, source_path=AGENT_PROFILES_PATH)


def parse_agent_profiles_markdown(
    text: str,
    source_path: str = AGENT_PROFILES_PATH,
) -> ModelRoutingConfig:
    """Parse model profiles and escalation rules from agent_profiles markdown."""
    lines = text.splitlines()
    use_for: dict[str, list[str]] = {name: [] for name in _MODEL_CLASSES}
    avoid_for: dict[str, list[str]] = {name: [] for name in _MODEL_CLASSES}
    preferred_models: dict[str, list[str]] = {name: [] for name in _MODEL_CLASSES}
    escalation_rules: list[EscalationRule] = []

    current_class: str | None = None
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        class_match = _CLASS_HEADER.match(stripped)
        if class_match:
            current_class = class_match.group(1)
            index += 1
            continue

        if current_class and stripped == "Use for:":
            items, index = _consume_bullets(lines, index + 1)
            use_for[current_class] = items
            continue

        if current_class and stripped == "Avoid for:":
            items, index = _consume_bullets(lines, index + 1)
            avoid_for[current_class] = items
            continue

        if stripped == "## Escalation Rules":
            rules, index = _parse_escalation_rules(lines, index + 1)
            escalation_rules.extend(rules)
            continue

        if stripped == "## Current Preferred Mapping":
            preferred_models, index = _parse_preferred_mapping(lines, index + 1)
            continue

        index += 1

    missing_classes = [name for name in _MODEL_CLASSES if not use_for.get(name)]
    if missing_classes:
        missing = ", ".join(missing_classes)
        raise ConfigError(
            "Model profile config is incomplete",
            detail=f"Missing model class section(s): {missing}",
        )

    profiles = [
        ModelProfile(
            model_class=name,
            use_for=use_for.get(name, []),
            avoid_for=avoid_for.get(name, []),
            preferred_models=preferred_models.get(name, []),
            escalation_targets=_build_escalation_targets(name, escalation_rules),
        )
        for name in _MODEL_CLASSES
    ]
    return ModelRoutingConfig(
        profiles=profiles,
        escalation_rules=escalation_rules,
        source_path=source_path,
    )


def _consume_bullets(lines: list[str], start_index: int) -> tuple[list[str], int]:
    """Collect contiguous markdown bullet items starting at start_index."""
    items: list[str] = []
    index = start_index
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped:
            index += 1
            continue
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
            index += 1
            continue
        break
    return items, index


def _parse_escalation_rules(
    lines: list[str],
    start_index: int,
) -> tuple[list[EscalationRule], int]:
    """Parse escalation rules section into EscalationRule entries."""
    rules: list[EscalationRule] = []
    index = start_index
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith("## "):
            break

        from_match = _ESCALATE_FROM.match(stripped)
        if from_match:
            conditions, index = _consume_bullets(lines, index + 1)
            rules.append(
                EscalationRule(
                    source_class=from_match.group(1),
                    target_class=from_match.group(2),
                    conditions=conditions,
                )
            )
            continue

        to_match = _ESCALATE_TO.match(stripped)
        if to_match:
            conditions, index = _consume_bullets(lines, index + 1)
            rules.append(
                EscalationRule(
                    source_class="*",
                    target_class=to_match.group(1),
                    conditions=conditions,
                )
            )
            continue

        index += 1

    return rules, index


def _parse_preferred_mapping(
    lines: list[str],
    start_index: int,
) -> tuple[dict[str, list[str]], int]:
    """Parse model-to-provider mapping bullets."""
    mapping: dict[str, list[str]] = {name: [] for name in _MODEL_CLASSES}
    index = start_index
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith("## "):
            break
        if not stripped.startswith("- "):
            index += 1
            continue

        content = stripped[2:]
        if ":" not in content:
            index += 1
            continue

        model_class, providers = content.split(":", 1)
        model_class = model_class.strip()
        if model_class in mapping:
            mapping[model_class] = _parse_provider_list(providers.strip())
        index += 1

    return mapping, index


def _parse_provider_list(value: str) -> list[str]:
    """Parse provider names from mapping values like 'Claude or Codex'."""
    normalized = value.replace("/", ",")
    parts = re.split(r"\s+or\s+|,\s*", normalized)
    return [part.strip() for part in parts if part.strip()]


def _build_escalation_targets(
    model_class: str,
    rules: list[EscalationRule],
) -> list[str]:
    """Build unique escalation targets for one model class."""
    targets: list[str] = []
    for rule in rules:
        if rule.source_class not in (model_class, "*"):
            continue
        if rule.target_class == model_class:
            continue
        if rule.target_class not in targets:
            targets.append(rule.target_class)
    return targets
