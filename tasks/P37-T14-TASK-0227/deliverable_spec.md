# Deliverable Spec: TASK-0227

## Required Output

### New Files
- `src/grain/engine/__init__.py` — package marker; exports nothing eagerly
- `src/grain/engine/kernel.py` — Event/Effect/Transition vocabulary, pure `advance()`,
  `RunStore` Protocol, `ConcurrentModification` / `UnknownRun` / `InvalidEvent` exceptions
- `tests/test_engine_kernel.py` — behaviour + purity + import-hygiene tests

### Modified Files
- none (leaf module; `grain/__init__.py` and the CLI import graph stay untouched)

## Acceptance Checklist
- [ ] `GateRejected` yields a `DiscardArtifact` effect and the step record's `artifact` is None
- [ ] `advance()` performs zero I/O — a spy RunStore that raises on any call proves the reducer
      never touches a store
- [ ] `StepFailed` increments `attempts` exactly once per event; step/run flip FAILED only at
      `attempts >= max_attempts`, else the step re-arms PENDING for retry
- [ ] A `Gate.REVIEW` step halts the run at `AWAITING_GATE` with the cursor unchanged
- [ ] `GateApproved` advances past the gate; on the final step the run is DONE with the cursor
      pinned to the last step id (run.json invariant §2.2)
- [ ] A test asserts `grain.engine.kernel` imports no `grain.services`, `grain.domain`, or
      `os.path`
- [ ] `RunStore` exposes `load`, `save(run, *, expected_version)` (raising
      `ConcurrentModification` on a stale version), `discard_artifact`, and `list_runs()` ordered
      by `created` — never lexical id sort (documented on the Protocol)
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- FilesystemRunStore or any store implementation (P37-T15)
- Conformance suite for stores (P37-T15)
- Touching `recipe_service.py` / `recipe_store.py` / `recipe_run.py` (P37-T17)
- Wiring into CLI, MCP, or `grain workflow` (P37-T18)
