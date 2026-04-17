# Plan: TASK-0098

## Approach

Add a single integration test module that exercises the complete existing-project adoption slice. Use synthetic repo trees and CLI runner invocations for deterministic, local-only coverage.

---

## Step 1 — Add Phase 13 integration module

Create `tests/test_phase13_integration.py` and include broad coverage for onboard, scanner, and doc generation behaviors.

---

## Step 2 — Ensure minimum coverage target

Provide at least 15 tests spanning all required subareas and one end-to-end additive flow test.

---

## Step 3 — Validate full repository

Run targeted integration tests first, then docs/task validators, then full `pytest` to confirm no regressions.

---

## Verification

- `.venv/bin/pytest -q tests/test_phase13_integration.py`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0098`
- `.venv/bin/pytest -q`
