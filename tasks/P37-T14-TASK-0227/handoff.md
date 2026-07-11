# Handoff: TASK-0227

## For P37-T15 (FilesystemRunStore + conformance suite)

- Implement `grain.engine.kernel.RunStore` over the exact `recipe_store.py` layout. The port
  is four methods; the version token type is store-chosen (`object`) — mtime/etag is fine.
- `save` must raise `kernel.ConcurrentModification` (import it from the kernel, do not mint a
  sibling); `load` raises `kernel.UnknownRun`.
- `list_runs()` newest-first by `Run.created`. The docstring on the port says why lexical id
  sort is wrong — keep the conformance suite asserting it with ids that would interleave
  (`run-2` vs `run-10`).
- The conformance suite must be store-agnostic: Diwa's PostgresRunStore imports and passes the
  same suite.

## For the Diwa Missions executor (products/diwa)

- Depend on `grain.contracts.workflow` for types and `grain.engine.kernel` for
  `advance()` + the port. Do NOT import `grain.services.*` or `grain.domain.*`.
- Driver loop shape: `run = store.load(id)` → observe the world → `t = advance(run, event,
  now=..., max_attempts=...)` → apply `t.effects` (each `DiscardArtifact` →
  `store.discard_artifact(...)`) → `store.save(t.run, expected_version=v)`; on
  `ConcurrentModification`, reload and re-advance — never blind-write.
- Effects are applied BEFORE save in the reference ordering used by the recipe engine
  (artifact state changes land first, then run state: `recipe_store` writes artifact-then-run).

## Sharp Edges

- `Run`/`StepRecord` are frozen — every transition builds new values with
  `dataclasses.replace`. Do not add mutation helpers.
- `advance()` raises `InvalidEvent` for: terminal runs, events off the cursor, gate decisions
  when not AWAITING_GATE, and artifacts landing on a FAILED step. Drivers treat `InvalidEvent`
  as a programming error or a stale read (reload and re-inspect), never retry blindly.
- `StepStarted` is idempotent on `started` (first start wins) but always flips status to
  RUNNING — a re-entrant driver is safe.
- The retry bound is kernel-new: the filesystem engine retries unboundedly via `resume`.
  When P37-T17 swaps the engine onto the kernel, pass `max_attempts` large or expose it —
  do not let the default silently change `grain recipe` behaviour.
