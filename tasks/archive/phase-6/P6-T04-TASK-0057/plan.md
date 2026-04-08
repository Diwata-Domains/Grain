# Plan: TASK-0057

## Approach

Add adapter metadata fields to task templates and parser alias handling in a backward-compatible way. Validate both new-field parsing and legacy packet behavior through unit and command-level tests.

## Model Selection
- `frontier_model` is appropriate because this task touches cross-file packet contracts (template + parser + validator behavior expectations) and must preserve compatibility.

---

## Step 1 — Update templates

Add `Primary Adapter` and `Secondary Adapters` metadata lines to task packet templates with safe defaults (`none`).

---

## Step 2 — Update parser behavior

Adjust packet metadata parsing so adapter keys are available as `primary_adapter` and `secondary_adapters`.

---

## Step 3 — Add compatibility tests and verify

Add parser tests for adapter fields and integration coverage showing packets without adapter fields still validate.

---

## Verification

Run:
- `./.venv/bin/pytest -q tests/test_packet_status.py tests/test_packet_file_validation.py tests/test_task_create_cmd.py tests/test_task_validate_cmd.py`
- `./.venv/bin/pytest -q`
