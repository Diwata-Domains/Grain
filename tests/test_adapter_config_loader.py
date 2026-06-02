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


def test_parse_runtime_adapter_profiles_includes_data_adapter_contract():
    profiles = parse_adapter_profiles_markdown(
        Path("docs/runtime/adapter_profiles.md").read_text(encoding="utf-8")
    )

    code_profile = next(profile for profile in profiles if profile.adapter_id == "code_adapter")
    obsidian_profile = next(profile for profile in profiles if profile.adapter_id == "obsidian_adapter")
    data_profile = next(profile for profile in profiles if profile.adapter_id == "data_adapter")
    database_profile = next(profile for profile in profiles if profile.adapter_id == "database_adapter")
    crawler_profile = next(profile for profile in profiles if profile.adapter_id == "crawler_adapter")
    assert "**/*.ipynb" not in code_profile.relevant_file_patterns
    assert obsidian_profile.domain_type == "docs"
    assert "**/*.md" in obsidian_profile.relevant_file_patterns
    assert any("wiki-link" in hint for hint in obsidian_profile.review_focus_hints)
    assert any(".obsidian/" in hint for hint in obsidian_profile.context_priority_rules)
    assert data_profile.domain_type == "data"
    assert "**/*.ipynb" in data_profile.relevant_file_patterns
    assert "**/*.parquet" in data_profile.relevant_file_patterns
    assert "**/*.onnx" in data_profile.relevant_file_patterns
    assert "requirements.txt" in data_profile.relevant_file_patterns
    assert any("metadata-only" in hint for hint in data_profile.build_or_run_hints)
    assert any(".ipynb" in hint for hint in data_profile.context_priority_rules)
    assert database_profile.domain_type == "code"
    assert "**/*.sql" in database_profile.relevant_file_patterns
    assert "schema.prisma" in database_profile.relevant_file_patterns
    assert "queries/**" in database_profile.relevant_file_patterns
    assert "src/repositories/**" in database_profile.relevant_file_patterns
    assert any("migration" in hint for hint in database_profile.test_or_validation_hints)
    assert any("rollback" in hint for hint in database_profile.review_focus_hints)
    assert any("schema files and migration directories" in hint for hint in database_profile.context_priority_rules)
    assert crawler_profile.domain_type == "code"
    assert "scrapy.cfg" in crawler_profile.relevant_file_patterns
    assert "selectors/**" in crawler_profile.relevant_file_patterns
    assert "normalizers/**" in crawler_profile.relevant_file_patterns
    assert "tests/fixtures/**" in crawler_profile.relevant_file_patterns
    assert any("selector coverage" in hint for hint in crawler_profile.test_or_validation_hints)
    assert any("robots policy" in hint for hint in crawler_profile.review_focus_hints)
    assert any("crawl configs" in hint for hint in crawler_profile.context_priority_rules)


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
