# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT
"""The workflow kernel: a pure ``advance()`` reducer and the ``RunStore`` port.

This module distills the recipe engine's attested transition semantics
(`services/recipe_service.py`) into a function over the frozen `grain.contracts.workflow`
types. Three promises hold it in place:

**Pure.** ``advance(run, event) -> Transition`` reads nothing and writes nothing — no clock
(``now`` is a parameter), no filesystem, no store. Anything the world must do comes back as an
:class:`Effect` the driver applies. The reject-path artifact delete that lives at
``recipe_service.py:739`` as an ``unlink()`` survives here as :class:`DiscardArtifact` — data,
not I/O — which is how the same reducer can serve grain's filesystem runs and Diwa's Postgres
missions.

**A leaf.** Imports `grain.contracts.workflow` and stdlib only. Never `grain.services`,
never `grain.domain`, never the CLI. `tests/test_engine_kernel.py` asserts the separation.

**One port.** :class:`RunStore` is the whole surface a storage backend implements. Optimistic
concurrency is the store's job (``save(..., expected_version)`` raising
:class:`ConcurrentModification`), ordering is by ``created`` — a store that sorts run ids
lexically will interleave ``run-10`` before ``run-2`` and is wrong.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Protocol, Union, runtime_checkable

from grain.contracts.workflow import (
    Artifact,
    Gate,
    Run,
    RunStatus,
    StepRecord,
    StepStatus,
)

DEFAULT_MAX_ATTEMPTS = 3

__all__ = [
    "AdvanceEvent",
    "ArtifactProduced",
    "ConcurrentModification",
    "DEFAULT_MAX_ATTEMPTS",
    "DiscardArtifact",
    "Effect",
    "GateApproved",
    "GateRejected",
    "InvalidEvent",
    "RunStore",
    "StepFailed",
    "StepStarted",
    "Transition",
    "UnknownRun",
    "advance",
]


# --- errors -----------------------------------------------------------------------------


class InvalidEvent(Exception):
    """The event does not apply to the run in its current state (wrong step, wrong status)."""


class ConcurrentModification(Exception):
    """``save(expected_version=...)`` found the run changed underneath the caller."""


class UnknownRun(KeyError):
    """``load``/``discard_artifact`` was asked about a run the store has never seen."""


# --- events: what the driver observed ---------------------------------------------------


@dataclass(frozen=True)
class StepStarted:
    """Work on the cursor step began (an agent was invoked, a human picked it up)."""

    step_id: str


@dataclass(frozen=True)
class ArtifactProduced:
    """The cursor step's output artifact landed, present and non-empty.

    The *driver* attests presence/non-emptiness (`recipe_service.py:340-349`); the reducer
    only ever sees the claim as data.
    """

    step_id: str
    artifact: Artifact


@dataclass(frozen=True)
class StepFailed:
    """The attempt on the cursor step failed (agent error, timeout, empty output)."""

    step_id: str
    error: str


@dataclass(frozen=True)
class GateApproved:
    """A human approved the review gate; the produced artifact stands."""

    step_id: str


@dataclass(frozen=True)
class GateRejected:
    """A human rejected the review gate; the artifact is discarded and the step re-arms."""

    step_id: str


AdvanceEvent = Union[StepStarted, ArtifactProduced, StepFailed, GateApproved, GateRejected]


# --- effects: what the driver must now do -----------------------------------------------


@dataclass(frozen=True)
class DiscardArtifact:
    """Remove a rejected step's artifact so completion cannot re-fire from stale output.

    The filesystem store unlinks a file; a Postgres store nulls a column. Same meaning.
    """

    run_id: str
    step_id: str
    artifact: Artifact


Effect = Union[DiscardArtifact]


@dataclass(frozen=True)
class Transition:
    """The reducer's whole answer: the next run state and the effects to apply."""

    run: Run
    effects: tuple[Effect, ...] = ()


# --- the store port ----------------------------------------------------------------------


@runtime_checkable
class RunStore(Protocol):
    """What a storage backend must offer a driver. The reducer never touches one.

    Implementations exist per product: grain's FilesystemRunStore (P37-T15) over
    ``docs/recipes/runs/<id>/run.json``, Diwa's PostgresRunStore for Missions. The
    store-agnostic conformance suite (P37-T15) is the contract's teeth.
    """

    def load(self, run_id: str) -> Run:
        """Return the run, or raise :class:`UnknownRun`."""
        ...

    def save(self, run: Run, *, expected_version: object) -> object:
        """Persist atomically iff the stored version still equals ``expected_version``.

        Returns the new version token. Raises :class:`ConcurrentModification` when another
        writer got there first — the caller reloads and re-advances, never blind-writes.
        """
        ...

    def discard_artifact(self, run_id: str, step_id: str, artifact: Artifact) -> None:
        """Apply a :class:`DiscardArtifact` effect (the delete at recipe_service.py:739)."""
        ...

    def list_runs(self) -> list[Run]:
        """All runs, newest first by ``created`` — never lexical id order."""
        ...


# --- the reducer --------------------------------------------------------------------------


def advance(
    run: Run,
    event: AdvanceEvent,
    *,
    now: str,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
) -> Transition:
    """Apply one observed event to a run, returning the next state and pending effects.

    Pure: same inputs, same answer; no I/O, no clock, no store. ``now`` is an ISO-8601
    timestamp the driver supplies for ``started``/``ended`` stamps.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")

    if run.status in (RunStatus.DONE, RunStatus.FAILED):
        raise InvalidEvent(f"run {run.run_id!r} is terminal ({run.status.value})")

    step_id = event.step_id
    if step_id != run.cursor:
        raise InvalidEvent(
            f"event targets step {step_id!r} but the cursor is on {run.cursor!r}"
        )
    record = run.step(step_id)

    if isinstance(event, (GateApproved, GateRejected)):
        if run.status is not RunStatus.AWAITING_GATE:
            raise InvalidEvent(
                f"run {run.run_id!r} is not awaiting a gate (status {run.status.value!r})"
            )
        if isinstance(event, GateApproved):
            return _approve(run, record, now)
        return _reject(run, record)

    if isinstance(event, StepStarted):
        started = _replace_step(
            run,
            replace(record, status=StepStatus.RUNNING, started=record.started or now),
        )
        return Transition(run=replace(started, status=RunStatus.RUNNING))

    if isinstance(event, ArtifactProduced):
        if record.status is StepStatus.FAILED:
            # recipe_service.py:569-581 — a failed step never silently completes;
            # it must re-enter through an explicit retry (StepStarted after re-arm).
            raise InvalidEvent(f"step {step_id!r} is failed; a late artifact does not complete it")
        return _complete(run, record, event.artifact, now)

    if isinstance(event, StepFailed):
        return _fail(run, record, event.error, now, max_attempts)

    raise InvalidEvent(f"unknown event {event!r}")  # pragma: no cover — closed union


# --- transitions (mirroring recipe_service._complete_and_advance and friends) --------------


def _complete(run: Run, record: StepRecord, artifact: Artifact, now: str) -> Transition:
    done = replace(
        record,
        status=StepStatus.DONE,
        artifact=artifact,
        ended=now,
        error=None,
        attempts=max(record.attempts, 1),
    )

    if record.gate is Gate.REVIEW:
        gated = replace(done, status=StepStatus.AWAITING_GATE)
        halted = replace(_replace_step(run, gated), status=RunStatus.AWAITING_GATE)
        return Transition(run=halted)  # cursor unchanged at a gate

    return Transition(run=_advance_cursor(_replace_step(run, done), record.id))


def _approve(run: Run, record: StepRecord, now: str) -> Transition:
    approved = replace(record, status=StepStatus.DONE, ended=now)
    return Transition(run=_advance_cursor(_replace_step(run, approved), record.id))


def _reject(run: Run, record: StepRecord) -> Transition:
    effects: tuple[Effect, ...] = ()
    if record.artifact is not None:
        effects = (
            DiscardArtifact(run_id=run.run_id, step_id=record.id, artifact=record.artifact),
        )
    rearmed = replace(record, status=StepStatus.PENDING, artifact=None, ended=None)
    # cursor unchanged — the same step is re-rendered and re-authored (recipe_service.py:747)
    return Transition(
        run=replace(_replace_step(run, rearmed), status=RunStatus.RUNNING),
        effects=effects,
    )


def _fail(run: Run, record: StepRecord, error: str, now: str, max_attempts: int) -> Transition:
    attempts = record.attempts + 1
    if attempts >= max_attempts:
        dead = replace(
            record, status=StepStatus.FAILED, attempts=attempts, error=error, ended=now
        )
        return Transition(run=replace(_replace_step(run, dead), status=RunStatus.FAILED))
    rearmed = replace(record, status=StepStatus.PENDING, attempts=attempts, error=error)
    return Transition(run=replace(_replace_step(run, rearmed), status=RunStatus.RUNNING))


# --- helpers ---------------------------------------------------------------------------------


def _replace_step(run: Run, record: StepRecord) -> Run:
    return replace(run, steps=tuple(record if s.id == record.id else s for s in run.steps))


def _advance_cursor(run: Run, from_step_id: str) -> Run:
    """Move past ``from_step_id``: next step and RUNNING, or DONE with the cursor pinned.

    The cursor stays on the final step id when the run completes — the run.json invariant
    (recipe_engine_spec §2.2) that P37-T17's byte-compat depends on.
    """
    ids = [s.id for s in run.steps]
    index = ids.index(from_step_id)
    if index + 1 == len(ids):
        return replace(run, status=RunStatus.DONE)
    return replace(run, status=RunStatus.RUNNING, cursor=ids[index + 1])
