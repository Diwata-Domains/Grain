# Plan: TASK-0185

## Approach

Add narrow, read-only drift checks to `workflow_service.py` so clearly invalid workflow state is surfaced before normal execution routing, then prove those states with focused workflow-state tests.

---

## Step 1 — Detect missing active-task pointers

If the backlog says a task is already `in_progress`, `review`, `blocked`, or `needs_fix` but `current_task.md` is unset, stop with an explicit workflow-state drift blocker instead of proceeding as if no task were active.

---

## Step 2 — Detect invalid packet/backlog mismatches

If an active packet exists, compare its status to the matching backlog entry and stop only for clearly invalid combinations like `ready` vs `in_progress`, while tolerating the small backlog lag that happens during normal progression.

---

## Step 3 — Lock the behavior with tests

Add focused tests for the new drift blockers and confirm the existing blocked/review/done behaviors still work.

---

## Verification

Run `/Users/barbaricum/diwata-labs/.venv/bin/python -m pytest -q tests/test_workflow_state_service.py`.
