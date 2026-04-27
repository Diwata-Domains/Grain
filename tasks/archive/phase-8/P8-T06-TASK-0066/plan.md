# Plan: TASK-0066

## Approach

Implement a dedicated task-prepare service and command that validate packet prerequisites for a specific task ID, map status to recommended prompt entrypoint, and return explicit missing-input signals in text/JSON formats.

---

## Step 1 — Add Task Prepare Service

Create a read-only service that locates a packet by task ID, checks required packet files, determines recommended prompt, and reports missing inputs.

---

## Step 2 — Add CLI Command

Add `task prepare --id TASK-####` command that calls the service and emits stable text/JSON output without mutating state.

---

## Step 3 — Add Command Tests

Add tests for:
- success when prerequisites exist
- missing packet file behavior
- JSON output payload
- missing packet usage error

---

## Verification

- `.venv/bin/pytest -q tests/test_task_prepare_cmd.py tests/test_task_next_cmd.py tests/test_phase_next_cmd.py tests/test_workflow_next_cmd.py tests/test_workflow_state_service.py`
- `.venv/bin/forge task validate --id TASK-0066`
- `.venv/bin/forge docs validate`
- `.venv/bin/pytest -q`
