# Plan: TASK-0137

## Approach

Keep the evaluator read-only, but make it inspect the referenced packet status directly. If `current_task.md` points to a packet already marked `done`, treat that pointer as stale for routing purposes and continue evaluating backlog readiness from an idle state.

---

## Step 1 — Normalize active task status from packet metadata

Read the packet’s actual status from `task.md` before applying active-task routing so stale `current_task.md` state does not override terminal packet state.

---

## Step 2 — Ignore stale done pointers during evaluation

When the referenced packet is already `done`, treat the current task as non-active in the evaluator instead of routing through execute/review logic.

---

## Step 3 — Add targeted regression coverage

Add tests proving that blocked/review behavior still works and that a stale done pointer allows routing to the next ready task.

---

## Verification

Run `.venv/bin/python -m pytest -q tests/test_workflow_state_service.py tests/test_workflow_run_cmd.py` and confirm the focused workflow-state suite passes.
