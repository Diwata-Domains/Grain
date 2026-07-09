# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Tests for the operator-mode recipe execution engine (RecipeService).

The suite scaffolds its OWN fixture recipes under a temp workspace
``docs/recipes/<id>/`` (it does NOT depend on the bundled ``research-brief``
recipe, which ships in T06 as data). It exercises start -> multi-step advance ->
gate pause -> resume, plus the typed-error and scoping invariants.
"""

from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path

import pytest
import yaml

from grain.domain.errors import ConfigError, MissingPathError
from grain.domain.recipe import RecipeSchemaError
from grain.domain.workflow_loop import WorkflowLoopAgentConfig
from grain.services import recipe_store
from grain.services.recipe_service import (
    ArtifactDecodeError,
    AutoStepOutcome,
    GateStateError,
    InputNotReadyError,
    MissingParamError,
    NextResult,
    RecipeDefinitionChangedError,
    RecipeEngineError,
    RecipeNotFoundError,
    RecipeService,
    RecipeSummary,
    RunNotFoundError,
    ScopedInput,
    UndeclaredInputError,
    UnknownTokenError,
    VALID_NEXT_OUTCOMES,
    resolve_recipe_agent,
)


# --- fixtures / helpers ------------------------------------------------------
def _scaffold(workspace: Path, recipe: dict, *, prompt_files: dict | None = None) -> str:
    """Write ``docs/recipes/<id>/recipe.yaml`` (+ optional prompt files)."""
    recipe_id = recipe["id"]
    recipe_dir = workspace / "docs" / "recipes" / recipe_id
    recipe_dir.mkdir(parents=True, exist_ok=True)
    (recipe_dir / "recipe.yaml").write_text(yaml.safe_dump(recipe), encoding="utf-8")
    for rel, text in (prompt_files or {}).items():
        target = recipe_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return recipe_id


def _gated_recipe() -> dict:
    """3-step recipe; step 2 has a review gate."""
    return {
        "apiVersion": "grain.recipe/v2",
        "id": "demo",
        "name": "Demo",
        "description": "demo recipe",
        "category": "research",
        "supervision": "gated",
        "params": [{"id": "topic", "required": True, "type": "string"}],
        "steps": [
            {
                "id": "intake",
                "name": "Intake",
                "prompt": "inline:Frame the topic {{topic}}",
                "inputs": ["params"],
                "output": "01-intake.md",
            },
            {
                "id": "review",
                "name": "Review",
                "prompt": "inline:Review {{topic}} using {{steps.intake}}",
                "inputs": ["params", "intake"],
                "output": "02-review.md",
                "gate": "review",
            },
            {
                "id": "format",
                "name": "Format",
                "prompt": "inline:Format {{steps.review}}",
                "inputs": ["review"],
                "output": "brief.md",
            },
        ],
        "final": "brief.md",
    }


def _linear_recipe() -> dict:
    """2-step recipe, no gates; step 1 uses a prompt FILE (exercise file load)."""
    return {
        "apiVersion": "grain.recipe/v2",
        "id": "linear",
        "name": "Linear",
        "supervision": "autonomous",
        "params": [{"id": "topic", "required": True, "type": "string"}],
        "steps": [
            {
                "id": "s1",
                "prompt": "steps/s1.md",
                "inputs": ["params"],
                "output": "01.md",
            },
            {
                "id": "s2",
                "prompt": "inline:Use {{steps.s1}}",
                "inputs": ["s1"],
                "output": "02.md",
            },
        ],
        "final": "02.md",
    }


def _undeclared_recipe() -> dict:
    """2-step recipe whose step 2 references a done-but-undeclared step."""
    return {
        "apiVersion": "grain.recipe/v2",
        "id": "undeclared",
        "name": "Undeclared",
        "supervision": "autonomous",
        "params": [{"id": "topic", "required": True, "type": "string"}],
        "steps": [
            {
                "id": "s1",
                "prompt": "inline:first {{topic}}",
                "inputs": ["params"],
                "output": "01.md",
            },
            {
                "id": "s2",
                # s1 is done by the time s2 renders, but is NOT in s2 inputs.
                "prompt": "inline:ref {{steps.s1}}",
                "inputs": ["params"],
                "output": "02.md",
            },
        ],
        "final": "02.md",
    }


def _param_unscoped_recipe() -> dict:
    """2-step recipe whose step 2 uses {{topic}} WITHOUT declaring 'params'."""
    return {
        "apiVersion": "grain.recipe/v2",
        "id": "paramscope",
        "name": "Param Scope",
        "supervision": "autonomous",
        "params": [{"id": "topic", "required": True, "type": "string"}],
        "steps": [
            {
                "id": "s1",
                "prompt": "inline:first {{topic}}",
                "inputs": ["params"],
                "output": "01.md",
            },
            {
                "id": "s2",
                # uses {{topic}} but inputs does NOT include 'params'.
                "prompt": "inline:ref {{topic}}",
                "inputs": ["s1"],
                "output": "02.md",
            },
        ],
        "final": "02.md",
    }


@pytest.fixture()
def service(tmp_path: Path) -> RecipeService:
    bundled = tmp_path / "bundled"
    bundled.mkdir()
    return RecipeService(workspace_root=tmp_path, bundled_recipes_root=bundled)


def _read_run_json(workspace: Path, run_id: str) -> dict:
    path = recipe_store.run_dir(workspace, run_id) / "run.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _write_artifact(workspace: Path, run_id: str, name: str, text: str = "x") -> None:
    target = recipe_store.run_dir(workspace, run_id) / name
    target.write_text(text, encoding="utf-8")


# --- 1. start_run happy path -------------------------------------------------
def test_start_run_no_auto_advance(service: RecipeService, tmp_path: Path) -> None:
    _scaffold(tmp_path, _gated_recipe())
    result = service.start_run("demo", {"topic": "GLP-1"})

    assert result.outcome == "started"
    assert result.run_status == "pending"
    assert result.cursor == "intake"
    assert result.run_id == "demo-0001"

    data = _read_run_json(tmp_path, "demo-0001")
    assert data["apiVersion"] == "grain.recipe-run/v1"
    assert data["status"] == "pending"
    assert data["cursor"] == "intake"
    assert data["mode"] == "operator"
    assert data["supervision"] == "gated"  # copied from the definition
    assert [s["status"] for s in data["steps"]] == ["pending", "pending", "pending"]


# --- 2. missing required param ----------------------------------------------
def test_start_run_missing_param(service: RecipeService, tmp_path: Path) -> None:
    _scaffold(tmp_path, _gated_recipe())
    with pytest.raises(MissingParamError):
        service.start_run("demo", {})
    assert not (tmp_path / "docs" / "recipes" / "runs" / "demo-0001").exists()


# --- 3. unknown recipe / run ------------------------------------------------
def test_unknown_recipe_and_run(service: RecipeService) -> None:
    with pytest.raises(RecipeNotFoundError):
        service.resolve("nope")
    with pytest.raises(RunNotFoundError):
        service.next("no-such-run")
    with pytest.raises(RunNotFoundError):
        service.resume("no-such-run")


# --- 4. next with no artifact -> prompt_ready / awaiting_input ---------------
def test_next_prompt_ready(service: RecipeService, tmp_path: Path) -> None:
    _scaffold(tmp_path, _gated_recipe())
    service.start_run("demo", {"topic": "GLP-1"})
    result = service.next("demo-0001")

    assert result.outcome == "prompt_ready"
    assert result.run_status == "awaiting_input"
    assert result.step_id == "intake"
    # token substituted, no literal mustache remains
    assert "GLP-1" in result.prompt
    assert "{{" not in result.prompt
    # absolute output path
    assert Path(result.output_path).is_absolute()
    assert result.output_path.endswith("demo-0001/01-intake.md")
    # only the declared input (params) is surfaced
    assert [i.id for i in result.inputs] == ["params"]
    assert result.inputs[0].kind == "params"
    assert "topic=GLP-1" in result.inputs[0].content

    data = _read_run_json(tmp_path, "demo-0001")
    assert data["status"] == "awaiting_input"
    assert data["steps"][0]["status"] == "awaiting_input"


# --- 5. scoping: declared inputs only ---------------------------------------
def test_scoping_excludes_later_step(service: RecipeService, tmp_path: Path) -> None:
    _scaffold(tmp_path, _gated_recipe())
    service.start_run("demo", {"topic": "T"})
    # advance to the review step (inputs: [params, intake])
    service.next("demo-0001")  # intake -> awaiting_input
    _write_artifact(tmp_path, "demo-0001", "01-intake.md", "intake body")
    service.next("demo-0001")  # advance to review
    result = service.next("demo-0001")  # render review prompt

    assert result.step_id == "review"
    surfaced = {i.id for i in result.inputs}
    assert surfaced == {"params", "intake"}
    assert "format" not in surfaced  # later/sibling step never auto-included


# --- 6. out-of-scope substitution -> UndeclaredInputError -------------------
def test_undeclared_input_error(service: RecipeService, tmp_path: Path) -> None:
    _scaffold(tmp_path, _undeclared_recipe())
    service.start_run("undeclared", {"topic": "T"})
    service.next("undeclared-0001")  # s1 -> awaiting_input
    _write_artifact(tmp_path, "undeclared-0001", "01.md", "s1 body")
    service.next("undeclared-0001")  # advance to s2
    with pytest.raises(UndeclaredInputError):
        service.next("undeclared-0001")  # s2 prompt references undeclared s1


def test_input_not_ready_distinct_from_undeclared(
    service: RecipeService, tmp_path: Path
) -> None:
    # review declares [params, intake] but intake is NOT done yet -> not-ready.
    _scaffold(tmp_path, _gated_recipe())
    run = recipe_store.create_run(
        tmp_path, service.resolve("demo"), {"topic": "T"}, mode="operator"
    )
    # force cursor onto review without intake being done
    run.cursor = "review"
    run.status = "running"
    recipe_store.save_run(tmp_path, run)
    with pytest.raises(InputNotReadyError):
        service.next(run.run_id)


# --- 6b. params scoping: {{param}} requires declared 'params' (F13) ----------
def test_param_token_requires_declared_params_input(
    service: RecipeService, tmp_path: Path
) -> None:
    _scaffold(tmp_path, _param_unscoped_recipe())
    service.start_run("paramscope", {"topic": "T"})
    service.next("paramscope-0001")  # s1 -> awaiting_input
    _write_artifact(tmp_path, "paramscope-0001", "01.md", "s1 body")
    service.next("paramscope-0001")  # advance to s2
    # s2 renders {{topic}} but does not declare 'params' -> undeclared (F13).
    with pytest.raises(UndeclaredInputError):
        service.next("paramscope-0001")


def test_param_token_in_scope_when_params_declared(
    service: RecipeService, tmp_path: Path
) -> None:
    # control: the SAME token resolves when the step declares 'params'.
    recipe = _param_unscoped_recipe()
    recipe["steps"][1]["inputs"] = ["params", "s1"]
    _scaffold(tmp_path, recipe)
    service.start_run("paramscope", {"topic": "GLP-1"})
    service.next("paramscope-0001")
    _write_artifact(tmp_path, "paramscope-0001", "01.md", "s1 body")
    service.next("paramscope-0001")  # advance to s2
    result = service.next("paramscope-0001")  # renders s2
    assert "GLP-1" in result.prompt
    assert {i.id for i in result.inputs} == {"params", "s1"}


# --- 7. fulfil artifact -> advanced -----------------------------------------
def test_next_advances(service: RecipeService, tmp_path: Path) -> None:
    _scaffold(tmp_path, _linear_recipe(), prompt_files={"steps/s1.md": "Do {{topic}}"})
    service.start_run("linear", {"topic": "T"})
    service.next("linear-0001")  # s1 awaiting_input
    _write_artifact(tmp_path, "linear-0001", "01.md", "s1 body")
    result = service.next("linear-0001")

    assert result.outcome == "advanced"
    assert result.cursor == "s2"
    assert result.run_status == "running"
    data = _read_run_json(tmp_path, "linear-0001")
    assert data["cursor"] == "s2"
    assert data["steps"][0]["status"] == "done"
    assert data["steps"][0]["artifact"] == "01.md"


# --- 7b. completion is exists + non-empty (operator, F2) ---------------------
def test_operator_empty_artifact_does_not_complete(
    service: RecipeService, tmp_path: Path
) -> None:
    _scaffold(tmp_path, _linear_recipe(), prompt_files={"steps/s1.md": "Do {{topic}}"})
    service.start_run("linear", {"topic": "T"})
    service.next("linear-0001")  # s1 awaiting_input
    # author an EMPTY artifact: must NOT count as done (F2) -> still paused.
    _write_artifact(tmp_path, "linear-0001", "01.md", "")
    result = service.next("linear-0001")
    assert result.outcome == "prompt_ready"
    assert result.run_status == "awaiting_input"
    assert result.cursor == "s1"
    data = _read_run_json(tmp_path, "linear-0001")
    assert data["cursor"] == "s1"
    assert data["steps"][0]["status"] == "awaiting_input"

    # filling it with content now completes the step.
    _write_artifact(tmp_path, "linear-0001", "01.md", "s1 body")
    advanced = service.next("linear-0001")
    assert advanced.outcome == "advanced"
    assert advanced.cursor == "s2"


# --- 7c. failed run does not reuse a left-behind output (F4) ------------------
def test_failed_run_does_not_treat_leftover_output_as_done(
    service: RecipeService, tmp_path: Path
) -> None:
    _scaffold(tmp_path, _linear_recipe(), prompt_files={"steps/s1.md": "Do {{topic}}"})
    service.start_run("linear", {"topic": "T"})
    service.next("linear-0001")  # s1 awaiting_input
    # a non-empty output is on disk, but the step/run are FAILED.
    _write_artifact(tmp_path, "linear-0001", "01.md", "leftover body")
    run = recipe_store.load_run(tmp_path, "linear-0001")
    run.status = "failed"
    rec = run.step("s1")
    rec.status = "failed"
    rec.attempts = 1
    rec.error = "boom"
    recipe_store.save_run(tmp_path, run)

    # next() must NOT silently complete the step from the leftover output; it
    # re-renders (explicit re-run path) instead of advancing.
    result = service.next("linear-0001")
    assert result.outcome == "prompt_ready"
    assert result.run_status == "awaiting_input"
    assert result.cursor == "s1"
    data = _read_run_json(tmp_path, "linear-0001")
    assert data["cursor"] == "s1"
    assert data["steps"][0]["status"] == "awaiting_input"
    assert data["steps"][0]["attempts"] == 2  # re-entering the failed step


# --- 8. gate handling -------------------------------------------------------
def test_gate_awaiting_then_noop(service: RecipeService, tmp_path: Path) -> None:
    _scaffold(tmp_path, _gated_recipe())
    service.start_run("demo", {"topic": "T"})
    service.next("demo-0001")  # intake awaiting
    _write_artifact(tmp_path, "demo-0001", "01-intake.md")
    service.next("demo-0001")  # advance to review
    service.next("demo-0001")  # review awaiting
    _write_artifact(tmp_path, "demo-0001", "02-review.md")
    gated = service.next("demo-0001")  # review done -> gate

    assert gated.outcome == "awaiting_gate"
    assert gated.gate == "review"
    assert gated.cursor == "review"  # cursor unchanged
    data = _read_run_json(tmp_path, "demo-0001")
    assert data["status"] == "awaiting_gate"
    assert data["cursor"] == "review"
    assert data["steps"][1]["status"] == "awaiting_gate"

    # second next on a gated run is a noop (no GateBlockedError)
    again = service.next("demo-0001")
    assert again.outcome == "noop"
    assert again.run_status == "awaiting_gate"


# --- 9. final step -> run_complete ------------------------------------------
def test_run_complete(service: RecipeService, tmp_path: Path) -> None:
    _scaffold(tmp_path, _linear_recipe(), prompt_files={"steps/s1.md": "Do {{topic}}"})
    service.start_run("linear", {"topic": "T"})
    service.next("linear-0001")  # s1 awaiting
    _write_artifact(tmp_path, "linear-0001", "01.md", "s1 body")
    service.next("linear-0001")  # advance to s2
    s2 = service.next("linear-0001")  # s2 awaiting; renders {{steps.s1}}
    assert "s1 body" in s2.prompt
    _write_artifact(tmp_path, "linear-0001", "02.md", "s2 body")
    result = service.next("linear-0001")

    assert result.outcome == "run_complete"
    assert result.run_status == "done"
    assert result.cursor is None
    data = _read_run_json(tmp_path, "linear-0001")
    assert data["status"] == "done"
    assert data["cursor"] == "s2"  # run.json keeps final step id (§2.2)

    # next() on a done run is run_complete (idempotent, no write needed)
    assert service.next("linear-0001").outcome == "run_complete"


# --- 10. resume from a fresh service ----------------------------------------
def test_resume_fresh_service(tmp_path: Path) -> None:
    bundled = tmp_path / "bundled"
    bundled.mkdir()
    svc = RecipeService(workspace_root=tmp_path, bundled_recipes_root=bundled)
    _scaffold(tmp_path, _linear_recipe(), prompt_files={"steps/s1.md": "Do {{topic}}"})
    svc.start_run("linear", {"topic": "T"})
    svc.next("linear-0001")  # s1 awaiting
    _write_artifact(tmp_path, "linear-0001", "01.md", "s1 body")
    svc.next("linear-0001")  # advance to s2 (cursor persisted)
    del svc

    fresh = RecipeService(workspace_root=tmp_path, bundled_recipes_root=bundled)
    resumed = fresh.resume("linear-0001")
    assert resumed.outcome == "prompt_ready"
    assert resumed.step_id == "s2"
    assert resumed.run_status == "awaiting_input"
    assert "s1 body" in resumed.prompt


# --- 11. idempotency of the operator pause ----------------------------------
def test_idempotent_pause(service: RecipeService, tmp_path: Path) -> None:
    _scaffold(tmp_path, _gated_recipe())
    service.start_run("demo", {"topic": "T"})
    first = service.next("demo-0001")
    second = service.next("demo-0001")
    assert first.outcome == second.outcome == "prompt_ready"
    assert first.prompt == second.prompt
    assert first.cursor == second.cursor == "intake"
    data = _read_run_json(tmp_path, "demo-0001")
    assert data["steps"][0]["attempts"] == 1  # not double-incremented


# --- 12. offline / decoupling ------------------------------------------------
def test_module_is_decoupled() -> None:
    from grain.services import recipe_service

    text = Path(recipe_service.__file__).read_text(encoding="utf-8")
    # the SDLC engine entry point is never referenced
    assert "evaluate_workflow_state" not in text
    # no import of any task-packet / review / close / workflow-state service
    import_lines = [
        line
        for line in text.splitlines()
        if line.strip().startswith(("import ", "from "))
    ]
    forbidden = (
        "workflow_state_service",
        "workflow_service",
        "review_service",
        "close_service",
        "task_service",
        "packet",
    )
    for line in import_lines:
        for token in forbidden:
            assert token not in line, f"forbidden import: {line!r}"


# --- enumeration ------------------------------------------------------------
def test_list_recipes(tmp_path: Path) -> None:
    bundled = tmp_path / "bundled"
    bundled.mkdir()
    # one bundled recipe
    b_dir = bundled / "bundled-one"
    b_dir.mkdir()
    bundled_recipe = _linear_recipe()
    bundled_recipe["id"] = "bundled-one"
    (b_dir / "recipe.yaml").write_text(yaml.safe_dump(bundled_recipe), encoding="utf-8")
    # one workspace recipe
    _scaffold(tmp_path, _gated_recipe())

    svc = RecipeService(workspace_root=tmp_path, bundled_recipes_root=bundled)
    summaries = svc.list_recipes()
    by_id = {s.id: s for s in summaries}
    assert isinstance(summaries[0], RecipeSummary)
    assert by_id["bundled-one"].source == "bundled"
    assert by_id["demo"].source == "workspace"
    assert by_id["demo"].category == "research"


# ===========================================================================
# Auto-mode (P34-T09): run_auto / resolve_recipe_agent / AutoStepOutcome
# ===========================================================================
#
# Every test uses a FAKE local agent command (a tiny Python script) — NEVER a
# real network call or API key. The fake agent learns where to write the step
# artifact from the ``GRAIN_RECIPE_OUTPUT`` env var the engine exports.

_SUCCESS_AGENT = (
    "import os\n"
    "with open(os.environ['GRAIN_RECIPE_OUTPUT'], 'w') as f:\n"
    "    f.write('auto body\\n')\n"
)
_NONZERO_AGENT = (
    "import sys\n"
    "sys.stderr.write('agent boom\\n')\n"
    "sys.exit(1)\n"
)
_MISSING_OUTPUT_AGENT = "import sys\nsys.exit(0)\n"  # exit 0 but write nothing
_EMPTY_OUTPUT_AGENT = (
    "import os\n"
    "open(os.environ['GRAIN_RECIPE_OUTPUT'], 'w').close()\n"  # present but empty
)
# Writes a non-empty BINARY (non-UTF8) artifact: passes exists+non-empty but is
# not decodable text -> F12 auto-mode decode failure.
_BINARY_OUTPUT_AGENT = (
    "import os\n"
    "with open(os.environ['GRAIN_RECIPE_OUTPUT'], 'wb') as f:\n"
    "    f.write(b'\\xff\\xfe\\x00\\x01 not utf-8')\n"
)
# Succeeds on the 1st invocation, fails on the 2nd+ (counter in the run dir).
_FAIL_ON_SECOND_AGENT = (
    "import os, sys\n"
    "counter = os.path.join(os.environ['GRAIN_RECIPE_RUN_DIR'], '.counter')\n"
    "n = 0\n"
    "try:\n"
    "    n = int(open(counter).read() or '0')\n"
    "except FileNotFoundError:\n"
    "    pass\n"
    "n += 1\n"
    "open(counter, 'w').write(str(n))\n"
    "if n >= 2:\n"
    "    sys.stderr.write('fail on step 2\\n')\n"
    "    sys.exit(1)\n"
    "with open(os.environ['GRAIN_RECIPE_OUTPUT'], 'w') as f:\n"
    "    f.write('s1 body\\n')\n"
)


def _agent(tmp_path: Path, name: str, body: str) -> WorkflowLoopAgentConfig:
    """Materialize a fake agent script and return a command-mode agent config."""
    script = tmp_path / name
    script.write_text(body, encoding="utf-8")
    command = f"{shlex.quote(sys.executable)} {shlex.quote(str(script))}"
    return WorkflowLoopAgentConfig(mode="command", command=command)


def test_run_auto_drives_to_done(service: RecipeService, tmp_path: Path) -> None:
    _scaffold(tmp_path, _linear_recipe(), prompt_files={"steps/s1.md": "Do {{topic}}"})
    agent = _agent(tmp_path, "ok_agent.py", _SUCCESS_AGENT)
    started = service.start_run("linear", {"topic": "T"}, mode="auto")

    run = service.run_auto(started.run_id, agent=agent)
    assert run.status == "done"
    assert run.cursor == "s2"  # cursor holds final step id on done
    assert [s.status for s in run.steps] == ["done", "done"]
    assert [s.attempts for s in run.steps] == [1, 1]

    data = _read_run_json(tmp_path, started.run_id)
    assert data["mode"] == "auto"
    assert data["status"] == "done"
    directory = recipe_store.run_dir(tmp_path, started.run_id)
    assert (directory / "01.md").is_file()
    assert (directory / "02.md").is_file()  # final artifact landed


def test_run_auto_halts_at_gate(service: RecipeService, tmp_path: Path) -> None:
    _scaffold(tmp_path, _gated_recipe())
    agent = _agent(tmp_path, "ok_agent.py", _SUCCESS_AGENT)
    started = service.start_run("demo", {"topic": "T"}, mode="auto")

    run = service.run_auto(started.run_id, agent=agent)
    assert run.status == "awaiting_gate"
    assert run.cursor == "review"  # cursor on the gated step
    assert run.step("intake").status == "done"
    assert run.step("review").status == "awaiting_gate"
    assert run.step("format").status == "pending"  # never executed past the gate
    directory = recipe_store.run_dir(tmp_path, started.run_id)
    assert not (directory / "brief.md").exists()  # post-gate artifact not produced


def test_run_auto_fails_on_nonzero_exit(service: RecipeService, tmp_path: Path) -> None:
    _scaffold(tmp_path, _linear_recipe(), prompt_files={"steps/s1.md": "Do {{topic}}"})
    agent = _agent(tmp_path, "bad_agent.py", _NONZERO_AGENT)
    started = service.start_run("linear", {"topic": "T"}, mode="auto")

    run = service.run_auto(started.run_id, agent=agent)
    assert run.status == "failed"
    assert run.cursor == "s1"  # cursor left on the failed step
    rec = run.step("s1")
    assert rec.status == "failed"
    assert rec.attempts == 1
    assert "agent exited 1" in (rec.error or "")
    assert "agent boom" in (rec.error or "")  # captured stderr


def test_run_auto_fails_on_missing_output(
    service: RecipeService, tmp_path: Path
) -> None:
    _scaffold(tmp_path, _linear_recipe(), prompt_files={"steps/s1.md": "Do {{topic}}"})
    agent = _agent(tmp_path, "noop_agent.py", _MISSING_OUTPUT_AGENT)
    started = service.start_run("linear", {"topic": "T"}, mode="auto")

    run = service.run_auto(started.run_id, agent=agent)
    assert run.status == "failed"
    assert run.step("s1").status == "failed"
    assert "no output artifact" in (run.step("s1").error or "")


def test_run_auto_empty_artifact_fails_not_done(
    service: RecipeService, tmp_path: Path
) -> None:
    # F2: completion is exists + NON-EMPTY (+ not-failed). A present-but-empty
    # artifact is NOT a completion — the step fails (it did not produce content).
    _scaffold(tmp_path, _linear_recipe(), prompt_files={"steps/s1.md": "Do {{topic}}"})
    agent = _agent(tmp_path, "empty_agent.py", _EMPTY_OUTPUT_AGENT)
    started = service.start_run("linear", {"topic": "T"}, mode="auto")

    run = service.run_auto(started.run_id, agent=agent)
    assert run.status == "failed"
    assert run.step("s1").status == "failed"
    assert "empty" in (run.step("s1").error or "")
    directory = recipe_store.run_dir(tmp_path, started.run_id)
    # the empty file is on disk but was never accepted as the step artifact.
    assert (directory / "01.md").read_text(encoding="utf-8") == ""
    assert run.step("s1").artifact is None


def test_run_auto_non_utf8_output_fails_typed_not_crash(
    service: RecipeService, tmp_path: Path
) -> None:
    # F12 (auto branch): an agent that writes a NON-EMPTY but binary/non-UTF8
    # output passes the exists+non-empty gate, but reading it for the atomic
    # write raises a typed ArtifactDecodeError -> the step is marked FAILED
    # (spec §5), never a raw UnicodeDecodeError crash.
    _scaffold(tmp_path, _linear_recipe(), prompt_files={"steps/s1.md": "Do {{topic}}"})
    agent = _agent(tmp_path, "binary_agent.py", _BINARY_OUTPUT_AGENT)
    started = service.start_run("linear", {"topic": "T"}, mode="auto")

    run = service.run_auto(started.run_id, agent=agent)
    assert run.status == "failed"
    assert run.step("s1").status == "failed"
    assert "UTF-8" in (run.step("s1").error or "")
    # the binary file is on disk but was never accepted as the step artifact
    # (write_step_artifact never ran, so the record reference stays unset).
    assert run.step("s1").artifact is None
    assert run.step("s2").status == "pending"  # never advanced past the failure


def test_run_auto_resume_increments_attempts_without_mutating_prior(
    service: RecipeService, tmp_path: Path
) -> None:
    _scaffold(tmp_path, _linear_recipe(), prompt_files={"steps/s1.md": "Do {{topic}}"})
    agent = _agent(tmp_path, "flaky_agent.py", _FAIL_ON_SECOND_AGENT)
    started = service.start_run("linear", {"topic": "T"}, mode="auto")

    run = service.run_auto(started.run_id, agent=agent)
    # s1 succeeded (invocation 1); s2 failed (invocation 2).
    assert run.status == "failed"
    assert run.cursor == "s2"
    assert run.step("s1").status == "done"
    assert run.step("s2").status == "failed"
    assert run.step("s2").attempts == 1
    directory = recipe_store.run_dir(tmp_path, started.run_id)
    s1_body_before = (directory / "01.md").read_text(encoding="utf-8")

    # resume re-enters in auto, retrying the failed cursor step.
    resumed = service.resume(started.run_id, agent=agent)
    assert resumed.status == "failed"  # invocation 3 also fails
    assert resumed.step("s2").attempts == 2  # incremented
    assert resumed.step("s1").status == "done"  # prior step untouched
    assert (directory / "01.md").read_text(encoding="utf-8") == s1_body_before


def test_resolve_recipe_agent(tmp_path: Path) -> None:
    runtime = tmp_path / "docs" / "runtime"
    runtime.mkdir(parents=True)
    (runtime / "workflow_loop.yaml").write_text(
        "supervision_level: autonomous\n"
        "agents:\n"
        "  executor: {shortcut: claude, model: claude-x}\n"
        "  reviewer: {shortcut: claude}\n"
        "  closer: {shortcut: claude}\n",
        encoding="utf-8",
    )
    agent = resolve_recipe_agent(tmp_path)
    assert isinstance(agent, WorkflowLoopAgentConfig)
    assert agent.mode == "shortcut"
    assert agent.shortcut == "claude"
    assert agent.model == "claude-x"

    # per-step model biases (overrides) the configured model
    biased = resolve_recipe_agent(tmp_path, step_model="claude-step")
    assert biased.model == "claude-step"
    # original config is not mutated
    assert resolve_recipe_agent(tmp_path).model == "claude-x"


def test_resolve_recipe_agent_missing_config_raises(tmp_path: Path) -> None:
    with pytest.raises(MissingPathError):
        resolve_recipe_agent(tmp_path)


def test_resolve_recipe_agent_invalid_config_raises(tmp_path: Path) -> None:
    runtime = tmp_path / "docs" / "runtime"
    runtime.mkdir(parents=True)
    (runtime / "workflow_loop.yaml").write_text(
        "supervision_level: gated\n"
        "agents:\n"
        "  executor: {shortcut: bogus}\n"  # not in VALID_AGENT_SHORTCUTS
        "  reviewer: {shortcut: claude}\n"
        "  closer: {shortcut: claude}\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError):
        resolve_recipe_agent(tmp_path)


def test_auto_step_outcome_validation() -> None:
    ok = AutoStepOutcome(step_id="s1", status="done", artifact="01.md", attempts=1)
    assert ok.status == "done"
    with pytest.raises(ValueError):
        AutoStepOutcome(step_id="s1", status="bogus")
    with pytest.raises(ValueError):
        AutoStepOutcome(step_id="s1", status="done", attempts=-1)


# ===========================================================================
# C2 run-lifecycle robustness regressions (F5 / F8 / F11 / F12 / F7)
# ===========================================================================


def _write_recipe_yaml(workspace: Path, dir_name: str, recipe: dict) -> None:
    """Write docs/recipes/<dir_name>/recipe.yaml with arbitrary id (for F5/F8)."""
    recipe_dir = workspace / "docs" / "recipes" / dir_name
    recipe_dir.mkdir(parents=True, exist_ok=True)
    (recipe_dir / "recipe.yaml").write_text(yaml.safe_dump(recipe), encoding="utf-8")


# --- F5: a recipe whose id != its directory is rejected (no orphaned run) -----
def test_resolve_rejects_dir_id_mismatch(service: RecipeService, tmp_path: Path) -> None:
    recipe = _gated_recipe()
    recipe["id"] = "other"  # yaml id diverges from the directory name "mydir"
    _write_recipe_yaml(tmp_path, "mydir", recipe)

    # Old behaviour: resolve-by-dir returned id "other", so a run persisted under
    # "other" could never be re-resolved (its dir is "mydir") -> orphaned run.
    with pytest.raises(RecipeSchemaError):
        service.resolve("mydir")
    # And it is not advertised as runnable either.
    assert "other" not in {s.id for s in service.list_recipes()}
    assert "mydir" not in {s.id for s in service.list_recipes()}


# --- F8: a mid-run definition edit raises a TYPED error, not a raw KeyError ----
def test_mid_run_definition_desync_raises_typed(
    service: RecipeService, tmp_path: Path
) -> None:
    recipe = {
        "apiVersion": "grain.recipe/v2",
        "id": "desync",
        "name": "Desync",
        "supervision": "autonomous",
        "params": [{"id": "topic", "required": True, "type": "string"}],
        "steps": [
            {"id": "s1", "prompt": "inline:first {{topic}}", "inputs": ["params"], "output": "01.md"},
            {"id": "s2", "prompt": "inline:use {{steps.s1}}", "inputs": ["s1"], "output": "02.md"},
        ],
        "final": "02.md",
    }
    _write_recipe_yaml(tmp_path, "desync", recipe)
    service.start_run("desync", {"topic": "T"})
    service.next("desync-0001")  # s1 awaiting_input
    _write_artifact(tmp_path, "desync-0001", "01.md", "s1 body")
    service.next("desync-0001")  # advance to s2

    # Insert a NEW step the running run never recorded; s2 now references it.
    recipe["steps"] = [
        {"id": "s1", "prompt": "inline:first {{topic}}", "inputs": ["params"], "output": "01.md"},
        {"id": "sx", "prompt": "inline:mid {{topic}}", "inputs": ["params"], "output": "0x.md"},
        {"id": "s2", "prompt": "inline:use {{steps.s1}} {{steps.sx}}", "inputs": ["s1", "sx"], "output": "02.md"},
    ]
    _write_recipe_yaml(tmp_path, "desync", recipe)

    # Old code raised a raw KeyError from run.step('sx'); now it is typed.
    with pytest.raises(RecipeDefinitionChangedError):
        service.next("desync-0001")


def test_mid_run_recipe_api_version_mismatch_raises_typed(
    service: RecipeService, tmp_path: Path
) -> None:
    _scaffold(tmp_path, _gated_recipe())
    service.start_run("demo", {"topic": "T"})
    # Tamper the captured recipe apiVersion to an incompatible major.
    run = recipe_store.load_run(tmp_path, "demo-0001")
    run.recipe_api_version = "grain.recipe/v3"
    recipe_store.save_run(tmp_path, run)
    with pytest.raises(RecipeDefinitionChangedError):
        service.next("demo-0001")


# --- F11: a missing step prompt file fails fast at start (typed) --------------
def test_missing_prompt_file_fails_fast_at_start(
    service: RecipeService, tmp_path: Path
) -> None:
    # _linear_recipe step s1 uses a prompt FILE; do NOT create it.
    _scaffold(tmp_path, _linear_recipe())  # no prompt_files
    with pytest.raises(RecipeSchemaError) as exc:
        service.start_run("linear", {"topic": "T"})
    assert "s1.md" in str(exc.value)
    # No run dir was created (failed before persistence).
    assert not (tmp_path / "docs" / "recipes" / "runs" / "linear-0001").exists()


# --- F12: a non-UTF8 prior artifact yields a typed error, not a crash ---------
def test_non_utf8_prior_artifact_raises_typed(
    service: RecipeService, tmp_path: Path
) -> None:
    _scaffold(tmp_path, _linear_recipe(), prompt_files={"steps/s1.md": "Do {{topic}}"})
    service.start_run("linear", {"topic": "T"})
    service.next("linear-0001")  # s1 awaiting_input
    # Author s1's artifact as BINARY / non-UTF8 bytes (non-empty -> completes).
    target = recipe_store.run_dir(tmp_path, "linear-0001") / "01.md"
    target.write_bytes(b"\xff\xfe\x00\x01 not utf-8")
    service.next("linear-0001")  # s1 done -> advance to s2

    # s2 declares s1 as an input; reading the binary artifact must be typed.
    with pytest.raises(ArtifactDecodeError):
        service.next("linear-0001")


# --- F7: reject_gate resets the gated step for rework (service-level) ---------
def test_reject_gate_resets_step_for_rework(
    service: RecipeService, tmp_path: Path
) -> None:
    _scaffold(tmp_path, _gated_recipe())
    service.start_run("demo", {"topic": "T"})
    service.next("demo-0001")  # intake awaiting
    _write_artifact(tmp_path, "demo-0001", "01-intake.md")
    service.next("demo-0001")  # advance to review
    service.next("demo-0001")  # review awaiting
    _write_artifact(tmp_path, "demo-0001", "02-review.md")
    service.next("demo-0001")  # review done -> awaiting_gate

    run = service.reject_gate("demo-0001")
    assert run.status == "running"
    assert run.cursor == "review"
    assert run.step("review").status == "pending"
    assert run.step("review").artifact is None
    # rejected artifact discarded so `next` does not re-complete from it.
    assert not (recipe_store.run_dir(tmp_path, "demo-0001") / "02-review.md").exists()

    # next re-renders the rejected step (proves it is not a dead-end).
    result = service.next("demo-0001")
    assert result.outcome == "prompt_ready"
    assert result.step_id == "review"


# --- F10: {{steps.params}} is a typed token error, never a raw KeyError --------
def _steps_params_recipe() -> dict:
    """1-step recipe whose prompt references {{steps.params}} (params is NOT a step)."""
    return {
        "apiVersion": "grain.recipe/v2",
        "id": "stepsparams",
        "name": "Steps Params",
        "supervision": "autonomous",
        "params": [{"id": "topic", "required": True, "type": "string"}],
        "steps": [
            {
                "id": "s1",
                # 'params' is a legal inputs entry, so it IS in declared inputs —
                # but it is not a step, so {{steps.params}} must not hit run.step().
                "prompt": "inline:bad {{steps.params}}",
                "inputs": ["params"],
                "output": "01.md",
            },
        ],
        "final": "01.md",
    }


def test_steps_params_reference_raises_typed_not_keyerror(
    service: RecipeService, tmp_path: Path
) -> None:
    _scaffold(tmp_path, _steps_params_recipe())
    service.start_run("stepsparams", {"topic": "T"})
    # Old code: run.step('params') raised a raw KeyError mid-render. Now it is a
    # clean typed token error (and a RecipeEngineError so the CLI translates it).
    with pytest.raises(UnknownTokenError) as exc:
        service.next("stepsparams-0001")
    assert isinstance(exc.value, RecipeEngineError)
    assert not isinstance(exc.value, KeyError)


# --- F14: every engine error subclasses the shared base RecipeEngineError ------
def test_all_engine_errors_share_base_class() -> None:
    # The uniform CLI translation (F14) depends on every typed engine error being
    # a RecipeEngineError so a single `except RecipeEngineError` catches them all.
    for err in (
        RecipeNotFoundError,
        RunNotFoundError,
        MissingParamError,
        InputNotReadyError,
        UndeclaredInputError,
        UnknownTokenError,
        RecipeDefinitionChangedError,
        ArtifactDecodeError,
        GateStateError,
    ):
        assert issubclass(err, RecipeEngineError), err


def test_result_dataclass_validation() -> None:
    with pytest.raises(ValueError):
        NextResult(
            run_id="r", outcome="bogus", cursor=None, step_id=None, run_status="pending"
        )
    with pytest.raises(ValueError):
        # prompt_ready requires prompt + output_path + awaiting_input
        NextResult(
            run_id="r",
            outcome="prompt_ready",
            cursor="s",
            step_id="s",
            run_status="pending",
        )
    with pytest.raises(ValueError):
        ScopedInput(kind="weird", id="x", path="", content="")
    assert "prompt_ready" in VALID_NEXT_OUTCOMES
    assert "awaiting_input" not in VALID_NEXT_OUTCOMES
    # token error type is importable/usable
    assert issubclass(UnknownTokenError, Exception)
