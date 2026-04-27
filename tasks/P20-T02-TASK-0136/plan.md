# Plan: TASK-0136

## Approach

Extend `next_task_id()` to scan the full `tasks/` tree so archived packet directories contribute to the maximum observed task number, then codify the expected behavior with focused archive-aware tests.

---

## Step 1 — Update allocator traversal

Change the task ID allocator to include nested packet directories under `tasks/archive/` instead of only scanning top-level active packet directories.

---

## Step 2 — Add archive-aware regression tests

Add coverage for archived packet directories contributing to the next ID and for plain archive container directories being ignored.

---

## Step 3 — Verify focused task-ID behavior

Run the dedicated task-ID test module to confirm the allocator still handles missing dirs, mixed legacy names, gaps, and archive traversal correctly.

---

## Verification

Run `.venv/bin/python -m pytest -q tests/test_task_id.py` and confirm all task-ID allocator tests pass.
