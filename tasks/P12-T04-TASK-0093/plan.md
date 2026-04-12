# Plan: TASK-0093

## Approach

Add a minimal accepted-plan lifecycle command and loop-side selection hook so conflicting ready tasks can be resolved by accepted orchestration strategy before fallback gating.

---

## Step 1 — Add Plan Acceptance Command

Implement `grain orchestrate accept --plan <id>` to mark a proposal JSON status as `accepted`.

---

## Step 2 — Add Loop Ordering Integration

When loop hits conflicting ready tasks, consult latest accepted plan in proposals and activate the first matching ready task from plan order.

---

## Step 3 — Add Integration Tests

Add tests for acceptance command success/failure and loop activation behavior driven by accepted plan ordering.

---

## Verification

- `python3 -m py_compile src/grain/cli/orchestrate.py src/grain/services/workflow_loop_service.py tests/test_orchestrate_cmd.py tests/test_workflow_loop_cmd.py`
- `.venv/bin/pytest -q tests/test_orchestrate_cmd.py tests/test_workflow_loop_cmd.py tests/test_workflow_run_cmd.py tests/test_workflow_next_cmd.py`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0093`
- `.venv/bin/pytest -q`
