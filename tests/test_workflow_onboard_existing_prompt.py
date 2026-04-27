"""Prompt surface tests for existing-project onboarding entrypoint."""

from __future__ import annotations

from pathlib import Path


def _prompt_text() -> str:
    path = Path(__file__).resolve().parents[1] / "prompts" / "workflow.onboard.existing.md"
    assert path.is_file(), "prompts/workflow.onboard.existing.md is missing"
    return path.read_text(encoding="utf-8")


def test_existing_onboard_prompt_has_expected_metadata_and_stage():
    text = _prompt_text()
    assert "stage: onboard_existing" in text
    assert "recommended_model_class: frontier_model" in text


def test_existing_onboard_prompt_contains_mandatory_cli_steps():
    text = _prompt_text()
    assert "grain --repo <REPO_ROOT> onboard <REPO_ROOT> --format json" in text
    assert "grain --repo <REPO_ROOT> docs validate" in text
    assert "grain --repo <REPO_ROOT> --format json workflow next" in text
    assert "grain --repo <REPO_ROOT> task validate --id <TASK-ID>" in text

