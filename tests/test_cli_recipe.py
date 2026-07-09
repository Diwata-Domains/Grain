# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Tests for the recipe CLI surface: ``list`` / ``show`` / ``scaffold``.

These tests are independent of the bundled ``research-brief`` recipe (owned by
P34-T06): every test scaffolds (or hand-writes) a fixture recipe into a temp
workspace first, then asserts against it. The commands are read-only/scaffold
only — they must never create a run directory or touch ``run.json``.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from click.testing import CliRunner

from grain.cli import main, recipe_group


def _scaffold(runner: CliRunner, root: Path, recipe_id: str, *args) -> None:
    result = runner.invoke(
        main, ["--repo", str(root), "recipe", "scaffold", recipe_id, *args]
    )
    assert result.exit_code == 0, result.output


def _write_recipe(root: Path, recipe: dict) -> str:
    recipe_id = recipe["id"]
    recipe_dir = root / "docs" / "recipes" / recipe_id
    (recipe_dir / "steps").mkdir(parents=True, exist_ok=True)
    (recipe_dir / "recipe.yaml").write_text(
        yaml.safe_dump(recipe, sort_keys=False), encoding="utf-8"
    )
    for step in recipe["steps"]:
        (recipe_dir / step["prompt"]).write_text("stub\n", encoding="utf-8")
    return recipe_id


def _gated_fixture() -> dict:
    """3-step fixture; the middle step declares a review gate."""
    return {
        "apiVersion": "grain.recipe/v2",
        "id": "gated-fixture",
        "name": "Gated Fixture",
        "description": "fixture with one gated step",
        "category": "research",
        "supervision": "gated",
        "params": [{"id": "topic", "label": "Topic", "required": True, "type": "string"}],
        "steps": [
            {
                "id": "intake",
                "name": "Frame",
                "prompt": "steps/intake.md",
                "inputs": ["params"],
                "output": "01-intake.md",
            },
            {
                "id": "review",
                "name": "Self check",
                "prompt": "steps/review.md",
                "inputs": ["intake"],
                "output": "02-review.md",
                "gate": "review",
            },
            {
                "id": "final",
                "prompt": "steps/final.md",
                "inputs": ["review"],
                "output": "brief.md",
            },
        ],
        "final": "brief.md",
    }


# --- group registration ------------------------------------------------------
def test_recipe_group_registered_and_lists_subcommands():
    runner = CliRunner()
    result = runner.invoke(main, ["recipe", "--help"])
    assert result.exit_code == 0
    for sub in ("list", "show", "scaffold"):
        assert sub in result.output
    # importable from grain.cli
    assert recipe_group.name == "recipe"


# --- list --------------------------------------------------------------------
def test_list_text_shows_workspace_fixture(tmp_path):
    runner = CliRunner()
    _scaffold(runner, tmp_path, "demo")

    result = runner.invoke(main, ["--repo", str(tmp_path), "recipe", "list"])
    assert result.exit_code == 0, result.output
    assert "demo" in result.output
    assert "workspace" in result.output
    # The scaffold has 2 steps; the row should reflect that.
    assert "SOURCE" in result.output


def test_list_json_fixture_is_workspace_with_step_count(tmp_path):
    runner = CliRunner()
    _scaffold(runner, tmp_path, "demo")

    result = runner.invoke(
        main, ["--repo", str(tmp_path), "--format", "json", "recipe", "list"]
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert isinstance(data, list)
    demo = next(item for item in data if item["id"] == "demo")
    assert demo["source"] == "workspace"
    assert demo["step_count"] == 2
    assert set(demo) >= {"id", "name", "category", "source", "step_count"}
    # No specific bundled recipe is required, but any bundled rows are tagged.
    for item in data:
        assert item["source"] in {"bundled", "workspace"}


# --- show --------------------------------------------------------------------
def test_show_json_shape_and_gate(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _gated_fixture())

    result = runner.invoke(
        main,
        ["--repo", str(tmp_path), "--format", "json", "recipe", "show", "gated-fixture"],
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["apiVersion"] == "grain.recipe/v2"
    assert data["id"] == "gated-fixture"

    steps = {s["id"]: s for s in data["steps"]}
    # Every step carries id/inputs/output and NEVER prompt.
    for step in data["steps"]:
        assert {"id", "inputs", "output"} <= set(step)
        assert "prompt" not in step
    # Gated step carries gate; non-gated step omits it.
    assert steps["review"]["gate"] == "review"
    assert "gate" not in steps["intake"]
    # Params surfaced.
    assert data["params"][0]["id"] == "topic"
    assert data["params"][0]["required"] is True


def test_show_text_lists_params_and_steps(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _gated_fixture())

    result = runner.invoke(
        main, ["--repo", str(tmp_path), "recipe", "show", "gated-fixture"]
    )
    assert result.exit_code == 0, result.output
    assert "topic" in result.output
    assert "intake" in result.output
    assert "review" in result.output
    assert "gate=review" in result.output


def test_show_unknown_recipe_exits_nonzero_no_traceback(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(tmp_path), "recipe", "show", "does-not-exist"]
    )
    assert result.exit_code != 0
    assert "Traceback" not in result.output
    assert "does-not-exist" in result.output
    assert result.exception is None or isinstance(result.exception, SystemExit)


# --- scaffold ----------------------------------------------------------------
def test_scaffold_creates_loadable_recipe(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(tmp_path), "recipe", "scaffold", "demo"]
    )
    assert result.exit_code == 0, result.output

    recipe_yaml = tmp_path / "docs" / "recipes" / "demo" / "recipe.yaml"
    assert recipe_yaml.is_file()
    assert (tmp_path / "docs" / "recipes" / "demo" / "steps" / "intake.md").is_file()
    assert (tmp_path / "docs" / "recipes" / "demo" / "steps" / "draft.md").is_file()
    # Valid grain.recipe/v2.
    parsed = yaml.safe_load(recipe_yaml.read_text(encoding="utf-8"))
    assert parsed["apiVersion"] == "grain.recipe/v2"
    # No run directory was created.
    assert not (tmp_path / "docs" / "recipes" / "runs").exists()

    # show on the scaffolded recipe succeeds.
    show = runner.invoke(main, ["--repo", str(tmp_path), "recipe", "show", "demo"])
    assert show.exit_code == 0, show.output


def test_scaffold_json_payload(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        main, ["--repo", str(tmp_path), "--format", "json", "recipe", "scaffold", "demo"]
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["id"] == "demo"
    assert data["path"] == "docs/recipes/demo"
    assert data["created"] is True
    assert "recipe.yaml" in data["files"]


def test_scaffold_refuses_overwrite_without_force(tmp_path):
    runner = CliRunner()
    _scaffold(runner, tmp_path, "demo")

    recipe_yaml = tmp_path / "docs" / "recipes" / "demo" / "recipe.yaml"
    # Mutate the file so we can detect an accidental overwrite.
    recipe_yaml.write_text("# sentinel\n" + recipe_yaml.read_text(), encoding="utf-8")
    before = recipe_yaml.read_text(encoding="utf-8")

    result = runner.invoke(main, ["--repo", str(tmp_path), "recipe", "scaffold", "demo"])
    assert result.exit_code != 0
    assert "Traceback" not in result.output
    assert recipe_yaml.read_text(encoding="utf-8") == before  # unchanged

    # --force overwrites.
    forced = runner.invoke(
        main, ["--repo", str(tmp_path), "recipe", "scaffold", "demo", "--force"]
    )
    assert forced.exit_code == 0, forced.output
    assert recipe_yaml.read_text(encoding="utf-8") != before
