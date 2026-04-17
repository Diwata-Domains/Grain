# Plan: TASK-0074

## Approach

Implement a read-only orchestration service that ranks adapter relevance from scope text and capability signals, then emits a typed `OrchestratorPlan` proposal with deterministic packet candidates and dependency hints. Keep all outputs proposal-only and file-backed through tests.

---

## Step 1 — Add Task-Level Orchestration Service

Create `src/grain/services/orchestration_service.py` with `build_task_level_plan(...)` returning `(CommandResult, OrchestratorPlan | None)`. Load adapter profiles, score relevance, and generate plan IDs/candidate packets.

---

## Step 2 — Encode Proposal Semantics

Generate `packet_candidates`, `dependency_links`, `cross_domain_flags`, and `split_recommendations` for multi-adapter scopes while preserving graceful fallback to single generic candidate when no adapter signals match.

---

## Step 3 — Add Service Tests

Add `tests/test_orchestration_service.py` covering:
- matching adapter detection
- multidomain split/dependency output
- no-signal graceful degradation
- missing adapter profile config handling
- empty-scope validation

---

## Verification

- `.venv/bin/pytest -q tests/test_orchestration_service.py tests/test_orchestrator_domain.py tests/test_adapter_capability.py`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0074`
- `.venv/bin/pytest -q`
