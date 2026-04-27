"""Adapter-system tests for profile loading and packet metadata parsing."""

from pathlib import Path

from grain.adapters.adapter_config import load_adapter_profiles
from grain.domain.packets import parse_task_metadata


def test_load_adapter_profiles_populates_expected_fields(tmp_path: Path):
    profiles_path = tmp_path / "docs" / "runtime" / "adapter_profiles.md"
    profiles_path.parent.mkdir(parents=True)
    profiles_path.write_text(
        """# Adapter Profiles

## 5. Adapter Profiles

### code_adapter
- `adapter_id`: `code_adapter`
- `domain_type`: `code`
- `applies_to`:
  - Python
- `relevant_file_patterns`:
  - `src/**`
- `ignore_file_patterns`:
  - `build/**`
- `build_or_run_hints`:
  - use virtualenv
- `test_or_validation_hints`:
  - run focused tests first
- `review_focus_hints`:
  - behavior regressions
- `context_priority_rules`:
  - prioritize touched source files, then nearby tests
- `default_model_bias`:
  - open_model

### docs_adapter
- `adapter_id`: `docs_adapter`
- `domain_type`: `docs`
- `applies_to`:
  - Markdown
- `context_priority_rules`:
  - prioritize changed docs
""",
        encoding="utf-8",
    )

    profiles = load_adapter_profiles(tmp_path)

    assert [profile.adapter_id for profile in profiles] == ["code_adapter", "docs_adapter"]

    code_profile = profiles[0]
    assert code_profile.relevant_file_patterns == ["src/**"]
    assert code_profile.ignore_file_patterns == ["build/**"]
    assert code_profile.build_or_run_hints == ["use virtualenv"]
    assert code_profile.test_or_validation_hints == ["run focused tests first"]
    assert code_profile.review_focus_hints == ["behavior regressions"]
    assert code_profile.context_priority_rules == [
        "prioritize touched source files, then nearby tests",
    ]
    assert code_profile.default_model_bias == ["open_model"]

    docs_profile = profiles[1]
    assert docs_profile.test_or_validation_hints == []
    assert docs_profile.review_focus_hints == []
    assert docs_profile.context_priority_rules == ["prioritize changed docs"]


def test_parse_task_metadata_extracts_adapter_fields_when_present(tmp_path: Path):
    task_md = tmp_path / "task.md"
    task_md.write_text(
        """# Task: Adapter task

## Metadata
- **ID:** TASK-9998
- **Status:** draft
- **Phase:** Phase 6 — Adapter System Foundation (V2)
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** frontend_adapter, docs_adapter

## Objective
Validate adapter parsing.
""",
        encoding="utf-8",
    )

    metadata = parse_task_metadata(task_md)

    assert metadata["primary_adapter"] == "code_adapter"
    assert metadata["secondary_adapters"] == "frontend_adapter, docs_adapter"


def test_parse_task_metadata_legacy_packet_works_without_adapter_fields(tmp_path: Path):
    task_md = tmp_path / "task.md"
    task_md.write_text(
        """# Task: Legacy task

## Metadata
- **ID:** TASK-9997
- **Status:** draft
- **Phase:** Phase 3 — Task Packet System

## Objective
No adapter metadata.
""",
        encoding="utf-8",
    )

    metadata = parse_task_metadata(task_md)

    assert metadata["id"] == "TASK-9997"
    assert metadata["status"] == "draft"
    assert metadata["phase"] == "Phase 3 — Task Packet System"
    assert "primary_adapter" not in metadata
    assert "secondary_adapters" not in metadata
