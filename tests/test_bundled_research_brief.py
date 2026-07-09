# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Tests for the bundled ``research-brief`` recipe (P34-T06, data only).

Covers schema validity via the T01 v2 parser, presence of the seven shipped
files, required template-token usage, and packaging inclusion verified against a
built wheel (NOT the source tree).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest
import yaml

from grain.domain.recipe import load_recipe

# Repo-relative source location of the bundled recipe (used only by the
# source-tree-facing tests; the packaging test deliberately ignores this).
_RECIPE_DIR = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "grain"
    / "data"
    / "recipes"
    / "research-brief"
)
_RECIPE_YAML = _RECIPE_DIR / "recipe.yaml"

_STEP_FILES = [
    "intake.md",
    "gather.md",
    "outline.md",
    "draft.md",
    "self_check.md",
    "format.md",
]

_EXPECTED_STEPS = [
    ("intake", ["params"], "01-intake.md"),
    ("gather", ["params", "intake"], "02-sources.md"),
    ("outline", ["intake", "gather"], "03-outline.md"),
    ("draft", ["outline", "gather"], "04-draft.md"),
    ("self_check", ["draft", "gather"], "05-review.md"),
    ("format", ["draft", "self_check"], "brief.md"),
]


# --------------------------------------------------------------------------- #
# 1. Schema validity (via the T01 v2 parser)
# --------------------------------------------------------------------------- #
def test_recipe_parses_with_zero_errors():
    recipe = load_recipe(_RECIPE_YAML)
    assert recipe.id == "research-brief"
    assert recipe.supervision == "autonomous"
    assert recipe.category == "research"
    assert recipe.final == "brief.md"


def test_recipe_api_version_is_v2():
    raw = yaml.safe_load(_RECIPE_YAML.read_text(encoding="utf-8"))
    assert raw["apiVersion"] == "grain.recipe/v2"


def test_recipe_has_six_steps_in_order():
    recipe = load_recipe(_RECIPE_YAML)
    assert [step.id for step in recipe.steps] == [
        "intake",
        "gather",
        "outline",
        "draft",
        "self_check",
        "format",
    ]


def test_recipe_step_inputs_and_outputs_match_spec():
    recipe = load_recipe(_RECIPE_YAML)
    actual = [(s.id, s.inputs, s.output) for s in recipe.steps]
    assert actual == _EXPECTED_STEPS


def test_recipe_final_equals_last_step_output():
    recipe = load_recipe(_RECIPE_YAML)
    assert recipe.final == recipe.steps[-1].output == "brief.md"


def test_recipe_has_single_topic_param():
    recipe = load_recipe(_RECIPE_YAML)
    assert [p.id for p in recipe.params] == ["topic"]
    topic = recipe.params[0]
    assert topic.required is True
    assert topic.type == "string"


def test_every_step_prompt_resolves_to_existing_file():
    recipe = load_recipe(_RECIPE_YAML)
    for step in recipe.steps:
        prompt_path = _RECIPE_DIR / step.prompt
        assert prompt_path.is_file(), f"missing prompt file for step {step.id!r}"


# --------------------------------------------------------------------------- #
# 2. File presence + no deferred/gate keys
# --------------------------------------------------------------------------- #
def test_all_seven_files_present():
    assert _RECIPE_YAML.is_file()
    for name in _STEP_FILES:
        assert (_RECIPE_DIR / "steps" / name).is_file(), name


def test_no_gate_or_deferred_keys():
    raw = yaml.safe_load(_RECIPE_YAML.read_text(encoding="utf-8"))
    assert "workspace_kind" not in raw
    for step in raw["steps"]:
        assert "gate" not in step, f"step {step['id']} declares a gate"
        assert "adapter" not in step, f"step {step['id']} declares an adapter"
        assert "model" not in step, f"step {step['id']} declares a model"


# --------------------------------------------------------------------------- #
# 3. Token references
# --------------------------------------------------------------------------- #
def test_intake_references_topic_token():
    text = (_RECIPE_DIR / "steps" / "intake.md").read_text(encoding="utf-8")
    assert "{{topic}}" in text


def test_a_downstream_prompt_references_a_steps_token():
    downstream = ["gather.md", "outline.md", "draft.md", "self_check.md", "format.md"]
    found = any(
        "{{steps." in (_RECIPE_DIR / "steps" / name).read_text(encoding="utf-8")
        for name in downstream
    )
    assert found, "no downstream prompt references a {{steps.<id>}} token"


def test_each_step_prompt_references_its_declared_inputs():
    """Authoring-target check: each prompt references all of its inputs."""
    recipe = load_recipe(_RECIPE_YAML)
    for step in recipe.steps:
        text = (_RECIPE_DIR / step.prompt).read_text(encoding="utf-8")
        for ref in step.inputs:
            token = "{{topic}}" if ref == "params" else f"{{{{steps.{ref}}}}}"
            assert token in text, (
                f"step {step.id!r} prompt missing token {token!r} for input {ref!r}"
            )


# --------------------------------------------------------------------------- #
# 4. Packaging (built artifact, NOT the source tree)
# --------------------------------------------------------------------------- #
def _build_wheel(project_root: Path, out_dir: Path) -> subprocess.CompletedProcess:
    """Build a wheel, preferring ``uv build`` and falling back to ``python -m build``."""
    if shutil.which("uv"):
        return subprocess.run(
            ["uv", "build", "--wheel", "--out-dir", str(out_dir)],
            cwd=str(project_root),
            capture_output=True,
            text=True,
        )
    return subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(out_dir)],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )


def test_recipe_files_present_in_built_wheel(tmp_path):
    project_root = Path(__file__).resolve().parents[1]
    out_dir = tmp_path / "wheel"
    result = _build_wheel(project_root, out_dir)
    if result.returncode != 0:
        pytest.skip(
            "wheel build unavailable in this environment:\n"
            f"{result.stdout}\n{result.stderr}"
        )

    wheels = list(out_dir.glob("*.whl"))
    assert wheels, "build produced no wheel"
    with zipfile.ZipFile(wheels[0]) as zf:
        names = set(zf.namelist())

    expected = ["grain/data/recipes/research-brief/recipe.yaml"] + [
        f"grain/data/recipes/research-brief/steps/{name}" for name in _STEP_FILES
    ]
    missing = [name for name in expected if name not in names]
    assert not missing, f"wheel is missing recipe files: {missing}"
