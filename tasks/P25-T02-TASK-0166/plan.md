# Plan: TASK-0166

## Approach

Keep the first database behavior small and direct-select. Database artifacts do not yet have useful graph connectivity, so the adapter should select its files by profile patterns, then apply one narrow priority pass that lifts schema and migrations first and keeps unrelated application code out of the bundle.

---

## Step 1 — Audit the existing selection pipeline

Inspect where adapter candidates are gathered, filtered, and reranked so the database behavior can slot into the same path used by other non-graph adapters.

---

## Step 2 — Add database-specific prioritization

Make `database_adapter` select its candidates without requiring graph traces, then add a small ordering helper that prioritizes schema and migration artifacts ahead of model-adjacent files.

---

## Step 3 — Verify with focused integration coverage

Add a focused database-adapter integration test that proves schema, migrations, and models are selected while unrelated app code is left out, then record the verification slice in `results.md`.

---

## Verification

Run the focused adapter-profile, release-surface, and database-adapter integration tests. Confirm schema and migration files are selected, unrelated code stays out of the bundle, and model-adjacent files are still available as secondary context.
