# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Tests for the RecipeRun / RecipeStepRecord run-state model."""

from __future__ import annotations

import pytest

from grain.domain.recipe_run import (
    RUN_API_VERSION,
    VALID_MODES,
    RecipeRun,
    RecipeStepRecord,
)


def _run(**overrides) -> RecipeRun:
    base = dict(
        run_id="research-brief-0001",
        recipe="research-brief",
        recipe_api_version="grain.recipe/v2",
        params={"topic": "GLP-1 obesity market"},
        mode="operator",
        supervision="gated",
        status="pending",
        cursor="intake",
        steps=[
            RecipeStepRecord(id="intake", status="pending"),
            RecipeStepRecord(id="format", status="pending"),
        ],
    )
    base.update(overrides)
    return RecipeRun(**base)


# ── construction + validation ──────────────────────────────────────────────────

def test_valid_run_constructs() -> None:
    run = _run()
    assert run.api_version == RUN_API_VERSION
    assert run.cursor == "intake"


def test_awaiting_input_is_a_valid_status() -> None:
    record = RecipeStepRecord(id="intake", status="awaiting_input")
    assert record.status == "awaiting_input"
    run = _run(status="awaiting_input")
    assert run.status == "awaiting_input"


def test_invalid_step_status_raises() -> None:
    with pytest.raises(ValueError):
        RecipeStepRecord(id="intake", status="bogus")


def test_invalid_run_status_raises() -> None:
    with pytest.raises(ValueError):
        _run(status="bogus")


def test_invalid_mode_raises() -> None:
    with pytest.raises(ValueError):
        _run(mode="supervised")  # a supervision value is NOT a mode
    assert "supervised" not in VALID_MODES


def test_empty_step_id_raises() -> None:
    with pytest.raises(ValueError):
        RecipeStepRecord(id="")


def test_negative_attempts_raises() -> None:
    with pytest.raises(ValueError):
        RecipeStepRecord(id="intake", attempts=-1)


def test_invalid_step_gate_raises() -> None:
    with pytest.raises(ValueError):
        RecipeStepRecord(id="intake", gate="bogus")


def test_invalid_supervision_raises() -> None:
    with pytest.raises(ValueError):
        _run(supervision="bogus")


def test_empty_run_id_raises() -> None:
    with pytest.raises(ValueError):
        _run(run_id="")


def test_no_steps_raises() -> None:
    with pytest.raises(ValueError):
        _run(steps=[], cursor="intake")


def test_duplicate_step_ids_raise() -> None:
    with pytest.raises(ValueError):
        _run(
            steps=[
                RecipeStepRecord(id="intake"),
                RecipeStepRecord(id="intake"),
            ],
            cursor="intake",
        )


def test_cursor_not_among_steps_raises() -> None:
    with pytest.raises(ValueError):
        _run(cursor="nope")


def test_step_lookup() -> None:
    run = _run()
    assert run.step("format").id == "format"
    with pytest.raises(KeyError):
        run.step("missing")


# ── round-trip ─────────────────────────────────────────────────────────────────

def test_round_trip_lossless_with_gate_and_mixed_status() -> None:
    run = RecipeRun(
        run_id="research-brief-0001",
        recipe="research-brief",
        recipe_api_version="grain.recipe/v2",
        params={"topic": "GLP-1 obesity market"},
        mode="operator",
        supervision="gated",
        status="awaiting_gate",
        cursor="self_check",
        created="2026-06-26T17:00:00Z",
        updated="2026-06-26T17:12:00Z",
        steps=[
            RecipeStepRecord(id="intake", status="done", artifact="01-intake.md", attempts=1),
            RecipeStepRecord(id="gather", status="done", artifact="02-sources.md", attempts=1),
            RecipeStepRecord(id="outline", status="done", artifact="03-outline.md", attempts=1),
            RecipeStepRecord(id="draft", status="done", artifact="04-draft.md", attempts=1),
            RecipeStepRecord(
                id="self_check",
                status="awaiting_gate",
                artifact="05-review.md",
                attempts=1,
                gate="review",
            ),
            RecipeStepRecord(id="format", status="pending"),
        ],
    )
    payload = run.to_dict()
    assert payload["apiVersion"] == "grain.recipe-run/v1"
    assert payload["mode"] == "operator"
    assert payload["supervision"] == "gated"

    restored = RecipeRun.from_dict(payload)
    assert restored == run
    assert restored.step("self_check").gate == "review"
    assert restored.step("format").gate == "none"


def test_pending_step_omits_default_fields() -> None:
    record = RecipeStepRecord(id="format", status="pending")
    assert record.to_dict() == {"id": "format", "status": "pending"}


def test_gate_emitted_only_when_not_default() -> None:
    plain = RecipeStepRecord(id="intake", status="done", attempts=1)
    assert "gate" not in plain.to_dict()
    gated = RecipeStepRecord(id="self_check", status="awaiting_gate", gate="review")
    assert gated.to_dict()["gate"] == "review"


def test_from_dict_rejects_wrong_major() -> None:
    payload = _run().to_dict()
    payload["apiVersion"] = "grain.recipe-run/v2"
    with pytest.raises(ValueError):
        RecipeRun.from_dict(payload)


def test_from_dict_rejects_missing_api_version() -> None:
    payload = _run().to_dict()
    del payload["apiVersion"]
    with pytest.raises(ValueError):
        RecipeRun.from_dict(payload)
