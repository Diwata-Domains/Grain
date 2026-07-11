# Results: TASK-0227

## What Was Built

`src/grain/engine/kernel.py` (new leaf module, plus `engine/__init__.py` package marker) and
`tests/test_engine_kernel.py` (19 tests, red-first).

- **Events** (frozen dataclasses): `StepStarted`, `ArtifactProduced`, `StepFailed`,
  `GateApproved`, `GateRejected`; closed union `AdvanceEvent`.
- **Effects**: `DiscardArtifact(run_id, step_id, artifact)` — the reject-path unlink at
  `recipe_service.py:739` expressed as data; union `Effect`.
- **`Transition`**: `(run: Run, effects: tuple[Effect, ...])`.
- **`advance(run, event, *, now, max_attempts=3) -> Transition`** — pure reducer over the
  frozen contract types via `dataclasses.replace`; `now` is a driver-supplied ISO timestamp
  (no clock inside).
- **`RunStore`** (runtime-checkable Protocol): `load` (raises `UnknownRun`),
  `save(run, *, expected_version)` (raises `ConcurrentModification`), `discard_artifact`,
  `list_runs()` documented newest-first by `created` — never lexical id order.

## Semantics Mirrored (attested anchors)

- Completion → gate/advance/complete mirrors `_complete_and_advance`
  (`recipe_service.py:612-686`): REVIEW gate halts run+step at AWAITING_GATE with cursor
  unchanged; final step → run DONE with cursor pinned (run.json invariant §2.2); else cursor
  advances, run RUNNING. Completed steps get `attempts = max(attempts, 1)` (`:635-636`).
- Reject mirrors `reject_gate` (`:716-749`): DiscardArtifact effect, step PENDING,
  `artifact=None`, `ended=None`, run RUNNING, cursor unchanged.
- Approve mirrors `approve_gate` (`:689-714`): artifact stands, step DONE, cursor advances.
- Failed-step guard mirrors `:569-581`: a FAILED step rejects a late artifact — completion
  is never silent after failure.
- **New (kernel-only) semantics**: bounded retries — `StepFailed` increments `attempts`
  exactly once per event, re-arms PENDING below `max_attempts`, flips step+run FAILED at
  `attempts >= max_attempts`. The filesystem engine has no retry bound; Missions need one.

## Acceptance Evidence

- Reject → `DiscardArtifact` + `artifact=None`: `test_gate_rejected_discards_the_artifact_and_rearms_the_step`
- Zero I/O: `advance()` takes no store at all (`test_advance_signature_admits_no_store`);
  input run untouched (frozen; `test_advance_is_pure_and_never_calls_the_store`)
- Attempts exactly-once + FAILED only at max: `test_step_failed_*` (two tests, loop to 3)
- REVIEW gate halts at AWAITING_GATE: `test_artifact_produced_on_a_review_step_halts_at_the_gate`
- Import purity: `test_kernel_is_a_leaf_module` (no `grain.services`/`grain.domain` in the
  import set, no `os.path`/`import os` in source) and `test_cli_does_not_import_the_engine`
  (subprocess: `import grain.cli` pulls no `grain.engine.*`)

## Test Runs

- `uv run pytest tests/test_engine_kernel.py` — 19 passed
- Full suite — see handoff (run at close time)

## Deviations From Plan

- `UnknownRun` documented on the port alongside `ConcurrentModification` (both are the
  store's contract vocabulary); `InvalidEvent` covers reducer-side rejection. No `KernelError`
  base — three precise exceptions beat one vague one.
