# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""Tests for the pre-staged recipe-demo workspace (P34-T07).

This packet ships demo *content*: a pre-staged Grain workspace under
``examples/recipe-demo/`` carrying

  * a minimal ``grain.toml`` marker with ``workspace_kind`` deliberately omitted
    (exercising the recipe engine's graceful-degradation path, spec §6),
  * the bundled ``research-brief`` recipe copied verbatim from P34-T06,
  * a committed reference run ``research-brief-0001`` (``status: done``,
    ``cursor: format``, 6 artifacts) proving the finished structure offline, and
  * a venue-style runbook ``README.md``.

These tests assert the committed content and that the PARALLEL recipe engine
drives a *fresh* run on a copy of the workspace (operator mode: renders step 1
and pauses at ``awaiting_input`` without writing any artifact). They never touch
the SDLC packet loop. The committed reference run is never mutated: live-run
checks operate on a temp copy of the workspace.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

import grain
from grain.domain.recipe import load_recipe
from grain.domain.recipe_run import (
    VALID_MODES,
    VALID_SUPERVISION,
    RecipeRun,
)
from grain.services import recipe_store
from grain.services.recipe_service import RecipeService

# --- locations ---------------------------------------------------------------
_PRODUCT_ROOT = Path(__file__).resolve().parents[1]
DEMO = _PRODUCT_ROOT / "examples" / "recipe-demo"
BUNDLED = Path(grain.__file__).resolve().parent / "data" / "recipes" / "research-brief"

REFERENCE_RUN = DEMO / "docs" / "recipes" / "runs" / "research-brief-0001"
DEMO_RECIPE = DEMO / "docs" / "recipes" / "research-brief"

STEP_FILES = (
    "intake.md",
    "gather.md",
    "outline.md",
    "draft.md",
    "self_check.md",
    "format.md",
)
EXPECTED_ARTIFACTS = (
    "01-intake.md",
    "02-sources.md",
    "03-outline.md",
    "04-draft.md",
    "05-review.md",
    "brief.md",
)


# --- workspace marker (grain.toml, graceful degradation) ---------------------
def test_grain_toml_present_without_workspace_kind() -> None:
    toml = DEMO / "grain.toml"
    assert toml.is_file()
    lines = toml.read_text(encoding="utf-8").splitlines()
    # No ACTIVE workspace_kind key (a commented hint is allowed); mirrors the
    # acceptance grep `grep -c '^workspace_kind' == 0`.
    active = [ln for ln in lines if ln.lstrip().startswith("workspace_kind")]
    assert active == [], f"workspace_kind must be omitted, found: {active}"
    assert not any(ln.startswith("workspace_kind") for ln in lines)


# --- recipe is the gateless T06 bundle, verbatim -----------------------------
def test_recipe_yaml_byte_identical_to_bundle() -> None:
    demo = (DEMO_RECIPE / "recipe.yaml").read_bytes()
    bundled = (BUNDLED / "recipe.yaml").read_bytes()
    assert demo == bundled


def test_step_prompts_byte_identical_to_bundle() -> None:
    for name in STEP_FILES:
        demo = (DEMO_RECIPE / "steps" / name).read_bytes()
        bundled = (BUNDLED / "steps" / name).read_bytes()
        assert demo == bundled, f"step {name} diverges from the bundle"


def test_demo_recipe_parses_and_is_gateless() -> None:
    definition = load_recipe(DEMO_RECIPE / "recipe.yaml")
    assert definition.id == "research-brief"
    assert len(definition.steps) == 6
    # Gateless bundle: no step declares a review gate (spec §7 demo recipe).
    assert all(s.gate in ("", "none") for s in definition.steps)
    assert definition.final == "brief.md"


# --- committed reference run proves the finished structure -------------------
def test_reference_run_is_schema_valid_done_run() -> None:
    data = json.loads((REFERENCE_RUN / "run.json").read_text(encoding="utf-8"))
    assert data["apiVersion"] == "grain.recipe-run/v1"
    assert data["run_id"] == "research-brief-0001"
    assert data["recipe"] == "research-brief"
    assert data["recipe_apiVersion"] == "grain.recipe/v2"
    assert data["params"] == {"topic": "GLP-1 obesity market"}
    # mode and supervision are DISTINCT fields (spec §2.2).
    assert data["mode"] == "operator"
    assert data["mode"] in VALID_MODES
    assert data["supervision"] in VALID_SUPERVISION
    # never store operator/auto as a supervision value
    assert data["supervision"] not in ("operator", "auto")
    assert data["status"] == "done"
    assert data["cursor"] == "format"  # final step id; no past-final sentinel
    assert len(data["steps"]) == 6


def test_reference_run_loads_via_store_and_round_trips() -> None:
    run = recipe_store.load_run(DEMO, "research-brief-0001")
    assert isinstance(run, RecipeRun)
    assert run.status == "done"
    assert run.cursor == "format"
    assert [s.id for s in run.steps] == [
        "intake",
        "gather",
        "outline",
        "draft",
        "self_check",
        "format",
    ]
    assert all(s.status == "done" for s in run.steps)


def test_reference_run_artifacts_exist_and_match_recipe_scoping() -> None:
    run = recipe_store.load_run(DEMO, "research-brief-0001")
    definition = load_recipe(DEMO_RECIPE / "recipe.yaml")
    # Each step record's artifact == the recipe's declared output, exists, non-empty.
    for record, step in zip(run.steps, definition.steps):
        assert record.artifact == step.output
        artifact = REFERENCE_RUN / record.artifact
        assert artifact.is_file(), f"missing artifact {record.artifact}"
        assert artifact.stat().st_size > 0, f"empty artifact {record.artifact}"
    assert [r.artifact for r in run.steps] == list(EXPECTED_ARTIFACTS)


def test_reference_run_final_artifact_is_brief() -> None:
    brief = REFERENCE_RUN / "brief.md"
    assert brief.is_file()
    assert brief.stat().st_size > 0


# --- live operator-mode run on a fresh copy (graceful degradation) -----------
@pytest.fixture()
def fresh_workspace(tmp_path: Path) -> Path:
    """A copy of the demo workspace WITHOUT the committed reference run."""
    ws = tmp_path / "recipe-demo"
    (ws / "docs" / "recipes").mkdir(parents=True)
    shutil.copy2(DEMO / "grain.toml", ws / "grain.toml")
    shutil.copytree(DEMO_RECIPE, ws / "docs" / "recipes" / "research-brief")
    return ws


def test_start_run_returns_started_pending_no_artifacts(fresh_workspace: Path) -> None:
    service = RecipeService(fresh_workspace)
    result = service.start_run(
        "research-brief", {"topic": "GLP-1 obesity market"}, mode="operator"
    )
    assert result.outcome == "started"
    assert result.run_status == "pending"
    assert result.cursor == "intake"  # cursor = first step
    run_dir = recipe_store.run_dir(fresh_workspace, result.run_id)
    # No artifact written by start_run.
    assert not (run_dir / "01-intake.md").exists()
    assert not (run_dir / "brief.md").exists()


def test_next_renders_step1_and_pauses_awaiting_input(fresh_workspace: Path) -> None:
    service = RecipeService(fresh_workspace)
    started = service.start_run(
        "research-brief", {"topic": "GLP-1 obesity market"}, mode="operator"
    )
    result = service.next(started.run_id)
    # awaiting_input is a STATUS; the outcome is prompt_ready (spec §3.1).
    assert result.outcome == "prompt_ready"
    assert result.run_status == "awaiting_input"
    assert result.step_id == "intake"
    assert result.prompt  # step 1 prompt rendered
    assert "GLP-1 obesity market" in result.prompt  # {{topic}} substituted
    # Engine writes NO artifact in operator mode.
    run_dir = recipe_store.run_dir(fresh_workspace, started.run_id)
    assert not (run_dir / "01-intake.md").exists()
    # run.json reflects the pause + cursor on the current step.
    run = recipe_store.load_run(fresh_workspace, started.run_id)
    assert run.status == "awaiting_input"
    assert run.cursor == "intake"
    assert run.step("intake").status == "awaiting_input"


def test_graceful_degradation_runs_without_workspace_kind(
    fresh_workspace: Path,
) -> None:
    # The marker carries no active workspace_kind; the engine must still run.
    toml_text = (fresh_workspace / "grain.toml").read_text(encoding="utf-8")
    assert not any(
        ln.startswith("workspace_kind") for ln in toml_text.splitlines()
    )
    service = RecipeService(fresh_workspace)
    started = service.start_run(
        "research-brief", {"topic": "GLP-1 obesity market"}, mode="operator"
    )
    result = service.next(started.run_id)
    assert result.outcome == "prompt_ready"
    assert result.run_status == "awaiting_input"
    assert result.step_id == "intake"


def test_bare_run_does_not_reach_done_offline(fresh_workspace: Path) -> None:
    """Operator mode never auto-completes: a fresh run pauses, never `done`."""
    service = RecipeService(fresh_workspace)
    started = service.start_run(
        "research-brief", {"topic": "GLP-1 obesity market"}, mode="operator"
    )
    # Drive next() repeatedly without authoring any artifact: it must keep
    # pausing at the first step, never advancing or completing.
    for _ in range(4):
        result = service.next(started.run_id)
        assert result.outcome == "prompt_ready"
        assert result.run_status == "awaiting_input"
    run = recipe_store.load_run(fresh_workspace, started.run_id)
    assert run.status != "done"
    run_dir = recipe_store.run_dir(fresh_workspace, started.run_id)
    assert not (run_dir / "brief.md").exists()


# --- runbook README reflects the locked demo ---------------------------------
def _readme() -> str:
    return (DEMO / "README.md").read_text(encoding="utf-8")


def test_readme_has_install_and_commands() -> None:
    text = _readme()
    assert "pip install grain-kit" in text
    assert "uv tool install grain-kit" in text
    assert "research-brief-0001" in text  # reference-run beat
    assert "grain recipe show" in text
    assert "grain recipe run research-brief" in text
    assert "grain recipe next" in text
    assert "grain recipe status" in text
    assert "Offline fallback" in text


def test_readme_does_not_overclaim_bare_run() -> None:
    text = _readme().lower()
    # Must not claim a bare run produces all 6 artifacts or reaches done.
    assert "does **not** auto-complete" in _readme() or "not auto-complete" in text
    assert "never" in text and "writes" in text  # "engine never writes artifacts"


def test_readme_omits_private_script_path() -> None:
    # The private Diwata-Infra presentation script must not ship in the README.
    assert _readme().count("grain_demo_script") == 0
    assert "Diwata-Infra" not in _readme()


# --- the live run never pollutes the committed reference run ------------------
def test_committed_runs_dir_holds_only_reference_run() -> None:
    runs_dir = DEMO / "docs" / "recipes" / "runs"
    entries = sorted(p.name for p in runs_dir.iterdir())
    # Only the committed reference run dir and the .gitkeep placeholder.
    assert entries == [".gitkeep", "research-brief-0001"]
