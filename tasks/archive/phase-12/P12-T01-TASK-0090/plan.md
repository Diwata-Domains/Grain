# Plan: TASK-0090

## Approach

Implement a typed domain model and YAML-backed config loader for workflow loop settings, with explicit validation rules for supervision level and stage agent invocation mode.

---

## Step 1 — Add Domain Types

Create workflow-loop config dataclasses for supervision level and per-stage agent settings.

---

## Step 2 — Add Config Loader Service

Load `docs/runtime/workflow_loop.yaml`, validate required shape and values, and support override hooks for future CLI flags.

---

## Step 3 — Add Runtime Config + Tests

Add default runtime YAML and tests for success/failure paths to lock the config contract.

---

## Verification

- `python3 -m py_compile src/grain/domain/workflow_loop.py src/grain/services/workflow_loop_config_service.py tests/test_workflow_loop_config_service.py`
- `.venv/bin/pytest -q tests/test_workflow_loop_config_service.py`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0090`
- `.venv/bin/pytest -q`
