# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT
"""P37-T13 — the published workflow vocabulary.

Grain owns the workflow capability, so Grain publishes its vocabulary
(`docs/superpowers/specs/2026-07-09-entity-boundaries-design.md` §5.1). Diwa's Missions imports
these types rather than growing a second set.

Two invariants matter more than the types themselves:

1. The enums are not a fresh opinion. They must equal the vocabularies already in force —
   `domain/recipe_run.py`'s `VALID_*` frozensets and the `stop_reason` literals that
   `services/workflow_service.py` actually emits. A contract that drifts from its callers is worse
   than no contract.
2. This module must never enter the CLI import graph. `cli()` wraps only `main()`
   (`cli/__init__.py:317-334`), so an import-time fault here would print an uncatchable traceback
   on `grain status` — the live demo's first command.
"""

from __future__ import annotations

import ast
import importlib.metadata
import pathlib
import re
import subprocess
import sys

import pytest

import grain_contracts.workflow as vocabulary
from grain.contracts.workflow import (
    Artifact,
    Gate,
    Mode,
    Protocol,
    Run,
    RunStatus,
    StepRecord,
    StepSpec,
    StepStatus,
    StopReason,
    Supervision,
)
from grain.domain.recipe_run import (
    VALID_GATES,
    VALID_MODES,
    VALID_RUN_STATUSES,
    VALID_STEP_STATUSES,
    VALID_SUPERVISION,
)

SRC = pathlib.Path(__file__).resolve().parents[1] / "src" / "grain"
WORKFLOW_SERVICE = SRC / "services" / "workflow_service.py"
# Resolved from the installed module, not a monorepo-relative path: products/grain is subtree-mirrored
# to a public repo where packages/ does not exist.
CONTRACT = pathlib.Path(vocabulary.__file__)


def _values(enum_cls) -> set[str]:
    return {member.value for member in enum_cls}


# ── the enums are not a fresh opinion ──────────────────────────────────────────


@pytest.mark.parametrize(
    ("enum_cls", "in_force"),
    [
        (Gate, VALID_GATES),
        (RunStatus, VALID_RUN_STATUSES),
        (StepStatus, VALID_STEP_STATUSES),
        (Mode, VALID_MODES),
        (Supervision, VALID_SUPERVISION),
    ],
    ids=["Gate", "RunStatus", "StepStatus", "Mode", "Supervision"],
)
def test_enum_matches_the_vocabulary_already_in_force(enum_cls, in_force):
    assert _values(enum_cls) == set(in_force)


def test_stop_reason_roster_is_exactly_what_workflow_service_declares():
    """StopReason ports the STOP_* constants; it must not invent or drop one.

    Derived from source rather than a hand-copied list, so a new stop reason in the service fails
    this test instead of silently escaping the contract.

    Scoped to `workflow_service.py`'s module-level STOP_* constants because those are the only
    values that reach `WorkflowEvaluation.stop_reason` (`domain/workflow.py:25`). The loop reasons
    in `workflow_loop_service.py` (`steps_limit_reached`, `supervision_required`, ...) go into that
    command's JSON `_payload`, not onto an evaluation — a separate, deliberately unpublished
    vocabulary.
    """
    source = WORKFLOW_SERVICE.read_text(encoding="utf-8")
    declared = set(re.findall(r'^STOP_[A-Z_]+ = "([a-z_]+)"', source, re.M))
    assert len(declared) == 20, f"expected 20 STOP_* constants, found {len(declared)}"
    assert _values(StopReason) == declared


# ── purity: no I/O, no grain internals, off the CLI import graph ───────────────


def test_contract_imports_only_stdlib():
    tree = ast.parse(CONTRACT.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    allowed = {"__future__", "dataclasses", "enum", "typing"}
    assert imported <= allowed, f"contract must stay stdlib-only; found {sorted(imported - allowed)}"


def test_grain_contracts_ships_with_zero_dependencies():
    """The whole point of the separate distribution.

    grain-kit mandatorily pulls networkx, textual, pdfplumber, openpyxl, python-docx and
    tree-sitter-language-pack. A consumer that only wants the vocabulary must not inherit any of it.
    """
    requires = importlib.metadata.requires("grain-contracts") or []
    runtime = [r for r in requires if "extra ==" not in r]
    assert runtime == [], f"grain-contracts must stay dependency-free; found {runtime}"


def test_grain_contracts_workflow_is_the_same_object_as_grain_contracts_workflow():
    """`grain.contracts.workflow` is an address, not a copy. §5.1 keeps its promise."""
    assert Run is vocabulary.Run
    assert StopReason is vocabulary.StopReason
    assert Gate is vocabulary.Gate


def test_importing_the_cli_does_not_pull_the_contract():
    """An import-time fault in the contract must not be able to reach `grain status`."""
    probe = (
        "import sys; import grain.cli; "
        "sys.exit(1 if 'grain.contracts.workflow' in sys.modules else 0)"
    )
    result = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True)
    assert result.returncode == 0, "grain.cli must not import grain.contracts.workflow"


# ── the types ─────────────────────────────────────────────────────────────────


def _run(**overrides) -> Run:
    steps = overrides.pop(
        "steps",
        [StepRecord(id="draft"), StepRecord(id="review", gate=Gate.REVIEW)],
    )
    kwargs = dict(
        run_id="brief-0001",
        protocol="capital-network-path",
        protocol_api_version="grain.protocol/v1",
        params={"target": "Equator VC"},
        mode=Mode.OPERATOR,
        supervision=Supervision.SUPERVISED,
        status=RunStatus.RUNNING,
        cursor="draft",
        steps=steps,
    )
    kwargs.update(overrides)
    return Run(**kwargs)


def test_run_round_trips_through_its_own_dict():
    run = _run()
    assert Run.from_dict(run.to_dict()) == run


def test_step_record_round_trips_with_every_field_set():
    record = StepRecord(
        id="draft",
        status=StepStatus.DONE,
        artifact=Artifact(path="draft.md"),
        gate=Gate.REVIEW,
        attempts=2,
        started="2026-07-09T00:00:00Z",
        ended="2026-07-09T00:01:00Z",
        error=None,
    )
    assert StepRecord.from_dict(record.to_dict()) == record


def test_run_rejects_a_cursor_that_names_no_step():
    with pytest.raises(ValueError, match="cursor"):
        _run(cursor="nonexistent")


def test_run_rejects_duplicate_step_ids():
    with pytest.raises(ValueError, match="unique"):
        _run(steps=[StepRecord(id="draft"), StepRecord(id="draft")])


def test_run_rejects_no_steps():
    with pytest.raises(ValueError, match="at least one step"):
        _run(steps=[])


def test_step_record_rejects_negative_attempts():
    with pytest.raises(ValueError, match="attempts"):
        StepRecord(id="draft", attempts=-1)


def test_from_dict_rejects_an_unsupported_api_major():
    payload = _run().to_dict()
    payload["apiVersion"] = "grain.workflow-run/v2"
    with pytest.raises(ValueError, match="apiVersion"):
        Run.from_dict(payload)


def test_from_dict_surfaces_a_missing_required_key_as_valueerror():
    payload = _run().to_dict()
    del payload["cursor"]
    with pytest.raises(ValueError):
        Run.from_dict(payload)


def test_protocol_declares_its_steps():
    protocol = Protocol(
        id="capital-network-path",
        api_version="grain.protocol/v1",
        steps=[StepSpec(id="draft"), StepSpec(id="review", gate=Gate.REVIEW)],
    )
    assert [s.id for s in protocol.steps] == ["draft", "review"]
    assert protocol.step("review").gate is Gate.REVIEW


def test_protocol_rejects_duplicate_step_ids():
    with pytest.raises(ValueError, match="unique"):
        Protocol(
            id="p",
            api_version="grain.protocol/v1",
            steps=[StepSpec(id="a"), StepSpec(id="a")],
        )


def test_the_types_are_frozen():
    run = _run()
    with pytest.raises(Exception):
        run.status = RunStatus.DONE  # type: ignore[misc]
