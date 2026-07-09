# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Tests for the file-backed recipe run store (docs/recipes/runs/<run-id>/)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from grain.domain.recipe import parse_recipe
from grain.domain.recipe_run import RecipeRun
from grain.services import recipe_store


def _definition():
    return parse_recipe(
        {
            "apiVersion": "grain.recipe/v2",
            "id": "research-brief",
            "name": "Research Brief",
            "description": "Produce a sourced research brief on a topic",
            "category": "research",
            "supervision": "gated",
            "params": [
                {"id": "topic", "label": "Topic", "required": True, "type": "string"},
            ],
            "steps": [
                {
                    "id": "intake",
                    "prompt": "steps/intake.md",
                    "inputs": ["params"],
                    "output": "01-intake.md",
                },
                {
                    "id": "self_check",
                    "prompt": "steps/self_check.md",
                    "inputs": ["intake"],
                    "output": "05-review.md",
                    "gate": "review",
                },
                {
                    "id": "format",
                    "prompt": "steps/format.md",
                    "inputs": ["self_check"],
                    "output": "brief.md",
                },
            ],
            "final": "brief.md",
        }
    )


# ── create_run ─────────────────────────────────────────────────────────────────

def test_create_run_writes_initial_run_json(tmp_path: Path) -> None:
    definition = _definition()
    run = recipe_store.create_run(
        tmp_path, definition, {"topic": "GLP-1 obesity market"}, mode="operator"
    )

    path = tmp_path / "docs/recipes/runs" / run.run_id / "run.json"
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["apiVersion"] == "grain.recipe-run/v1"
    assert data["status"] == "pending"
    assert data["cursor"] == "intake"
    assert data["mode"] == "operator"
    assert data["supervision"] == "gated"
    assert data["recipe_apiVersion"] == "grain.recipe/v2"
    assert data["params"] == {"topic": "GLP-1 obesity market"}
    assert [s["id"] for s in data["steps"]] == ["intake", "self_check", "format"]
    assert all(s["status"] == "pending" for s in data["steps"])

    # the declared gate is carried onto the step record
    self_check = next(s for s in data["steps"] if s["id"] == "self_check")
    assert self_check["gate"] == "review"
    assert data["created"] and data["updated"]


def test_create_run_auto_mode(tmp_path: Path) -> None:
    run = recipe_store.create_run(tmp_path, _definition(), {"topic": "x"}, mode="auto")
    assert run.mode == "auto"


def test_create_run_rejects_bad_mode(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        recipe_store.create_run(tmp_path, _definition(), {}, mode="gated")


# ── run-id allocation ──────────────────────────────────────────────────────────

def test_run_ids_monotonic_and_zero_padded(tmp_path: Path) -> None:
    definition = _definition()
    first = recipe_store.create_run(tmp_path, definition, {"topic": "a"})
    second = recipe_store.create_run(tmp_path, definition, {"topic": "b"})

    assert first.run_id == "research-brief-0001"
    assert second.run_id == "research-brief-0002"

    first_dir = tmp_path / "docs/recipes/runs" / first.run_id
    second_dir = tmp_path / "docs/recipes/runs" / second.run_id
    assert first_dir.is_dir() and second_dir.is_dir()
    assert first_dir != second_dir


def test_next_run_id_isolated_per_recipe(tmp_path: Path) -> None:
    recipe_store.create_run(tmp_path, _definition(), {"topic": "a"})
    assert recipe_store.next_run_id(tmp_path, "other-recipe") == "other-recipe-0001"


# ── load / save round-trip (resume) ────────────────────────────────────────────

def test_load_run_equals_saved_run(tmp_path: Path) -> None:
    run = recipe_store.create_run(tmp_path, _definition(), {"topic": "a"})
    run.status = "awaiting_gate"
    run.cursor = "self_check"
    run.step("intake").status = "done"
    run.step("intake").artifact = "01-intake.md"
    run.step("intake").attempts = 1
    recipe_store.save_run(tmp_path, run)

    reloaded = recipe_store.load_run(tmp_path, run.run_id)
    assert reloaded == run


def test_load_run_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        recipe_store.load_run(tmp_path, "research-brief-9999")


def test_load_run_rejects_unsupported_major(tmp_path: Path) -> None:
    run = recipe_store.create_run(tmp_path, _definition(), {"topic": "a"})
    path = tmp_path / "docs/recipes/runs" / run.run_id / "run.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["apiVersion"] = "grain.recipe-run/v2"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        recipe_store.load_run(tmp_path, run.run_id)


def test_list_runs(tmp_path: Path) -> None:
    a = recipe_store.create_run(tmp_path, _definition(), {"topic": "a"})
    b = recipe_store.create_run(tmp_path, _definition(), {"topic": "b"})
    assert set(recipe_store.list_runs(tmp_path)) == {a.run_id, b.run_id}


# ── write_step_artifact: artifact-first, atomic ────────────────────────────────

def test_write_step_artifact_writes_artifact_then_run_json(tmp_path: Path) -> None:
    run = recipe_store.create_run(tmp_path, _definition(), {"topic": "a"})
    run.step("intake").status = "done"
    recipe_store.write_step_artifact(
        tmp_path, run, "intake", "# Intake\n", "01-intake.md"
    )

    run_d = tmp_path / "docs/recipes/runs" / run.run_id
    assert (run_d / "01-intake.md").read_text(encoding="utf-8") == "# Intake\n"

    data = json.loads((run_d / "run.json").read_text(encoding="utf-8"))
    intake = next(s for s in data["steps"] if s["id"] == "intake")
    assert intake["artifact"] == "01-intake.md"
    assert intake["status"] == "done"


def test_write_step_artifact_unknown_step_raises(tmp_path: Path) -> None:
    run = recipe_store.create_run(tmp_path, _definition(), {"topic": "a"})
    with pytest.raises(KeyError):
        recipe_store.write_step_artifact(tmp_path, run, "nope", "x", "x.md")


@pytest.mark.parametrize("evil", ["../escape.md", "/etc/passwd", "a/../../escape.md"])
def test_write_step_artifact_rejects_path_traversal(tmp_path: Path, evil) -> None:
    # F1: the defensive join-site guard refuses an artifact name that escapes the
    # run dir, and writes nothing outside it.
    from grain.domain.recipe import RecipeSchemaError

    run = recipe_store.create_run(tmp_path, _definition(), {"topic": "a"})
    run.step("intake").status = "done"
    with pytest.raises(RecipeSchemaError):
        recipe_store.write_step_artifact(tmp_path, run, "intake", "x", evil)
    # nothing was written outside the run dir.
    assert not (tmp_path / "escape.md").exists()
    assert not (tmp_path.parent / "escape.md").exists()


def test_run_json_write_failure_leaves_prior_intact(
    tmp_path: Path, monkeypatch
) -> None:
    """Fault-inject the run.json rename: prior run.json stays intact + parses,
    and the artifact written first is present on disk."""
    run = recipe_store.create_run(tmp_path, _definition(), {"topic": "a"})
    run_d = tmp_path / "docs/recipes/runs" / run.run_id
    run_json = run_d / "run.json"

    before = run_json.read_text(encoding="utf-8")

    real_replace = recipe_store.os.replace

    def faulty_replace(src, dst):
        if str(dst).endswith("run.json"):
            raise OSError("simulated crash during run.json rename")
        return real_replace(src, dst)

    monkeypatch.setattr(recipe_store.os, "replace", faulty_replace)

    run.step("intake").status = "done"
    with pytest.raises(OSError):
        recipe_store.write_step_artifact(
            tmp_path, run, "intake", "# Intake\n", "01-intake.md"
        )

    # The artifact landed first (before the run.json failure).
    assert (run_d / "01-intake.md").read_text(encoding="utf-8") == "# Intake\n"

    # Prior run.json is byte-for-byte intact and still parses.
    after = run_json.read_text(encoding="utf-8")
    assert after == before
    assert RecipeRun.from_dict(json.loads(after))  # not truncated
