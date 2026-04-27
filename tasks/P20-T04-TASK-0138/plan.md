# Plan: TASK-0138

## Approach

Teach the current-phase parser to recognize an explicit `complete` marker, then have the workflow evaluator return a dedicated `project_complete` stop state and make `phase next` describe it as a no-op/project-complete condition instead of a task-ready state.

---

## Step 1 — Extend phase parsing

Add a terminal `complete` parse path alongside numbered phase parsing so `current_focus.md` can intentionally represent a finished project.

---

## Step 2 — Surface a dedicated workflow stop state

Return `project_complete` from workflow evaluation when the parsed phase is terminal, and map that state through the runner gate contract.

---

## Step 3 — Align phase-next output and focused tests

Update `phase next` reasoning for the complete state and add focused tests for both evaluator and phase-next behavior.

---

## Verification

Run `.venv/bin/python -m pytest -q tests/test_workflow_state_service.py tests/test_phase_next_cmd.py` and confirm the complete-state tests pass alongside existing workflow-state coverage.
