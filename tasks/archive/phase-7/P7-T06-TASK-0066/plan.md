# Plan: TASK-0066

## Approach

Exercise the onboarding path through CLI-level integration tests using `forge init` options introduced in earlier Phase 7 tasks, then align `README.md` and `current_focus.md` so documented guidance matches what the integration coverage verifies.

---

## Step 1 — Add Onboarding Integration Coverage

Create a new phase-level integration test module that validates init scaffolding outputs, adapter selection reporting, and starter packet bootstrap behavior in both normal and dry-run paths.

---

## Step 2 — Update Onboarding Docs

Update `README.md` to reflect the currently supported onboarding command shape and update `docs/working/current_focus.md` to reflect the next review/phase-boundary priorities.

---

## Step 3 — Verify And Prepare Review Handoff

Run targeted test commands plus full suite validation, then complete `results.md` and `handoff.md` and move packet status to `review`.

---

## Verification

- `.venv/bin/pytest -q tests/test_phase7_integration.py`
- `.venv/bin/pytest -q tests/test_init_service.py tests/test_task_create_cmd.py`
- `.venv/bin/pytest -q`
