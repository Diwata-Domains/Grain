# Plan: TASK-0040

## Approach

Implement deterministic stage/role routing in the domain layer, then expose a service function that loads runtime model profiles and returns a `model select` decision. Cover selection behavior with focused unit tests and run full regression tests.

---

## Step 1 — Extend routing domain logic

Add stage mapping, role-signal matching, and default fallback selection in `routing.py` so selection can run without CLI coupling.

---

## Step 2 — Add model selection service

Create `model_service.py` to load `agent_profiles.md` through the existing adapter and return a structured selection decision plus command result state.

---

## Step 3 — Add and run tests

Add tests covering stage mapping, ambiguity escalation signals, review-oriented role selection, default behavior, and missing-config failure path.

---

## Verification

Run `.venv/bin/pytest tests/test_model_service.py tests/test_model_config_loader.py` and `.venv/bin/pytest` to confirm both targeted behavior and full-suite stability.
