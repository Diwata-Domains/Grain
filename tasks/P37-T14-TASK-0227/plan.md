# Plan: TASK-0227

## Approach

TDD, red first. Write the behaviour tests against the not-yet-existing `grain.engine.kernel`,
watch them fail on import, then build the module in one pass: event/effect vocabulary as frozen
dataclasses, `Transition` as (new run, effects tuple), `advance()` as a pure function over the
frozen `grain.contracts.workflow` types using `dataclasses.replace` — no mutation, no clock, no
filesystem. The `RunStore` Protocol and its two exception types (`ConcurrentModification`,
`UnknownRun`) sit in the same module so a store implementer imports exactly one address.

---

## Step 1 — Red: behaviour tests

`tests/test_engine_kernel.py`, driven by the backlog acceptance:
reject → `DiscardArtifact` effect + `artifact=None` + re-armed PENDING step; zero-I/O spy
(any RunStore call raises inside `advance()`); `step_failed` attempts exactly-once and FAILED
only at `max_attempts`; REVIEW gate halts at AWAITING_GATE; approve advances past the gate;
final-step completion → run DONE; wrong-step / wrong-state events raise `InvalidEvent`;
import-purity test (no `grain.services`, `grain.domain`, `os.path` in the kernel's import set).

---

## Step 2 — Green: the kernel

`src/grain/engine/kernel.py`: `StepStarted` / `ArtifactProduced` / `StepFailed` / `GateApproved`
/ `GateRejected` events; `DiscardArtifact` effect; `advance()` dispatching per event, mirroring
`_complete_and_advance` (gate → AWAITING_GATE with cursor unchanged; last step → DONE with cursor
pinned; else advance cursor), `reject_gate` (discard + re-arm), and bounded-retry failure.
`RunStore` Protocol: `load`, `save(run, *, expected_version)`, `discard_artifact`, `list_runs`.

---

## Step 3 — Refactor + suite

Tighten names/docstrings to grain idiom, then run the full grain suite to prove the leaf is off
every existing import path (no CLI regression possible if nothing imports it).

---

## Verification

`uv run pytest tests/test_engine_kernel.py` green; full `uv run pytest` green (1928+ tests, no
regressions); `python -c "import grain.cli"` does not pull `grain.engine` (asserted in the test);
`grain task close --id TASK-0227` validation passes after results/handoff are written.
