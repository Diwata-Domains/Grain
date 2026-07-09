# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Tests for the recipe definition model + grain.recipe/v2 parser."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from grain.domain.recipe import (
    RECIPE_API_VERSION,
    RecipeDefinition,
    RecipeSchemaError,
    load_recipe,
    parse_recipe,
)


def _research_brief() -> dict:
    """The spec §2.1 research-brief example as a parsed-YAML dict."""
    return {
        "apiVersion": "grain.recipe/v2",
        "id": "research-brief",
        "name": "Research Brief",
        "description": "Produce a sourced research brief on a topic",
        "category": "research",
        "workspace_kind": "knowledge",
        "supervision": "gated",
        "params": [
            {"id": "topic", "label": "Topic", "required": True, "type": "string"},
        ],
        "steps": [
            {
                "id": "intake",
                "name": "Frame the topic",
                "prompt": "steps/intake.md",
                "inputs": ["params"],
                "output": "01-intake.md",
            },
            {
                "id": "gather",
                "name": "Gather sources",
                "prompt": "steps/gather.md",
                "inputs": ["params", "intake"],
                "output": "02-sources.md",
            },
            {
                "id": "outline",
                "prompt": "steps/outline.md",
                "inputs": ["intake", "gather"],
                "output": "03-outline.md",
            },
            {
                "id": "draft",
                "prompt": "steps/draft.md",
                "inputs": ["outline", "gather"],
                "output": "04-draft.md",
            },
            {
                "id": "self_check",
                "prompt": "steps/self_check.md",
                "inputs": ["draft", "gather"],
                "output": "05-review.md",
                "gate": "review",
            },
            {
                "id": "format",
                "prompt": "steps/format.md",
                "inputs": ["draft", "self_check"],
                "output": "brief.md",
            },
        ],
        "final": "brief.md",
    }


# 1. Happy path -----------------------------------------------------------------


def test_research_brief_happy_path():
    recipe = parse_recipe(_research_brief())
    assert isinstance(recipe, RecipeDefinition)
    assert recipe.id == "research-brief"
    assert recipe.name == "Research Brief"
    assert recipe.final == "brief.md"
    assert recipe.supervision == "gated"
    assert recipe.category == "research"

    # 6 ordered steps, index-aligned with the file.
    assert [s.id for s in recipe.steps] == [
        "intake",
        "gather",
        "outline",
        "draft",
        "self_check",
        "format",
    ]
    assert len(recipe.steps) == 6

    # one required param.
    assert len(recipe.params) == 1
    param = recipe.params[0]
    assert param.id == "topic"
    assert param.required is True

    # gate round-trips on the self_check step.
    self_check = next(s for s in recipe.steps if s.id == "self_check")
    assert self_check.gate == "review"


# 2. apiVersion gating ----------------------------------------------------------


def test_api_version_constant():
    assert RECIPE_API_VERSION == "grain.recipe/v2"


@pytest.mark.parametrize("bad_version", ["grain.recipe/v1", "grain.recipe/v3", "v2"])
def test_api_version_other_value_rejected(bad_version):
    data = _research_brief()
    data["apiVersion"] = bad_version
    with pytest.raises(RecipeSchemaError) as exc:
        parse_recipe(data)
    assert bad_version in str(exc.value)


def test_api_version_missing_rejected():
    data = _research_brief()
    del data["apiVersion"]
    with pytest.raises(RecipeSchemaError) as exc:
        parse_recipe(data)
    assert "apiVersion" in str(exc.value)


def test_api_version_v2_accepted():
    data = _research_brief()
    data["apiVersion"] = "grain.recipe/v2"
    assert parse_recipe(data).id == "research-brief"


# 2b. supervision ---------------------------------------------------------------


@pytest.mark.parametrize("level", ["supervised", "gated", "autonomous"])
def test_supervision_roundtrips(level):
    data = _research_brief()
    data["supervision"] = level
    assert parse_recipe(data).supervision == level


def test_supervision_defaults_to_gated_when_absent():
    data = _research_brief()
    del data["supervision"]
    assert parse_recipe(data).supervision == "gated"


def test_supervision_invalid_value_rejected():
    data = _research_brief()
    data["supervision"] = "operator"
    with pytest.raises(RecipeSchemaError) as exc:
        parse_recipe(data)
    assert "operator" in str(exc.value)


# 3 / 4 / 5. unknown-key rejection ---------------------------------------------


def test_unknown_top_level_key_rejected():
    data = _research_brief()
    data["foo"] = "bar"
    with pytest.raises(RecipeSchemaError) as exc:
        parse_recipe(data)
    assert "foo" in str(exc.value)


def test_unknown_per_step_key_rejected():
    data = _research_brief()
    data["steps"][0]["widget"] = 1
    with pytest.raises(RecipeSchemaError) as exc:
        parse_recipe(data)
    assert "widget" in str(exc.value)


def test_unknown_per_param_key_rejected():
    data = _research_brief()
    data["params"][0]["gizmo"] = True
    with pytest.raises(RecipeSchemaError) as exc:
        parse_recipe(data)
    assert "gizmo" in str(exc.value)


def test_accepted_and_ignored_keys_parse():
    # workspace_kind (top-level) + adapter/model (per-step) are in the allow-set.
    data = _research_brief()
    data["steps"][0]["adapter"] = "knowledge"
    data["steps"][0]["model"] = "opus"
    recipe = parse_recipe(data)
    assert recipe.id == "research-brief"


# 6. inputs reference integrity -------------------------------------------------


def test_forward_input_reference_rejected():
    data = _research_brief()
    # intake (first step) references a later step.
    data["steps"][0]["inputs"] = ["params", "gather"]
    with pytest.raises(RecipeSchemaError) as exc:
        parse_recipe(data)
    assert "gather" in str(exc.value)


def test_unknown_input_reference_rejected():
    data = _research_brief()
    data["steps"][1]["inputs"] = ["params", "does_not_exist"]
    with pytest.raises(RecipeSchemaError) as exc:
        parse_recipe(data)
    assert "does_not_exist" in str(exc.value)


def test_self_input_reference_rejected():
    data = _research_brief()
    data["steps"][0]["inputs"] = ["intake"]
    with pytest.raises(RecipeSchemaError):
        parse_recipe(data)


def test_params_and_earlier_input_accepted():
    data = _research_brief()
    data["steps"][1]["inputs"] = ["params", "intake"]
    assert parse_recipe(data).steps[1].inputs == ["params", "intake"]


# 7. final resolves -------------------------------------------------------------


def test_final_with_no_matching_output_rejected():
    data = _research_brief()
    data["final"] = "nonexistent.md"
    with pytest.raises(RecipeSchemaError) as exc:
        parse_recipe(data)
    assert "nonexistent.md" in str(exc.value)


# 8. gate values ----------------------------------------------------------------


def test_gate_review_parses():
    data = _research_brief()
    data["steps"][0]["gate"] = "review"
    assert parse_recipe(data).steps[0].gate == "review"


def test_gate_none_parses():
    data = _research_brief()
    data["steps"][0]["gate"] = "none"
    assert parse_recipe(data).steps[0].gate == "none"


def test_gate_invalid_value_rejected():
    data = _research_brief()
    data["steps"][0]["gate"] = "approve"
    with pytest.raises(RecipeSchemaError) as exc:
        parse_recipe(data)
    assert "approve" in str(exc.value)


# 9. duplicate ids + missing required keys -------------------------------------


def test_duplicate_step_id_rejected():
    data = _research_brief()
    data["steps"][1]["id"] = "intake"
    with pytest.raises(RecipeSchemaError) as exc:
        parse_recipe(data)
    assert "intake" in str(exc.value)


@pytest.mark.parametrize(
    "bad_output",
    [
        "/etc/passwd",            # absolute
        "../escape.md",           # parent traversal
        "sub/../../escape.md",    # traversal via subdir
        "..",                     # bare parent
        "nested\\win.md",         # backslash separator
    ],
)
def test_unsafe_step_output_rejected(bad_output):
    # F1: a step `output` must be a safe relative filename inside the run dir.
    data = _research_brief()
    data["steps"][0]["output"] = bad_output
    with pytest.raises(RecipeSchemaError) as exc:
        parse_recipe(data)
    assert "output" in str(exc.value)


def test_safe_nested_step_output_accepted():
    # A relative name in a subdir (no traversal) is allowed.
    data = _research_brief()
    data["steps"][0]["output"] = "sub/01-intake.md"
    assert parse_recipe(data).steps[0].output == "sub/01-intake.md"


def test_duplicate_step_output_rejected():
    # F3: two steps declaring the same `output:` filename is rejected, like ids.
    data = _research_brief()
    data["steps"][1]["output"] = data["steps"][0]["output"]
    with pytest.raises(RecipeSchemaError) as exc:
        parse_recipe(data)
    assert data["steps"][0]["output"] in str(exc.value)


def test_missing_required_step_key_rejected():
    data = _research_brief()
    del data["steps"][0]["output"]
    with pytest.raises(RecipeSchemaError) as exc:
        parse_recipe(data)
    assert "output" in str(exc.value)


def test_missing_steps_rejected():
    data = _research_brief()
    data["steps"] = []
    with pytest.raises(RecipeSchemaError):
        parse_recipe(data)


def test_invalid_category_rejected():
    data = _research_brief()
    data["category"] = "marketing"
    with pytest.raises(RecipeSchemaError) as exc:
        parse_recipe(data)
    assert "marketing" in str(exc.value)


# 10. load_recipe round-trip ----------------------------------------------------


def test_load_recipe_roundtrip(tmp_path: Path):
    data = _research_brief()
    recipe_path = tmp_path / "recipe.yaml"
    recipe_path.write_text(yaml.safe_dump(data), encoding="utf-8")

    loaded = load_recipe(recipe_path)
    expected = parse_recipe(copy.deepcopy(data))
    assert loaded == expected


def test_load_recipe_accepts_str_path(tmp_path: Path):
    recipe_path = tmp_path / "recipe.yaml"
    recipe_path.write_text(yaml.safe_dump(_research_brief()), encoding="utf-8")
    assert load_recipe(str(recipe_path)).id == "research-brief"


def test_load_recipe_missing_file_raises():
    with pytest.raises(RecipeSchemaError):
        load_recipe("/nonexistent/path/recipe.yaml")


def test_load_recipe_invalid_yaml_raises(tmp_path: Path):
    recipe_path = tmp_path / "recipe.yaml"
    recipe_path.write_text("key: [unclosed", encoding="utf-8")
    with pytest.raises(RecipeSchemaError):
        load_recipe(recipe_path)


def test_load_recipe_empty_file_raises(tmp_path: Path):
    recipe_path = tmp_path / "recipe.yaml"
    recipe_path.write_text("", encoding="utf-8")
    with pytest.raises(RecipeSchemaError):
        load_recipe(recipe_path)
