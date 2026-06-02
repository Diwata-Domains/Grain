# Plan: TASK-0169

## Approach

Treat this as validation and closeout only. Add one integrated database smoke path that exercises the current adapter slice end-to-end, then record the verification and phase-close metrics rather than expanding the feature surface further.

---

## Step 1 — Audit the existing database slice

Review the schema/migration, query/repository, and review-guidance work so the smoke slice covers the real current scope rather than inventing new behavior.

---

## Step 2 — Add the integrated smoke check

Add one focused export-oriented smoke test that proves the main database surfaces appear together under a persistence-oriented objective.

---

## Step 3 — Close the packet and phase cleanly

Record the exact test slice in `results.md`, prepare the handoff artifact, and update the phase metrics so `grain phase close` can seal Phase 25 without drift.

---

## Verification

Run the focused database integration, adapter-profile, and release-surface tests. Confirm the integrated smoke slice covers schema, migrations, queries, repositories, and the shipped review guidance together.
