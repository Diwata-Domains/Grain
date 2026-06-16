# Plan: TASK-0157

## Approach

Treat this as the closeout hardening slice for Phase 23. First, expand the office command coverage into a smoke-flow test that proves packet-first `.docx` and spreadsheet execution plus persisted review inspection behave coherently. Then document the operator flow in repo-facing docs and runtime guidance so users can drive the slice safely. Verification should stay focused on the office path unless broader regressions are directly exposed.

---

## Step 1 — Smoke-flow coverage

Add higher-level tests around the office CLI path so `.docx` and spreadsheet propose/export commands, review-artifact persistence, and validator output are exercised as an operator flow rather than only as isolated services.

---

## Step 2 — Operator docs and runtime guidance

Update the README and any relevant runtime guidance so the first office-artifact workflow is discoverable, including command shapes, packet expectations, and review-bundle inspection.

---

## Step 3 — Verification and closeout

Run the focused office CLI and service tests, record the verification command and any full-suite caveats in `results.md`, and prepare the review bundle for normal closeout.

---

## Verification

Run the focused office CLI and service slice plus any new smoke tests. Confirm that the office commands remain packet-first, emit persisted `office_review.json`, and that the documentation reflects the actual CLI behavior.
