# Plan: TASK-0182

## Approach

Treat verification state as a first-class closure precondition, then reuse the same validator output in both `workflow next` and `task close` so operators see one consistent set of review-close blockers.

---

## Step 1 — Tighten closure validation

Update `validate_closure` so pending verification blocks closure outright and failed verification requires an explicit waive-or-resolve decision rather than silently passing under the default completion policy.

---

## Step 2 — Surface blockers in workflow state

Change the review branch of `workflow_service.py` to run closure validation before routing to `task_close`, so review packets with unresolved verification stay in review with explicit blocker reasons.

---

## Step 3 — Keep the CLI output actionable

Make `grain task close` print the closure blocker details before raising, and extend the focused tests for validator, workflow, and close-command behavior.

---

## Verification

Run `/Users/barbaricum/diwata-labs/.venv/bin/python -m pytest -q tests/test_verify_submit_cmd.py tests/test_command_groups.py tests/test_closure_validation.py tests/test_workflow_state_service.py tests/test_task_close_cmd.py`.
