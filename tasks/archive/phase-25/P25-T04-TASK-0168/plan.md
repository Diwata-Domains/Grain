# Plan: TASK-0168

## Approach

Keep this slice in shipped guidance and regression coverage. The database adapter already encodes review hints in its profile, so this task should surface those expectations in the operator-facing docs and lock them with release-surface tests.

---

## Step 1 — Audit existing shipped guidance

Review the README and runtime agent guidance to see where desktop, Obsidian, office, and other non-code workflows already define explicit operator rules.

---

## Step 2 — Add database review and validation guidance

Add database-specific instructions covering adapter choice, narrow context loading, destructive migration risk, rollback expectations, and schema/query drift.

---

## Step 3 — Lock the guidance into regression tests

Extend the shipped release-surface tests so the database guidance is checked automatically and then record the exact verification slice in `results.md`.

---

## Verification

Run the focused release-surface, adapter-profile, and database integration tests. Confirm the shipped docs mention `database_adapter` and the key review risks without implying any live database execution surface.
