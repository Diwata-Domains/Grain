# Plan: TASK-0059

## Approach

Extend the existing adapter-aware context pipeline by carrying adapter review/validation hints in bundle metadata, then surface those hints in CLI and markdown export outputs with adapter-neutral-safe defaults. Keep output changes additive and verify via focused context build/export tests plus full regression tests.

---

## Step 1 — Extend context metadata with adapter hint fields

Update context bundle assembly to populate `review_focus_hints` and `test_or_validation_hints` from the resolved adapter profile while preserving empty-list defaults when no adapter is active.

---

## Step 2 — Surface hints in build/export outputs

Expose adapter hint details in `forge context build` and `forge context export` text outputs, include `adapter_context` in JSON export payloads, and render an adapter hint section in markdown exports for active adapters.

---

## Step 3 — Add and run focused validation

Add or update tests for bundle metadata, build command output, JSON export output, and markdown export rendering; then run focused context suites and the full repository suite to confirm no regressions.

---

## Verification

Run:
- `./.venv/bin/pytest -q tests/test_context_build.py tests/test_context_build_cmd.py tests/test_context_export.py tests/test_context_export_cmd.py`
- `./.venv/bin/pytest -q`
