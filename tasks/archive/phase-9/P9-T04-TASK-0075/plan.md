# Plan: TASK-0075

## Approach

Extend existing task-level orchestration service with a phase-level planner that converts a phase summary (and optional candidate titles) into a proposal-only `OrchestratorPlan` containing ordered packet candidates, dependency links, cross-domain flags, and split recommendations.

---

## Step 1 — Add Phase-Level Service Function

Implement `build_phase_level_plan(...)` in `src/grain/services/orchestration_service.py` with validation, adapter profile loading, candidate shaping, and deterministic plan output.

---

## Step 2 — Encode Dependency Chain and Replan Signals

Generate candidate dependency chains and domain links across candidate sequence; include split recommendations for multi-segment or replan-oriented phase summaries.

---

## Step 3 — Add Focused Tests

Extend `tests/test_orchestration_service.py` to verify phase-level behavior for summary splitting, explicit candidate titles, and required summary validation.

---

## Verification

- `.venv/bin/pytest -q tests/test_orchestration_service.py tests/test_orchestrator_domain.py tests/test_adapter_capability.py`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0075`
- `.venv/bin/pytest -q`
