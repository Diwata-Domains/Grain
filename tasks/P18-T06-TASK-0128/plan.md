# Plan: TASK-0128

## Approach

Build one representative temporary repo that exercises the full Phase 18 path, then assert the key user-visible outputs rather than retesting every internal helper. Keep the suite deterministic by faking data-artifact extraction where needed and reusing existing manifest/packet setup patterns from earlier phase integration tests.

---

## Step 1 — Build a representative repo fixture

Create a temporary repo layout with runtime docs, a packet using `data_adapter`, a notebook, and at least one data artifact.

---

## Step 2 — Assert the integrated user-facing flows

Verify context bundle/export, orchestration scope signals, and onboarding/scanner outputs all reflect the new `data_adapter` path in the same repo shape.

---

## Step 3 — Run the full Phase 18 focused suite

Run the new integration test together with the focused Phase 18 modules so the phase can close on one stable targeted test gate.

---

## Verification

Run the Phase 18 targeted suite and confirm every Phase 18 task surface is exercised without a full-repo test run.
