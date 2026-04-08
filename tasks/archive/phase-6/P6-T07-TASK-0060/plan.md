# Plan: TASK-0060

## Approach

Add narrow adapter-system test modules that verify coverage gaps for loader/metadata/context safety while avoiding runtime behavior changes. Reuse existing test patterns and fixtures, then validate with focused and full test runs.

---

## Step 1 — Add adapter loader and packet metadata coverage

Create tests that exercise adapter profile loading with optional hint fields and packet metadata parsing paths both with adapter metadata and without adapter metadata (legacy-safe path).

---

## Step 2 — Add context assembly adapter-safety coverage

Create tests for context assembly when `primary_adapter` is `none` and when it references an unknown adapter ID, confirming safe degradation and unchanged baseline behavior.

---

## Step 3 — Run validation and package artifacts

Run focused adapter/context suites and then full repository tests; update packet artifacts and working docs with results and reviewer handoff details.

---

## Verification

Run:
- `./.venv/bin/pytest -q tests/test_adapter_loading.py tests/test_adapter_context.py tests/test_adapter_domain.py tests/test_adapter_config_loader.py tests/test_packet_status.py tests/test_task_validate_cmd.py tests/test_context_build.py tests/test_context_build_cmd.py tests/test_context_export.py tests/test_context_export_cmd.py`
- `./.venv/bin/pytest -q`
