# Plan: TASK-0092

## Approach

Harden workflow loop execution with explicit non-mutating preview mode and bounded-step safeguards, then update operator docs and tests so behavior is visible and stable.

---

## Step 1 — Add Guardrail Behavior

Implement `--dry-run` flow and default max-step safety cap in the loop service, keeping gate semantics unchanged.

---

## Step 2 — Improve Loop Output

Add clearer loop metadata (`steps_requested`) and per-step execution details (`dry_run`, `duration_ms`) in text/JSON outputs.

---

## Step 3 — Update Docs and Tests

Update runtime and README guidance for supervision-level risk framing, and add tests for dry-run/no-mutation and updated payload fields.

---

## Verification

- `python3 -m py_compile src/grain/cli/workflow.py src/grain/services/workflow_loop_service.py tests/test_workflow_loop_cmd.py`
- `.venv/bin/pytest -q tests/test_workflow_loop_cmd.py tests/test_workflow_run_cmd.py tests/test_workflow_next_cmd.py`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0092`
- `.venv/bin/pytest -q`
