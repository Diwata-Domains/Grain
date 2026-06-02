# Plan: TASK-0174

## Approach

Treat this as validation and closeout only. Add one integrated crawler smoke path that exercises the current adapter slice end-to-end, then record the verification and phase-close metrics rather than expanding the feature surface further.

---

## Step 1 — Audit the existing crawler slice

Review the crawl-config/selector, extraction-quality, and review-guidance work so the smoke slice covers the real current scope rather than inventing new behavior.

---

## Step 2 — Add the integrated smoke check

Add one focused export-oriented smoke test that proves the main crawler surfaces appear together under a quality-oriented objective.

---

## Step 3 — Close the packet and phase cleanly

Record the exact test slice in `results.md`, prepare the handoff artifact, and update the phase metrics so `grain phase close` can seal Phase 26 without drift.

---

## Verification

Run the focused crawler integration, adapter-profile, and release-surface tests. Confirm the integrated smoke slice covers configs, selectors, schemas, outputs, normalization, and the shipped safety guidance together.
