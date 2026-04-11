"""Tests for loading adapter profile configuration from runtime markdown."""

from pathlib import Path

import pytest

from grain.adapters.adapter_config import load_adapter_profiles, parse_adapter_profiles_markdown
from grain.domain.errors import ConfigError, MissingPathError


SAMPLE_ADAPTER_PROFILES = """# Adapter Profiles

## 5. Adapter Profiles

### code_adapter
- `adapter_id`: `code_adapter`
- `domain_type`: `code`
- `applies_to`:
  - Python
  - CLI tooling
- `relevant_file_patterns`:
  - `src/**`
- `test_or_validation_hints`:
  - run focused tests first

### frontend_adapter
- `adapter_id`: `frontend_adapter`
- `domain_type`: `frontend`
- `applies_to`:
  - React
- `context_priority_rules`:
  - prioritize changed UI modules
"""


def test_parse_adapter_profiles_returns_expected_profiles():
    profiles = parse_adapter_profiles_markdown(SAMPLE_ADAPTER_PROFILES)

    assert [profile.adapter_id for profile in profiles] == [
        "code_adapter",
        "frontend_adapter",
    ]
    code_profile = profiles[0]
    assert code_profile.domain_type == "code"
    assert code_profile.applies_to == ["Python", "CLI tooling"]
    assert code_profile.relevant_file_patterns == ["src/**"]
    assert code_profile.test_or_validation_hints == ["run focused tests first"]

    frontend_profile = profiles[1]
    assert frontend_profile.context_priority_rules == ["prioritize changed UI modules"]
    assert frontend_profile.test_or_validation_hints == []


def test_parse_adapter_profiles_raises_for_missing_required_field():
    invalid = SAMPLE_ADAPTER_PROFILES.replace(
        "- `domain_type`: `code`\n",
        "",
    )
    with pytest.raises(ConfigError) as exc:
        parse_adapter_profiles_markdown(invalid)
    assert "Missing required field(s)" in exc.value.detail


def test_parse_adapter_profiles_raises_when_required_hint_is_missing():
    invalid = SAMPLE_ADAPTER_PROFILES.replace(
        "- `test_or_validation_hints`:\n  - run focused tests first\n",
        "",
    ).replace(
        "- `context_priority_rules`:\n  - prioritize changed UI modules\n",
        "",
    )
    with pytest.raises(ConfigError) as exc:
        parse_adapter_profiles_markdown(invalid)
    assert "must include at least one hint section" in exc.value.detail


def test_load_adapter_profiles_reads_runtime_file(tmp_path: Path):
    profiles_path = tmp_path / "docs" / "runtime" / "adapter_profiles.md"
    profiles_path.parent.mkdir(parents=True)
    profiles_path.write_text(SAMPLE_ADAPTER_PROFILES, encoding="utf-8")

    profiles = load_adapter_profiles(tmp_path)
    assert [profile.adapter_id for profile in profiles] == [
        "code_adapter",
        "frontend_adapter",
    ]


def test_load_adapter_profiles_raises_when_file_missing(tmp_path: Path):
    with pytest.raises(MissingPathError) as exc:
        load_adapter_profiles(tmp_path)
    assert "Adapter profile config not found" in exc.value.message
