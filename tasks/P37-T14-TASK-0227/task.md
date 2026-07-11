# Task: engine/kernel.py — RunStore port + pure advance() reducer

## Metadata
- **ID:** TASK-0227
- **Status:** review
- **Phase:** 37 — Workflow contract & engine extraction
- **Backlog:** P37-T14
- **Packet Path:** tasks/P37-T14-TASK-0227/
- **Dependencies:** TASK-0226 (P37-T13, done — grain.contracts.workflow vocabulary)
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Create the leaf module `src/grain/engine/kernel.py`: the `RunStore` Protocol (the port Diwa's
Postgres store and grain's filesystem store both implement), the `Event`/`Effect`/`Transition`
vocabulary, and a pure `advance(run, event, *, now, max_attempts) -> Transition` reducer that
re-expresses the recipe engine's real transition semantics over `grain.contracts.workflow` types
with zero I/O.

## Why This Task Exists
Diwa's Missions executor (capability register: Workflow→Grain) must run protocol-shaped missions
over Postgres without importing grain's filesystem engine. The reducer is the shared semantics;
stores are per-product. This is the load-bearing dependency for Diwa's PostgresRunStore + executor,
and for P37-T15 (FilesystemRunStore) and P37-T17 (recipe engine swap).

## Scope
- `src/grain/engine/__init__.py` + `src/grain/engine/kernel.py` — new leaf modules
- Events: step started / artifact produced / step failed / gate approved / gate rejected
- Effects: `DiscardArtifact` (the reject-path delete at `services/recipe_service.py:739`,
  expressed as data the driver applies — the reducer never touches disk)
- `RunStore` Protocol: `load`, `save(run, *, expected_version)` raising `ConcurrentModification`,
  `discard_artifact`, `list_runs()` ordered by `created` (never lexical id sort)
- Property/behaviour tests in `tests/test_engine_kernel.py`

## Constraints
- `advance()` performs zero I/O; asserted with a spy RunStore that raises on any call
- `grain.engine.kernel` imports no `grain.services`, no `grain.domain`, no `os.path`
  (types come from `grain.contracts.workflow` only) — asserted by a test
- NOT wired into `grain/__init__.py` or any CLI import path (demo-safe: off the startup graph)
- Transition semantics mirror the recipe engine's attested behaviour (completion only via
  produced artifact; REVIEW gate halts at AWAITING_GATE; reject discards artifact and re-arms)
- `step_failed` increments attempts exactly once per event; FAILED only at attempts >= max_attempts

## Escalation Conditions
- If mirroring engine semantics would require importing engine code, stop — the packet's premise
  (a pure leaf) is broken and the founder decides.
- Any need to modify `grain.contracts.workflow` types (frozen contract, P37-T13 sealed).
