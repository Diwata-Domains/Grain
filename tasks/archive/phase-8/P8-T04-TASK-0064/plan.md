# Plan: TASK-0064

## Approach

Implement `task next` as a thin command-layer projection of workflow evaluator output. It should return a single ready task when available, report planning-required when no ready task exists, and surface explicit stop details for blocked/ambiguous states.

---

## Step 1 — Add Task Selection Command

Add `task next` under `src/forge/cli/task.py` and wire it to `evaluate_workflow_state`.

---

## Step 2 — Map Evaluator Output to Task-Selection Output

Map evaluator states to task-focused outputs:
- `task_execute` + candidate -> next task
- `task_planning` -> planning required
- explicit stop reasons -> stopped with blockers

---

## Step 3 — Add Command Tests

Add tests for text candidate output, planning-required output, and JSON payload correctness.

---

## Verification

- `.venv/bin/pytest -q tests/test_workflow_state_service.py tests/test_workflow_next_cmd.py tests/test_task_next_cmd.py`
- `.venv/bin/forge task validate --id TASK-0064`
- `.venv/bin/forge docs validate`
- `.venv/bin/pytest -q`
