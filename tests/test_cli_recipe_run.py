# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Tests for the operator-mode recipe run verbs (P34-T05).

Covers ``grain recipe run / next / status / resume / gate`` over the PARALLEL
recipe engine. Every test stages a fixture recipe into a temp workspace, then
drives the engine via Click's ``CliRunner`` and asserts against ``run.json``
(the single source of truth) — never the SDLC packet loop. Operator mode is
deterministic and offline: no network, no API key.
"""

from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path

import yaml
from click.testing import CliRunner

from grain.cli import main
from grain.services import recipe_store
from grain.services.recipe_service import RecipeService


# --- fixtures ----------------------------------------------------------------
def _write_recipe(root: Path, recipe: dict) -> str:
    recipe_id = recipe["id"]
    recipe_dir = root / "docs" / "recipes" / recipe_id
    (recipe_dir / "steps").mkdir(parents=True, exist_ok=True)
    (recipe_dir / "recipe.yaml").write_text(
        yaml.safe_dump(recipe, sort_keys=False), encoding="utf-8"
    )
    for step in recipe["steps"]:
        (recipe_dir / step["prompt"]).write_text(
            "Work on {{topic}}.\n", encoding="utf-8"
        )
    return recipe_id


def _nogate_recipe() -> dict:
    return {
        "apiVersion": "grain.recipe/v2",
        "id": "nogate",
        "name": "No Gate",
        "description": "two-step recipe with no gates",
        "category": "research",
        "supervision": "gated",
        "params": [
            {"id": "topic", "label": "Topic", "required": True, "type": "string"}
        ],
        "steps": [
            {
                "id": "intake",
                "name": "Frame",
                "prompt": "steps/intake.md",
                "inputs": ["params"],
                "output": "01-intake.md",
            },
            {
                "id": "draft",
                "name": "Draft",
                "prompt": "steps/draft.md",
                "inputs": ["params"],
                "output": "brief.md",
            },
        ],
        "final": "brief.md",
    }


def _gated_recipe() -> dict:
    return {
        "apiVersion": "grain.recipe/v2",
        "id": "gated",
        "name": "Gated",
        "description": "three-step recipe; middle step gated",
        "category": "research",
        "supervision": "gated",
        "params": [
            {"id": "topic", "label": "Topic", "required": True, "type": "string"}
        ],
        "steps": [
            {
                "id": "intake",
                "prompt": "steps/intake.md",
                "inputs": ["params"],
                "output": "01-intake.md",
            },
            {
                "id": "review",
                "prompt": "steps/review.md",
                "inputs": ["params"],
                "output": "02-review.md",
                "gate": "review",
            },
            {
                "id": "final",
                "prompt": "steps/final.md",
                "inputs": ["params"],
                "output": "brief.md",
            },
        ],
        "final": "brief.md",
    }


def _invoke(runner: CliRunner, root: Path, *args, fmt: str | None = None):
    base = ["--repo", str(root)]
    if fmt:
        base += ["--format", fmt]
    return runner.invoke(main, [*base, "recipe", *args])


def _only_run_id(root: Path) -> str:
    ids = recipe_store.list_runs(root)
    assert len(ids) == 1, ids
    return ids[0]


def _write_output(root: Path, run_id: str, name: str) -> None:
    path = recipe_store.run_dir(root, run_id) / name
    path.write_text("artifact body\n", encoding="utf-8")


# --- run: operator pause + drive to done -------------------------------------
def test_run_pauses_at_awaiting_input_then_next_drives_to_done(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _nogate_recipe())

    result = _invoke(runner, tmp_path, "run", "nogate", "-p", "topic=GLP-1")
    assert result.exit_code == 0, result.output

    run_id = _only_run_id(tmp_path)
    run = recipe_store.load_run(tmp_path, run_id)
    assert run.mode == "operator"
    assert run.status == "awaiting_input"
    assert run.cursor == "intake"
    # run.json exists at the spec'd path
    assert (recipe_store.run_dir(tmp_path, run_id) / "run.json").is_file()

    # Author step 1, advance.
    _write_output(tmp_path, run_id, "01-intake.md")
    r2 = _invoke(runner, tmp_path, "next")
    assert r2.exit_code == 0, r2.output
    run = recipe_store.load_run(tmp_path, run_id)
    assert run.cursor == "draft"
    assert run.step("intake").status == "done"

    # Author final, advance to completion.
    _write_output(tmp_path, run_id, "brief.md")
    r3 = _invoke(runner, tmp_path, "next")
    assert r3.exit_code == 0, r3.output
    run = recipe_store.load_run(tmp_path, run_id)
    assert run.status == "done"
    assert run.cursor == "draft"  # cursor holds final step id on done
    assert (recipe_store.run_dir(tmp_path, run_id) / "brief.md").is_file()


# --- next advances exactly one step ------------------------------------------
def test_next_advances_exactly_one_step(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _nogate_recipe())
    _invoke(runner, tmp_path, "run", "nogate", "-p", "topic=x")
    run_id = _only_run_id(tmp_path)

    # Author BOTH outputs up front, then advance one step at a time.
    _write_output(tmp_path, run_id, "01-intake.md")
    _write_output(tmp_path, run_id, "brief.md")

    before = recipe_store.load_run(tmp_path, run_id)
    n_steps = len(before.steps)
    done_before = sum(1 for s in before.steps if s.status == "done")

    _invoke(runner, tmp_path, "next")
    mid = recipe_store.load_run(tmp_path, run_id)
    assert len(mid.steps) == n_steps  # array length fixed
    assert mid.cursor == "draft"  # cursor moved by one
    assert sum(1 for s in mid.steps if s.status == "done") == done_before + 1

    _invoke(runner, tmp_path, "next")
    after = recipe_store.load_run(tmp_path, run_id)
    assert after.status == "done"
    assert sum(1 for s in after.steps if s.status == "done") == n_steps


# --- gate: halt / approve / reject / resume ----------------------------------
def test_run_halts_at_awaiting_gate(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _gated_recipe())
    # Pre-stage outputs so the run reaches the gated step.
    result = _invoke(runner, tmp_path, "run", "gated", "-p", "topic=x")
    assert result.exit_code == 0, result.output
    run_id = _only_run_id(tmp_path)
    # First step un-authored -> pauses on intake.
    assert recipe_store.load_run(tmp_path, run_id).cursor == "intake"

    _write_output(tmp_path, run_id, "01-intake.md")
    _write_output(tmp_path, run_id, "02-review.md")
    # Re-run drives across intake to the gate on review.
    r2 = _invoke(runner, tmp_path, "run", "gated", "--run", run_id)
    assert r2.exit_code == 0, r2.output
    run = recipe_store.load_run(tmp_path, run_id)
    assert run.status == "awaiting_gate"
    assert run.cursor == "review"


def test_gate_approve_advances_past_gated_step(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _gated_recipe())
    _invoke(runner, tmp_path, "run", "gated", "-p", "topic=x")
    run_id = _only_run_id(tmp_path)
    _write_output(tmp_path, run_id, "01-intake.md")
    _write_output(tmp_path, run_id, "02-review.md")
    _invoke(runner, tmp_path, "run", "gated", "--run", run_id)
    assert recipe_store.load_run(tmp_path, run_id).status == "awaiting_gate"

    attempts_before = recipe_store.load_run(tmp_path, run_id).step("review").attempts
    r = _invoke(runner, tmp_path, "gate", "approve", "--run", run_id)
    assert r.exit_code == 0, r.output
    run = recipe_store.load_run(tmp_path, run_id)
    assert run.cursor == "final"  # advanced PAST the gate
    assert run.step("review").status == "done"
    # gated step not re-run
    assert run.step("review").attempts == attempts_before


def test_gate_reject_sends_step_back_for_rework(tmp_path):
    # F7: reject is NOT a dead-end. It resets the gated step for rework so the
    # run can move forward again, instead of freezing at the gate.
    runner = CliRunner()
    _write_recipe(tmp_path, _gated_recipe())
    _invoke(runner, tmp_path, "run", "gated", "-p", "topic=x")
    run_id = _only_run_id(tmp_path)
    _write_output(tmp_path, run_id, "01-intake.md")
    _write_output(tmp_path, run_id, "02-review.md")
    _invoke(runner, tmp_path, "run", "gated", "--run", run_id)
    assert recipe_store.load_run(tmp_path, run_id).status == "awaiting_gate"

    r = _invoke(runner, tmp_path, "gate", "reject", "--run", run_id)
    assert r.exit_code == 0, r.output
    run = recipe_store.load_run(tmp_path, run_id)
    # The run is back to running, cursor still on the gated step, which is reset
    # to a re-runnable state and its rejected artifact discarded.
    assert run.status == "running"
    assert run.cursor == "review"
    review = run.step("review")
    assert review.status == "pending"
    assert review.artifact is None
    assert not (recipe_store.run_dir(tmp_path, run_id) / "02-review.md").exists()

    # `next` re-renders the rejected step (operator pause), proving it is not a
    # dead-end: re-author -> back to the gate.
    r2 = _invoke(runner, tmp_path, "next")
    assert r2.exit_code == 0, r2.output
    assert recipe_store.load_run(tmp_path, run_id).status == "awaiting_input"
    _write_output(tmp_path, run_id, "02-review.md")
    r3 = _invoke(runner, tmp_path, "next")
    assert r3.exit_code == 0, r3.output
    assert recipe_store.load_run(tmp_path, run_id).status == "awaiting_gate"


def test_resume_does_not_pass_gate(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _gated_recipe())
    _invoke(runner, tmp_path, "run", "gated", "-p", "topic=x")
    run_id = _only_run_id(tmp_path)
    _write_output(tmp_path, run_id, "01-intake.md")
    _write_output(tmp_path, run_id, "02-review.md")
    _invoke(runner, tmp_path, "run", "gated", "--run", run_id)
    assert recipe_store.load_run(tmp_path, run_id).status == "awaiting_gate"

    r = _invoke(runner, tmp_path, "resume", run_id)
    assert r.exit_code == 0, r.output
    run = recipe_store.load_run(tmp_path, run_id)
    assert run.status == "awaiting_gate"  # gate NOT passed by resume
    assert run.cursor == "review"


# --- status ------------------------------------------------------------------
def test_status_reflects_cursor_and_per_step_status(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _nogate_recipe())
    _invoke(runner, tmp_path, "run", "nogate", "-p", "topic=x")
    run_id = _only_run_id(tmp_path)

    r = _invoke(runner, tmp_path, "status")
    assert r.exit_code == 0, r.output
    assert "intake" in r.output
    assert "draft" in r.output
    assert "awaiting_input" in r.output


def test_status_json_shape_and_roundtrip(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _nogate_recipe())
    _invoke(runner, tmp_path, "run", "nogate", "-p", "topic=x")
    run_id = _only_run_id(tmp_path)

    r = _invoke(runner, tmp_path, "status", fmt="json")
    assert r.exit_code == 0, r.output
    payload = json.loads(r.output)
    for key in (
        "run_id",
        "mode",
        "supervision",
        "status",
        "cursor",
        "created",
        "updated",
        "steps",
    ):
        assert key in payload, key
    assert payload["mode"] == "operator"
    assert isinstance(payload["steps"], list)
    assert {"id", "status"} <= set(payload["steps"][0].keys())

    # created / updated / mode round-trip via a re-load.
    run = recipe_store.load_run(tmp_path, run_id)
    assert run.created == payload["created"]
    assert run.updated == payload["updated"]
    assert run.mode == payload["mode"]


def test_each_verb_emits_json_with_mode(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _nogate_recipe())

    r_run = _invoke(runner, tmp_path, "run", "nogate", "-p", "topic=x", fmt="json")
    assert r_run.exit_code == 0, r_run.output
    payload = json.loads(r_run.output)
    assert payload["mode"] == "operator"
    run_id = payload["run_id"]

    for verb in (["next"], ["status"], ["resume", run_id]):
        r = _invoke(runner, tmp_path, *verb, fmt="json")
        assert r.exit_code == 0, r.output
        body = json.loads(r.output)
        assert "mode" in body and "created" in body and "updated" in body


# --- ambiguity ---------------------------------------------------------------
def _make_two_open_runs(tmp_path) -> tuple[str, str]:
    service = RecipeService(tmp_path)
    a = service.start_run("nogate", {"topic": "a"}, mode="operator").run_id
    b = service.start_run("nogate", {"topic": "b"}, mode="operator").run_id
    return a, b


def test_ambiguous_open_runs_raise_usage_error(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _nogate_recipe())
    _make_two_open_runs(tmp_path)

    for args in (["run", "nogate"], ["next"], ["status"], ["gate", "approve"]):
        r = _invoke(runner, tmp_path, *args)
        assert r.exit_code != 0, (args, r.output)
        assert "ambiguous" in (r.output + (str(r.exception) or "")).lower(), (
            args,
            r.output,
        )


def test_run_with_explicit_run_id_disambiguates(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _nogate_recipe())
    a, _b = _make_two_open_runs(tmp_path)
    r = _invoke(runner, tmp_path, "next", "--run", a)
    assert r.exit_code == 0, r.output


# --- resume from a failed run ------------------------------------------------
def test_resume_failed_run_increments_attempts(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _nogate_recipe())
    service = RecipeService(tmp_path)
    run_id = service.start_run("nogate", {"topic": "x"}, mode="operator").run_id

    # Simulate a failed run parked on the first step.
    run = recipe_store.load_run(tmp_path, run_id)
    run.status = "failed"
    rec = run.step("intake")
    rec.status = "failed"
    rec.attempts = 1
    rec.error = "boom"
    recipe_store.save_run(tmp_path, run)

    r = _invoke(runner, tmp_path, "resume", run_id)
    assert r.exit_code == 0, r.output
    after = recipe_store.load_run(tmp_path, run_id)
    assert after.step("intake").attempts == 2  # re-entered from cursor
    assert after.status == "awaiting_input"
    # prior step artifacts never mutated (none authored here)
    assert after.step("draft").artifact is None


def test_missing_prompt_file_run_fails_cleanly(tmp_path):
    # F11: a step prompt path that does not exist fails fast on `run` with a
    # clean non-zero exit (typed ValidationError), never a traceback.
    runner = CliRunner()
    recipe = _nogate_recipe()
    recipe_dir = tmp_path / "docs" / "recipes" / recipe["id"]
    (recipe_dir / "steps").mkdir(parents=True, exist_ok=True)
    (recipe_dir / "recipe.yaml").write_text(
        yaml.safe_dump(recipe, sort_keys=False), encoding="utf-8"
    )
    # Deliberately do NOT write the steps/*.md prompt files.
    r = _invoke(runner, tmp_path, "run", "nogate", "-p", "topic=x")
    assert r.exit_code != 0
    assert "Traceback" not in r.output
    assert r.exception is None or isinstance(r.exception, SystemExit)
    # No run advanced into an awaiting_input state on a broken definition.
    assert not (tmp_path / "docs" / "recipes" / "runs").exists() or not recipe_store.list_runs(tmp_path)


def test_non_utf8_artifact_next_fails_cleanly(tmp_path):
    # F12: a non-UTF8 prior artifact surfaces as a clean non-zero exit on `next`,
    # never a raw UnicodeDecodeError / traceback.
    runner = CliRunner()
    recipe = _nogate_recipe()
    # Make draft depend on intake's artifact so it is read on render.
    recipe["steps"][1]["inputs"] = ["params", "intake"]
    _write_recipe(tmp_path, recipe)
    _invoke(runner, tmp_path, "run", "nogate", "-p", "topic=x")
    run_id = _only_run_id(tmp_path)
    # Author intake's artifact as binary (non-empty -> completes), then advance.
    (recipe_store.run_dir(tmp_path, run_id) / "01-intake.md").write_bytes(
        b"\xff\xfe binary not utf-8"
    )
    _invoke(runner, tmp_path, "next")  # intake done -> cursor draft
    r = _invoke(runner, tmp_path, "next")  # draft render reads binary intake
    assert r.exit_code != 0
    assert "Traceback" not in r.output
    assert r.exception is None or isinstance(r.exception, SystemExit)


def test_unknown_run_id_fails_cleanly(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _nogate_recipe())
    r = _invoke(runner, tmp_path, "status", "--run", "nogate-9999")
    assert r.exit_code != 0


# ===========================================================================
# C3 error-contract & CLI-robustness regressions (F14 / F10 / F15 / F9 / F6)
# ===========================================================================


def _corrupt_run_missing_cursor(root: Path, run_id: str) -> None:
    """Rewrite a run's run.json with the required ``cursor`` key removed."""
    path = recipe_store.run_dir(root, run_id) / "run.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    del data["cursor"]
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


# --- F14: a run verb translates EVERY engine error (shared base) to exit 3 -----
def test_run_verb_translates_unlisted_engine_error(tmp_path, monkeypatch):
    # An engine error that the OLD hardcoded except-tuple did not list must STILL
    # translate to the spec ValidationError (exit 3), not leak to the CLI
    # catch-all as a raw exception / exit 1. The shared RecipeEngineError base
    # makes this hold for any error, present or future.
    from grain.services.recipe_service import RecipeEngineError

    class _BrandNewEngineError(RecipeEngineError):
        pass

    runner = CliRunner()
    _write_recipe(tmp_path, _nogate_recipe())
    _invoke(runner, tmp_path, "run", "nogate", "-p", "topic=x")
    run_id = _only_run_id(tmp_path)

    def _boom(self, rid):
        raise _BrandNewEngineError("a brand new engine error")

    monkeypatch.setattr(RecipeService, "next", _boom)
    r = _invoke(runner, tmp_path, "next", "--run", run_id)
    assert r.exit_code == 3, (r.exit_code, r.output)  # ValidationError, not exit 1
    assert "Traceback" not in r.output
    assert r.exception is None or isinstance(r.exception, SystemExit)


# --- F10: {{steps.params}} through the CLI is a clean non-zero exit ------------
def test_steps_params_reference_next_fails_cleanly(tmp_path):
    runner = CliRunner()
    recipe = _nogate_recipe()
    recipe["id"] = "stepsparams"
    # First step references {{steps.params}} (params is an inputs entry, not a step).
    recipe["steps"][0]["prompt"] = "inline:bad {{steps.params}}"
    recipe["steps"][0]["inputs"] = ["params"]
    _write_recipe(tmp_path, recipe)
    # The render fires on `run` (which advances toward the first pause).
    r = _invoke(runner, tmp_path, "run", "stepsparams", "-p", "topic=x")
    assert r.exit_code != 0
    assert "Traceback" not in r.output
    assert r.exception is None or isinstance(r.exception, SystemExit)


# --- F15: a run.json missing a required key surfaces as "unreadable run" -------
def test_run_json_missing_cursor_is_unreadable_not_keyerror(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _nogate_recipe())
    _invoke(runner, tmp_path, "run", "nogate", "-p", "topic=x")
    run_id = _only_run_id(tmp_path)
    _corrupt_run_missing_cursor(tmp_path, run_id)

    r = _invoke(runner, tmp_path, "status", "--run", run_id)
    # Old code: raw KeyError('cursor') -> catch-all exit 1. Now: ValidationError.
    assert r.exit_code == 3, (r.exit_code, r.output)
    assert "unreadable" in r.output.lower()
    assert "Traceback" not in r.output


# --- F9: an unreadable run is surfaced, not silently swallowed -----------------
def test_unreadable_run_surfaced_not_reported_as_no_open_run(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _nogate_recipe())
    _invoke(runner, tmp_path, "run", "nogate", "-p", "topic=x")
    run_id = _only_run_id(tmp_path)
    _corrupt_run_missing_cursor(tmp_path, run_id)

    # No --run: the open-run scan must NOT swallow the broken run and falsely
    # claim "no open recipe run".
    r = _invoke(runner, tmp_path, "status")
    assert r.exit_code != 0
    combined = (r.output + (str(r.exception) or "")).lower()
    assert "unreadable" in combined
    assert "no open recipe run" not in combined


def test_unreadable_run_blocks_conflicting_new_run(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _nogate_recipe())
    _invoke(runner, tmp_path, "run", "nogate", "-p", "topic=x")
    run_id = _only_run_id(tmp_path)
    _corrupt_run_missing_cursor(tmp_path, run_id)

    # Old code swallowed the broken run and allowed a SECOND run to start.
    r = _invoke(runner, tmp_path, "run", "nogate", "-p", "topic=y")
    assert r.exit_code != 0
    assert "unreadable" in r.output.lower()
    # No conflicting second run was created.
    assert recipe_store.list_runs(tmp_path) == [run_id]


# --- F6: a FAILED run does not block a new run; single-run msg is accurate -----
def test_failed_run_does_not_block_new_run(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _nogate_recipe())
    service = RecipeService(tmp_path)
    failed_id = service.start_run("nogate", {"topic": "x"}, mode="operator").run_id
    run = recipe_store.load_run(tmp_path, failed_id)
    run.status = "failed"
    run.step("intake").status = "failed"
    run.step("intake").error = "boom"
    recipe_store.save_run(tmp_path, run)

    # A new run must START (a failed run is parked, not in progress).
    r = _invoke(runner, tmp_path, "run", "nogate", "-p", "topic=y")
    assert r.exit_code == 0, r.output
    assert len(recipe_store.list_runs(tmp_path)) == 2  # the failed one + the new one


def test_single_in_progress_run_message_is_accurate(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _nogate_recipe())
    service = RecipeService(tmp_path)
    service.start_run("nogate", {"topic": "x"}, mode="operator")  # one pending run

    r = _invoke(runner, tmp_path, "run", "nogate", "-p", "topic=y")
    assert r.exit_code != 0
    out = r.output.lower()
    # Accurate single-run message, NOT the false "ambiguous: multiple…".
    assert "in progress" in out
    assert "ambiguous" not in out


# ===========================================================================
# Auto mode (P34-T09): --auto on `run`, opt-in guard, gate halt, failure+resume
# ===========================================================================
#
# All auto-mode tests use a FAKE local agent command (a tiny Python script) —
# NEVER a real network call or API key.

_SUCCESS_AGENT = (
    "import os\n"
    "with open(os.environ['GRAIN_RECIPE_OUTPUT'], 'w') as f:\n"
    "    f.write('auto body\\n')\n"
)
# Records that it was invoked (marker), then writes output. Used to PROVE the
# operator path never shells out.
_MARKER_AGENT = (
    "import os\n"
    "open(os.path.join(os.environ['GRAIN_RECIPE_RUN_DIR'], '.agent_ran'), 'w').close()\n"
    "with open(os.environ['GRAIN_RECIPE_OUTPUT'], 'w') as f:\n"
    "    f.write('auto body\\n')\n"
)
_NONZERO_AGENT = "import sys\nsys.stderr.write('boom\\n')\nsys.exit(1)\n"


def _autonomous_recipe() -> dict:
    recipe = _nogate_recipe()
    recipe["id"] = "auton"
    recipe["supervision"] = "autonomous"
    return recipe


def _write_agent_config(root: Path, body: str) -> Path:
    """Stage docs/runtime/workflow_loop.yaml pointing every stage at a fake agent."""
    script = root / "fake_agent.py"
    script.write_text(body, encoding="utf-8")
    command = f"{shlex.quote(sys.executable)} {shlex.quote(str(script))}"
    runtime = root / "docs" / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    config = {
        "supervision_level": "gated",
        "agents": {
            "executor": {"command": command},
            "reviewer": {"command": command},
            "closer": {"command": command},
        },
    }
    (runtime / "workflow_loop.yaml").write_text(
        yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
    )
    return script


def test_run_auto_drives_to_done(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _nogate_recipe())
    _write_agent_config(tmp_path, _SUCCESS_AGENT)

    r = _invoke(runner, tmp_path, "run", "nogate", "-p", "topic=GLP-1", "--auto")
    assert r.exit_code == 0, r.output

    run_id = _only_run_id(tmp_path)
    run = recipe_store.load_run(tmp_path, run_id)
    assert run.mode == "auto"
    assert run.status == "done"
    directory = recipe_store.run_dir(tmp_path, run_id)
    assert (directory / "01-intake.md").is_file()
    assert (directory / "brief.md").is_file()  # final artifact landed


def test_auto_is_opt_in_operator_never_shells_out(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _nogate_recipe())
    _write_agent_config(tmp_path, _MARKER_AGENT)

    # No --auto and supervision is 'gated' -> operator path, no agent invoked.
    r = _invoke(runner, tmp_path, "run", "nogate", "-p", "topic=x")
    assert r.exit_code == 0, r.output

    run_id = _only_run_id(tmp_path)
    run = recipe_store.load_run(tmp_path, run_id)
    assert run.mode == "operator"
    assert run.status == "awaiting_input"
    directory = recipe_store.run_dir(tmp_path, run_id)
    assert not (directory / ".agent_ran").exists()  # fake agent was NOT called
    assert not (directory / "01-intake.md").exists()  # no artifact written


def test_autonomous_supervision_implies_auto(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _autonomous_recipe())
    _write_agent_config(tmp_path, _SUCCESS_AGENT)

    # No --auto flag, but supervision: autonomous implies auto mode.
    r = _invoke(runner, tmp_path, "run", "auton", "-p", "topic=x")
    assert r.exit_code == 0, r.output
    run_id = _only_run_id(tmp_path)
    run = recipe_store.load_run(tmp_path, run_id)
    assert run.mode == "auto"
    assert run.status == "done"


def test_auto_halts_at_gate(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _gated_recipe())
    _write_agent_config(tmp_path, _SUCCESS_AGENT)

    r = _invoke(runner, tmp_path, "run", "gated", "-p", "topic=x", "--auto")
    assert r.exit_code == 0, r.output
    run_id = _only_run_id(tmp_path)
    run = recipe_store.load_run(tmp_path, run_id)
    assert run.status == "awaiting_gate"
    assert run.cursor == "review"
    assert run.step("final").status == "pending"  # not executed past the gate
    assert not (recipe_store.run_dir(tmp_path, run_id) / "brief.md").exists()


def test_auto_failure_then_resume_increments_attempts(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _nogate_recipe())
    _write_agent_config(tmp_path, _NONZERO_AGENT)

    r = _invoke(runner, tmp_path, "run", "nogate", "-p", "topic=x", "--auto")
    assert r.exit_code != 0, r.output  # agent failure -> non-zero exit
    run_id = _only_run_id(tmp_path)
    run = recipe_store.load_run(tmp_path, run_id)
    assert run.status == "failed"
    assert run.cursor == "intake"
    assert run.step("intake").attempts == 1
    assert "agent exited 1" in (run.step("intake").error or "")

    # resume re-enters in auto, retrying the failed cursor step.
    r2 = _invoke(runner, tmp_path, "resume", run_id)
    assert r2.exit_code != 0, r2.output  # still failing
    after = recipe_store.load_run(tmp_path, run_id)
    assert after.step("intake").attempts == 2  # incremented on resume
    assert after.step("draft").artifact is None  # prior step never mutated


def test_auto_missing_agent_config_fails_before_steps(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _nogate_recipe())
    # No workflow_loop.yaml staged.
    r = _invoke(runner, tmp_path, "run", "nogate", "-p", "topic=x", "--auto")
    assert r.exit_code != 0
    run_id = _only_run_id(tmp_path)
    # No step ran: first step still pending, no artifact.
    run = recipe_store.load_run(tmp_path, run_id)
    assert run.step("intake").status == "pending"
    assert not (recipe_store.run_dir(tmp_path, run_id) / "01-intake.md").exists()


def test_auto_run_json_records_mode_auto(tmp_path):
    runner = CliRunner()
    _write_recipe(tmp_path, _nogate_recipe())
    _write_agent_config(tmp_path, _SUCCESS_AGENT)
    r = _invoke(runner, tmp_path, "run", "nogate", "-p", "topic=x", "--auto", fmt="json")
    assert r.exit_code == 0, r.output
    payload = json.loads(r.output)
    assert payload["mode"] == "auto"
    assert payload["status"] == "done"
