"""Load and parse adapter profile configuration from runtime markdown."""

from __future__ import annotations

import re
from pathlib import Path

from forge.domain.adapters import AdapterProfile
from forge.domain.errors import ConfigError, MissingPathError

ADAPTER_PROFILES_PATH = "docs/runtime/adapter_profiles.md"
_PROFILE_SECTION_HEADER = "## 5. Adapter Profiles"
_PROFILE_HEADER = re.compile(r"^###\s+([a-zA-Z0-9_]+)\s*$")
_INLINE_FIELD = re.compile(r"^- `([^`]+)`: `([^`]+)`\s*$")
_LIST_FIELD_HEADER = re.compile(r"^- `([^`]+)`:\s*$")

_REQUIRED_FIELDS: tuple[str, ...] = ("adapter_id", "domain_type", "applies_to")
_REQUIRED_HINT_FIELDS: tuple[str, ...] = (
    "context_priority_rules",
    "test_or_validation_hints",
)


def load_adapter_profiles(root: Path) -> list[AdapterProfile]:
    """Load adapter profiles from docs/runtime/adapter_profiles.md."""
    config_path = root / ADAPTER_PROFILES_PATH
    if not config_path.exists():
        raise MissingPathError(
            f"Adapter profile config not found: {ADAPTER_PROFILES_PATH}",
            detail=str(config_path),
        )

    text = config_path.read_text(encoding="utf-8")
    return parse_adapter_profiles_markdown(text)


def parse_adapter_profiles_markdown(text: str) -> list[AdapterProfile]:
    """Parse adapter profiles from adapter_profiles runtime markdown."""
    lines = text.splitlines()
    profile_start = _find_profile_section(lines)
    if profile_start is None:
        raise ConfigError(
            "Adapter profile config is incomplete",
            detail="Missing '## 5. Adapter Profiles' section",
        )

    profiles: list[AdapterProfile] = []
    index = profile_start + 1
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith("## "):
            break

        profile_match = _PROFILE_HEADER.match(stripped)
        if not profile_match:
            index += 1
            continue

        section_name = profile_match.group(1)
        fields, index = _parse_profile_fields(lines, index + 1)
        profiles.append(_build_profile(section_name, fields))

    if not profiles:
        raise ConfigError(
            "Adapter profile config is incomplete",
            detail="No adapter profiles found in '## 5. Adapter Profiles' section",
        )

    return profiles


def _find_profile_section(lines: list[str]) -> int | None:
    """Return line index for adapter profile section header."""
    for index, line in enumerate(lines):
        if line.strip() == _PROFILE_SECTION_HEADER:
            return index
    return None


def _parse_profile_fields(
    lines: list[str],
    start_index: int,
) -> tuple[dict[str, object], int]:
    """Parse one adapter profile field block under a ### profile header."""
    fields: dict[str, object] = {}
    index = start_index
    while index < len(lines):
        stripped = lines[index].strip()
        if _PROFILE_HEADER.match(stripped) or stripped.startswith("## "):
            break

        inline_match = _INLINE_FIELD.match(stripped)
        if inline_match:
            fields[inline_match.group(1)] = inline_match.group(2).strip()
            index += 1
            continue

        list_header_match = _LIST_FIELD_HEADER.match(stripped)
        if list_header_match:
            items, index = _consume_bullets(lines, index + 1)
            fields[list_header_match.group(1)] = items
            continue

        index += 1

    return fields, index


def _consume_bullets(lines: list[str], start_index: int) -> tuple[list[str], int]:
    """Collect contiguous markdown bullet items starting at start_index."""
    items: list[str] = []
    index = start_index
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped:
            index += 1
            continue
        if _INLINE_FIELD.match(stripped) or _LIST_FIELD_HEADER.match(stripped):
            break
        if stripped.startswith("- "):
            items.append(_strip_backticks(stripped[2:].strip()))
            index += 1
            continue
        break
    return items, index


def _build_profile(section_name: str, fields: dict[str, object]) -> AdapterProfile:
    """Validate parsed fields and convert them into an AdapterProfile."""
    missing_fields = [name for name in _REQUIRED_FIELDS if not fields.get(name)]
    if missing_fields:
        missing = ", ".join(missing_fields)
        raise ConfigError(
            "Adapter profile config is incomplete",
            detail=f"Missing required field(s) in '{section_name}': {missing}",
        )

    adapter_id = _as_text(fields.get("adapter_id"))
    if adapter_id != section_name:
        raise ConfigError(
            "Adapter profile config is invalid",
            detail=(
                f"Section '{section_name}' has adapter_id '{adapter_id}'. "
                "Header and adapter_id must match."
            ),
        )

    domain_type = _as_text(fields.get("domain_type"))
    applies_to = _as_list(fields.get("applies_to"))
    if not applies_to:
        raise ConfigError(
            "Adapter profile config is incomplete",
            detail=f"Field 'applies_to' must include at least one item in '{section_name}'",
        )

    hint_presence = any(_as_list(fields.get(name)) for name in _REQUIRED_HINT_FIELDS)
    if not hint_presence:
        required = ", ".join(_REQUIRED_HINT_FIELDS)
        raise ConfigError(
            "Adapter profile config is incomplete",
            detail=(
                f"Adapter '{section_name}' must include at least one hint section: {required}"
            ),
        )

    return AdapterProfile(
        adapter_id=adapter_id,
        domain_type=domain_type,
        applies_to=applies_to,
        relevant_file_patterns=_as_list(fields.get("relevant_file_patterns")),
        ignore_file_patterns=_as_list(fields.get("ignore_file_patterns")),
        build_or_run_hints=_as_list(fields.get("build_or_run_hints")),
        test_or_validation_hints=_as_list(fields.get("test_or_validation_hints")),
        review_focus_hints=_as_list(fields.get("review_focus_hints")),
        context_priority_rules=_as_list(fields.get("context_priority_rules")),
        default_model_bias=_as_list(fields.get("default_model_bias")),
    )


def _as_text(value: object) -> str:
    """Normalize a parsed scalar field into text."""
    if value is None:
        return ""
    if isinstance(value, list):
        return value[0] if value else ""
    return _strip_backticks(str(value).strip())


def _as_list(value: object) -> list[str]:
    """Normalize a parsed field into a list of strings."""
    if value is None:
        return []
    if isinstance(value, list):
        return [_strip_backticks(str(item).strip()) for item in value if str(item).strip()]
    text = _strip_backticks(str(value).strip())
    return [text] if text else []


def _strip_backticks(value: str) -> str:
    """Remove one layer of surrounding markdown backticks."""
    if len(value) >= 2 and value.startswith("`") and value.endswith("`"):
        return value[1:-1]
    return value
