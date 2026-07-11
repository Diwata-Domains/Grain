# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT
"""The engine kernel: a pure reducer over the workflow contract (P37-T14).

`advance()` re-expresses the recipe engine's attested transitions — completion via a produced
artifact (`recipe_service.py:569-581`), REVIEW gates halting the run (`:646-659`), reject
discarding the artifact and re-arming the step (`:716-749`) — as a pure function. Purity is the
contract: the reject-path unlink at `recipe_service.py:739` survives as a `DiscardArtifact`
EFFECT the driver applies, never as I/O inside the reducer. Diwa's Postgres executor and grain's
filesystem store both drive this one reducer; if it did I/O, one of them couldn't.
"""

import pytest

from grain.contracts.workflow import (
    Artifact,
    Gate,
    Run,
    RunStatus,
    StepRecord,
    StepStatus,
)
from grain.engine.kernel import (
    AdvanceEvent,
    ArtifactProduced,
    ConcurrentModification,
    DiscardArtifact,
    GateApproved,
    GateRejected,
    InvalidEvent,
    RunStore,
    StepFailed,
    StepStarted,
    advance,
)

NOW = "2026-07-11T12:00:00+00:00"


def _run(*, cursor="draft", status=RunStatus.RUNNING, steps=None) -> Run:
    if steps is None:
        steps = (
            StepRecord(id="draft", status=StepStatus.RUNNING),
            StepRecord(id="review", gate=Gate.REVIEW),
            StepRecord(id="publish"),
        )
    return Run(
        run_id="run-1",
        protocol="release-notes",
        protocol_api_version="grain.protocol/v1",
        status=status,
        cursor=cursor,
        steps=steps,
    )


class _SpyStore:
    """A RunStore that proves advance() never talks to a store: every method raises."""

    def _boom(self, *args, **kwargs):
        raise AssertionError("advance() must perform zero I/O — it called the store")

    load = save = discard_artifact = list_runs = _boom


# --- purity ---------------------------------------------------------------------


def test_advance_is_pure_and_never_calls_the_store():
    run = _run()
    transition = advance(
        run, ArtifactProduced(step_id="draft", artifact=Artifact("draft.md")), now=NOW
    )
    # the input run is untouched (frozen), the output is a new value
    assert run.step("draft").status is StepStatus.RUNNING
    assert transition.run is not run
    # a spy store confirms by construction: advance() has no store parameter at all,
    # and the RunStore Protocol is only a port for drivers.
    assert not isinstance(transition, _SpyStore)


def test_advance_signature_admits_no_store():
    import inspect

    params = inspect.signature(advance).parameters
    assert "store" not in params
    assert set(params) == {"run", "event", "now", "max_attempts"}


# --- artifact produced: done → gate / advance / complete -------------------------


def test_artifact_produced_advances_the_cursor():
    t = advance(_run(), ArtifactProduced(step_id="draft", artifact=Artifact("draft.md")), now=NOW)
    assert t.run.status is RunStatus.RUNNING
    assert t.run.cursor == "review"
    done = t.run.step("draft")
    assert done.status is StepStatus.DONE
    assert done.artifact == Artifact("draft.md")
    assert done.ended == NOW
    assert done.attempts == 1  # a completed step counts at least one attempt
    assert t.effects == ()


def test_artifact_produced_on_a_review_step_halts_at_the_gate():
    run = _run(cursor="review", steps=(
        StepRecord(id="draft", status=StepStatus.DONE, artifact=Artifact("draft.md")),
        StepRecord(id="review", status=StepStatus.RUNNING, gate=Gate.REVIEW),
        StepRecord(id="publish"),
    ))
    t = advance(run, ArtifactProduced(step_id="review", artifact=Artifact("review.md")), now=NOW)
    assert t.run.status is RunStatus.AWAITING_GATE
    assert t.run.cursor == "review"  # cursor unchanged at a gate
    assert t.run.step("review").status is StepStatus.AWAITING_GATE
    assert t.run.step("review").artifact == Artifact("review.md")


def test_artifact_produced_on_the_final_step_completes_the_run():
    run = _run(cursor="publish", steps=(
        StepRecord(id="draft", status=StepStatus.DONE, artifact=Artifact("draft.md")),
        StepRecord(id="review", status=StepStatus.DONE, artifact=Artifact("review.md")),
        StepRecord(id="publish", status=StepStatus.RUNNING),
    ))
    t = advance(run, ArtifactProduced(step_id="publish", artifact=Artifact("out.md")), now=NOW)
    assert t.run.status is RunStatus.DONE
    # cursor stays pinned on the final step id (run.json invariant §2.2)
    assert t.run.cursor == "publish"


# --- gate decisions ---------------------------------------------------------------


def _gated_run() -> Run:
    return _run(cursor="review", status=RunStatus.AWAITING_GATE, steps=(
        StepRecord(id="draft", status=StepStatus.DONE, artifact=Artifact("draft.md")),
        StepRecord(
            id="review", status=StepStatus.AWAITING_GATE, gate=Gate.REVIEW,
            artifact=Artifact("review.md"), attempts=1, started=NOW,
        ),
        StepRecord(id="publish"),
    ))


def test_gate_approved_advances_past_the_gate():
    t = advance(_gated_run(), GateApproved(step_id="review"), now=NOW)
    assert t.run.status is RunStatus.RUNNING
    assert t.run.cursor == "publish"
    assert t.run.step("review").status is StepStatus.DONE
    # the approved artifact stands — approval never re-runs the step
    assert t.run.step("review").artifact == Artifact("review.md")
    assert t.effects == ()


def test_gate_rejected_discards_the_artifact_and_rearms_the_step():
    t = advance(_gated_run(), GateRejected(step_id="review"), now=NOW)
    assert t.effects == (
        DiscardArtifact(run_id="run-1", step_id="review", artifact=Artifact("review.md")),
    )
    rearmed = t.run.step("review")
    assert rearmed.status is StepStatus.PENDING
    assert rearmed.artifact is None
    assert rearmed.ended is None
    assert t.run.status is RunStatus.RUNNING
    assert t.run.cursor == "review"  # same step goes again


def test_gate_decisions_require_an_awaiting_gate_run():
    with pytest.raises(InvalidEvent):
        advance(_run(), GateApproved(step_id="draft"), now=NOW)
    with pytest.raises(InvalidEvent):
        advance(_run(), GateRejected(step_id="draft"), now=NOW)


# --- failure: bounded retries -------------------------------------------------------


def test_step_failed_increments_attempts_exactly_once_and_rearms():
    t = advance(_run(), StepFailed(step_id="draft", error="agent exited 1"), now=NOW)
    failed = t.run.step("draft")
    assert failed.attempts == 1
    assert failed.status is StepStatus.PENDING  # re-armed, not dead
    assert failed.error == "agent exited 1"
    assert t.run.status is RunStatus.RUNNING


def test_step_failed_flips_failed_only_at_max_attempts():
    run = _run()
    for expected_attempts in (1, 2):
        t = advance(run, StepFailed(step_id="draft", error="boom"), now=NOW, max_attempts=3)
        run = t.run
        assert run.step("draft").attempts == expected_attempts
        assert run.step("draft").status is StepStatus.PENDING
        assert run.status is RunStatus.RUNNING

    t = advance(run, StepFailed(step_id="draft", error="boom"), now=NOW, max_attempts=3)
    assert t.run.step("draft").attempts == 3
    assert t.run.step("draft").status is StepStatus.FAILED
    assert t.run.step("draft").ended == NOW
    assert t.run.status is RunStatus.FAILED


# --- step started ---------------------------------------------------------------------


def test_step_started_marks_running_and_stamps_started_once():
    run = _run(steps=(
        StepRecord(id="draft"),
        StepRecord(id="review", gate=Gate.REVIEW),
        StepRecord(id="publish"),
    ))
    t = advance(run, StepStarted(step_id="draft"), now=NOW)
    assert t.run.step("draft").status is StepStatus.RUNNING
    assert t.run.step("draft").started == NOW
    assert t.run.status is RunStatus.RUNNING

    later = "2026-07-11T13:00:00+00:00"
    t2 = advance(t.run, StepStarted(step_id="draft"), now=later)
    assert t2.run.step("draft").started == NOW  # first start wins


# --- guards ---------------------------------------------------------------------------


def test_events_off_the_cursor_are_rejected():
    with pytest.raises(InvalidEvent):
        advance(_run(), ArtifactProduced(step_id="publish", artifact=Artifact("x")), now=NOW)
    with pytest.raises(InvalidEvent):
        advance(_run(), StepFailed(step_id="publish", error="x"), now=NOW)


def test_terminal_runs_accept_no_events():
    done = _run(cursor="publish", status=RunStatus.DONE, steps=(
        StepRecord(id="draft", status=StepStatus.DONE, artifact=Artifact("a")),
        StepRecord(id="review", status=StepStatus.DONE, artifact=Artifact("b")),
        StepRecord(id="publish", status=StepStatus.DONE, artifact=Artifact("c")),
    ))
    with pytest.raises(InvalidEvent):
        advance(done, ArtifactProduced(step_id="publish", artifact=Artifact("c")), now=NOW)


def test_failed_step_never_silently_completes():
    """Mirrors recipe_service.py:569-581 — a failed run takes an explicit re-run path."""
    run = _run(status=RunStatus.FAILED, steps=(
        StepRecord(id="draft", status=StepStatus.FAILED, attempts=3, error="boom"),
        StepRecord(id="review", gate=Gate.REVIEW),
        StepRecord(id="publish"),
    ))
    with pytest.raises(InvalidEvent):
        advance(run, ArtifactProduced(step_id="draft", artifact=Artifact("late.md")), now=NOW)


# --- the RunStore port ------------------------------------------------------------------


def test_runstore_is_a_runtime_checkable_port():
    class _Store:
        def load(self, run_id):
            raise KeyError(run_id)

        def save(self, run, *, expected_version):
            raise ConcurrentModification(run.run_id)

        def discard_artifact(self, run_id, step_id, artifact):
            pass

        def list_runs(self):
            return []

    assert isinstance(_Store(), RunStore)
    assert not isinstance(object(), RunStore)


def test_concurrent_modification_is_this_modules_contract():
    assert issubclass(ConcurrentModification, Exception)
    assert issubclass(InvalidEvent, Exception)


# --- import hygiene ---------------------------------------------------------------------


def test_kernel_is_a_leaf_module():
    """The kernel imports contract types only — no services, no domain, no os.path.

    Asserted in a SUBPROCESS: mutating this interpreter's sys.modules would leave every
    later test monkeypatching a stale module object while the code under test re-imports
    fresh ones — module-identity corruption that poisons the rest of the suite.
    """
    import subprocess
    import sys

    code = (
        "import sys; import grain.engine.kernel; "
        "bad = [m for m in sys.modules if m.startswith(('grain.services', 'grain.domain'))]; "
        "sys.exit(1 if bad else 0)"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=60)
    assert proc.returncode == 0, proc.stderr.decode()

    import grain.engine.kernel as kernel

    source = open(kernel.__file__).read()
    assert "os.path" not in source
    assert "import os" not in source


def test_cli_does_not_import_the_engine():
    """The kernel is off the startup graph — `grain status` cannot be broken by it."""
    import subprocess
    import sys

    code = (
        "import sys; import grain.cli; "
        "sys.exit(1 if any(m.startswith('grain.engine') for m in sys.modules) else 0)"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=60)
    assert proc.returncode == 0, proc.stderr.decode()


def test_event_union_covers_the_vocabulary():
    """AdvanceEvent is the closed set a driver can emit."""
    assert set(AdvanceEvent.__args__) == {
        StepStarted,
        ArtifactProduced,
        StepFailed,
        GateApproved,
        GateRejected,
    }
