# Plan: TASK-0058

## Approach

Integrate primary-adapter awareness into context bundle assembly by reading packet metadata, loading adapter profiles, selecting adapter-relevant source files, and applying a simple priority heuristic from context priority rules. Preserve existing no-adapter behavior exactly.

## Model Selection
- `frontier_model` is appropriate because this task affects context assembly behavior, cross-file coordination, and compatibility guarantees.

---

## Step 1 — Add adapter-aware context helpers

Update context service to read `primary_adapter`, resolve adapter profiles, collect relevant file pattern matches, exclude ignored paths, and apply deterministic ordering bias from context priority rules.

---

## Step 2 — Wire adapter-biased sources into bundle output

Include adapter-selected source files in `export_metadata.sources` ahead of canonical/working docs while preserving packet files and deduplicating source paths.

---

## Step 3 — Validate behavior with focused tests

Add/extend context build tests to confirm adapter bias behavior and adapter-neutral fallback, then run focused context suites and full regression tests.

---

## Verification

Run:
- `./.venv/bin/pytest -q tests/test_context_build.py tests/test_context_build_cmd.py tests/test_context_show_cmd.py tests/test_context_export.py tests/test_context_export_cmd.py`
- `./.venv/bin/pytest -q`
