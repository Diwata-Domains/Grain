# Plan: TASK-0063

## Approach

Add a dedicated `workflow` CLI group and implement `workflow next` as a thin wrapper over the evaluator service. Keep behavior read-only and return a stable machine-readable payload for automation while preserving human-readable text output for terminal use.

---

## Step 1 — Add Workflow CLI Surface

Create `src/forge/cli/workflow.py` with `workflow` group and `next` subcommand, then register the group in the root CLI command tree.

---

## Step 2 — Wire Evaluator Output

Invoke `evaluate_workflow_state` and expose its fields in text and JSON forms, including explicit stop reasons and blocking reasons for non-advancing states.

---

## Step 3 — Add Command Tests

Add CLI tests for:
- single ready task -> `task_execute`
- conflicting ready tasks -> explicit stop reason
- JSON output shape containing the evaluation payload

---

## Verification

- `.venv/bin/pytest -q tests/test_workflow_state_service.py tests/test_workflow_next_cmd.py`
- `.venv/bin/forge task validate --id TASK-0063`
- `.venv/bin/forge docs validate`
- `.venv/bin/pytest -q`
