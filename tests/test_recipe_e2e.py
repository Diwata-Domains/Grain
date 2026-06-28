# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""End-to-end integration tests for the recipe step-runner MVP (P34-T08).

These two tests close out the recipe step-runner MVP with regression proof. They
exercise the PARALLEL recipe engine — ``grain.recipe/v2`` definitions driven into
``grain.recipe-run/v1`` run state under ``docs/recipes/runs/<run-id>/`` — over the
bundled, gateless ``research-brief`` recipe (6 steps) shipped by P34-T06. They
ship no new engine surface: they pin the behaviour the P34-T05 runner (CLI
``run`` / ``next`` / ``status`` / ``resume`` / ``gate``) and P34-T06 data already
built.

Both tests are OFFLINE and DETERMINISTIC: no network, no API key, no agent CLI
shell-out, and the auto-mode ``WorkflowLoopAgentConfig`` path is never exercised.
Operator mode never writes artifacts and never auto-completes — the harness
authors each step's declared ``output`` artifact (fixed fixture text) between
cursor advances; the engine only asserts ordering / scoping / gating / run-state,
never LLM content (spec §1.2).

The recipe engine is parallel to the SDLC loop: these tests assert that no task
packet is created and that ``evaluate_workflow_state`` is never invoked.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from grain.cli import main
from grain.domain.recipe import load_recipe
from grain.domain.recipe_run import (
    VALID_MODES,
    VALID_SUPERVISION,
)
from grain.services import recipe_store, workflow_service
from grain.services.recipe_service import RecipeService

RECIPE_ID = "research-brief"
TOPIC = "GLP-1 obesity market"

# Spec-ordered step ids of the bundled research-brief recipe (P34-T06).
STEP_ORDER = ("intake", "gather", "outline", "draft", "self_check", "format")


# --- shared fixture: a pre-staged knowledge workspace ------------------------
@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """A temp workspace; the bundled ``research-brief`` recipe is resolved from
    the package data dir (no git / branch / task-packet machinery required).

    The run dir lands under ``<workspace>/docs/recipes/runs/`` exactly as in a
    real pre-staged ``knowledge`` workspace.
    """
    (tmp_path / "docs" / "recipes").mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture
def no_packet_loop(monkeypatch) -> list:
    """Spy on ``evaluate_workflow_state``: the parallel recipe engine must never
    call it. Returns a list that stays EMPTY across a clean recipe run."""
    calls: list = []

    def _trip(*args, **kwargs):  # pragma: no cover - must never run
        calls.append((args, kwargs))
        raise AssertionError(
            "recipe engine must not call evaluate_workflow_state (parallel engine)"
        )

    monkeypatch.setattr(workflow_service, "evaluate_workflow_state", _trip)
    return calls


def _bundled_definition(service: RecipeService):
    return service.resolve(RECIPE_ID)


def _output_for(definition, step_id: str) -> str:
    for step in definition.steps:
        if step.id == step_id:
            return step.output
    raise KeyError(step_id)


def _write_output(workspace: Path, run_id: str, name: str, body: str) -> None:
    """Author a step's declared output artifact (operator mode = human writes it)."""
    path = recipe_store.run_dir(workspace, run_id) / name
    path.write_text(body, encoding="utf-8")


def _invoke(runner: CliRunner, workspace: Path, *args, fmt: str | None = None):
    base = ["--repo", str(workspace)]
    if fmt:
        base += ["--format", fmt]
    return runner.invoke(main, [*base, "recipe", *args])


def _run_json(workspace: Path, run_id: str) -> dict:
    path = recipe_store.run_dir(workspace, run_id) / "run.json"
    return json.loads(path.read_text(encoding="utf-8"))


# ===========================================================================
# Test A — full operator run via the authoring loop
# ===========================================================================
def test_research_brief_full_operator_run(workspace, no_packet_loop):
    runner = CliRunner()
    service = RecipeService(workspace)
    definition = _bundled_definition(service)
    assert [s.id for s in definition.steps] == list(STEP_ORDER)

    # 1. Start the run (service contract: start_run returns `started`, status
    #    `pending`, cursor on the first step — NO auto-advance, NO artifact).
    started = service.start_run(RECIPE_ID, {"topic": TOPIC}, mode="operator")
    assert started.outcome == "started"
    assert started.run_status == "pending"
    assert started.cursor == "intake"
    run_id = started.run_id

    on_disk = _run_json(workspace, run_id)
    assert on_disk["status"] == "pending"
    assert on_disk["mode"] == "operator"
    assert on_disk["cursor"] == "intake"
    run_dir = recipe_store.run_dir(workspace, run_id)
    # bare start wrote run.json only — no step artifacts.
    assert not any(
        (run_dir / _output_for(definition, sid)).exists() for sid in STEP_ORDER
    )

    # 2. Negative check: `next` with NO authored artifact pauses at
    #    `awaiting_input` on the same cursor (operator pause, not failed/done).
    paused = service.next(run_id)
    assert paused.outcome == "prompt_ready"
    assert paused.run_status == "awaiting_input"
    assert paused.cursor == "intake"
    after_pause = _run_json(workspace, run_id)
    assert after_pause["status"] == "awaiting_input"
    assert after_pause["status"] != "done"
    assert not (run_dir / _output_for(definition, "intake")).exists()

    # 3. Authoring loop: read the cursor from `grain recipe status --format json`,
    #    write the cursor step's declared output, then `grain recipe next`.
    completed_order: list[str] = []
    for _ in range(len(STEP_ORDER)):
        status_res = _invoke(runner, workspace, "status", fmt="json")
        assert status_res.exit_code == 0, status_res.output
        cursor = json.loads(status_res.output)["cursor"]
        completed_order.append(cursor)

        _write_output(
            workspace,
            run_id,
            _output_for(definition, cursor),
            f"# {cursor}\n\nfixture artifact for {cursor} on {TOPIC}\n",
        )
        next_res = _invoke(runner, workspace, "next")
        assert next_res.exit_code == 0, next_res.output

    # Steps were driven to `done` in spec order.
    assert completed_order == list(STEP_ORDER)

    # 4. Final run-state assertions (run.json is the single source of truth).
    final = _run_json(workspace, run_id)
    assert final["apiVersion"] == "grain.recipe-run/v1"
    assert final["recipe_apiVersion"] == "grain.recipe/v2"
    assert final["run_id"] == run_id
    assert final["recipe"] == RECIPE_ID
    assert final["params"] == {"topic": TOPIC}
    assert final["status"] == "done"
    assert final["cursor"] == "format"  # final step id; no past-final sentinel
    # mode is distinct from supervision and never stored as a supervision value.
    assert final["mode"] == "operator"
    assert final["mode"] in VALID_MODES
    assert final["supervision"] in VALID_SUPERVISION
    assert final["supervision"] not in ("operator", "auto")

    assert [s["id"] for s in final["steps"]] == list(STEP_ORDER)
    for rec in final["steps"]:
        assert rec["status"] == "done", rec
        assert rec["attempts"] == 1, rec

    # `final` artifact present under the run dir.
    assert (run_dir / definition.final).is_file()
    assert (run_dir / "brief.md").is_file()

    # Parallel-engine invariants: no task packet, evaluate_workflow_state untouched.
    assert not (workspace / "tasks").exists()
    assert no_packet_loop == []

    # (Bonus) the committed reference run proves the same finished structure.
    ref = (
        Path(__file__).resolve().parents[1]
        / "examples"
        / "recipe-demo"
        / "docs"
        / "recipes"
        / "runs"
        / "research-brief-0001"
        / "run.json"
    )
    if ref.is_file():
        ref_data = json.loads(ref.read_text(encoding="utf-8"))
        assert ref_data["status"] == "done"
        assert ref_data["cursor"] == "format"
        assert ref_data["mode"] == "operator"


# ===========================================================================
# Test B — resume after an EXPLICIT validation failure
# ===========================================================================
def test_resume_after_validation_failure(workspace, no_packet_loop):
    service = RecipeService(workspace)
    definition = _bundled_definition(service)

    started = service.start_run(RECIPE_ID, {"topic": TOPIC}, mode="operator")
    run_id = started.run_id
    run_dir = recipe_store.run_dir(workspace, run_id)

    # 1. Drive intake -> gather -> outline to done (author output, then advance).
    for step_id in ("intake", "gather", "outline"):
        _write_output(
            workspace,
            run_id,
            _output_for(definition, step_id),
            f"# {step_id}\n\nfixture artifact for {step_id}\n",
        )
        res = service.next(run_id)
        assert res.outcome == "advanced"

    run = recipe_store.load_run(workspace, run_id)
    assert run.cursor == "draft"
    assert run.step("draft").status == "pending"
    assert run.step("draft").attempts == 0

    # 2. Force an EXPLICIT validation failure on `draft`. The MVP engine validates
    #    output-artifact EXISTENCE only (spec §8.5), so a content-validation
    #    failure is recorded via the engine's failure path: the offending draft is
    #    rejected (not persisted), the step is marked `failed` with the error
    #    recorded, and the cursor stays on `draft` (spec §5). A *missing* output
    #    would be the normal `awaiting_input` pause — this is a deliberate FAILURE.
    run = recipe_store.load_run(workspace, run_id)
    draft_rec = run.step("draft")
    draft_rec.status = "failed"
    draft_rec.attempts = 1
    draft_rec.error = "validation failed: draft missing required sections"
    run.status = "failed"
    # cursor unchanged (stays on the failed step)
    recipe_store.save_run(workspace, run)

    failed = recipe_store.load_run(workspace, run_id)
    assert failed.status == "failed"
    assert failed.cursor == "draft"
    assert failed.step("draft").status == "failed"
    assert failed.step("draft").error
    # the rejected draft output was never persisted.
    assert not (run_dir / _output_for(definition, "draft")).exists()

    # 3. Snapshot byte content of every prior step artifact.
    prior = {
        _output_for(definition, sid): (run_dir / _output_for(definition, sid)).read_bytes()
        for sid in ("intake", "gather", "outline")
    }

    # 4. Resume: re-reads run.json (the single source of truth, including `mode`)
    #    and continues from the cursor in the RECORDED mode (operator).
    resumed = service.resume(run_id)
    assert resumed.outcome == "prompt_ready"
    assert resumed.run_status == "awaiting_input"
    assert resumed.cursor == "draft"

    after_resume = recipe_store.load_run(workspace, run_id)
    # resume continued in the recorded operator mode: it re-rendered the prompt
    # and paused — it did NOT auto-write the artifact (that would be auto mode).
    assert after_resume.mode == "operator"
    assert not (run_dir / _output_for(definition, "draft")).exists()
    # re-entering the failed step incremented attempts (1 -> 2).
    assert after_resume.step("draft").attempts == 2

    # Author a VALID draft, then drive the remaining steps to done.
    for step_id in ("draft", "self_check", "format"):
        _write_output(
            workspace,
            run_id,
            _output_for(definition, step_id),
            f"# {step_id}\n\nvalid fixture artifact for {step_id}\n",
        )
        service.next(run_id)

    # 5. Final assertions.
    done = recipe_store.load_run(workspace, run_id)
    assert done.status == "done"
    assert done.cursor == "format"
    assert done.step("draft").attempts == 2  # retried step
    for rec in done.steps:
        assert rec.status == "done", rec

    # Prior step artifacts are byte-for-byte unchanged (no step mutates another's
    # artifact — spec §5).
    for name, body in prior.items():
        assert (run_dir / name).read_bytes() == body, name

    # Parallel-engine invariant: the SDLC evaluator was never touched.
    assert no_packet_loop == []
    assert not (workspace / "tasks").exists()


# --- offline / deterministic guard -------------------------------------------
def test_bundled_recipe_is_gateless_and_offline(workspace):
    """Sanity: the recipe under test is the gateless 6-step bundle, so the full
    operator run advances every step straight to `done` with no gate pause and
    no auto/networked path."""
    service = RecipeService(workspace)
    definition = load_recipe(
        service.bundled_recipes_root / RECIPE_ID / "recipe.yaml"
    )
    assert definition.id == RECIPE_ID
    assert [s.id for s in definition.steps] == list(STEP_ORDER)
    assert definition.final == "brief.md"
    assert all(s.gate in ("none", "") for s in definition.steps)
