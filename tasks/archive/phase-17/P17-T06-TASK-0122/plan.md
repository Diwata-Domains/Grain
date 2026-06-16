# Plan: TASK-0122

## Approach

Build one integration suite that configures a temporary Phase 17 repo and verifies the ranking layer through its real consumer surfaces: context selection, orchestration scope analysis, and ranked task advice. Use fake embedding providers so the suite stays deterministic and fast.

---

## Step 1 — Add shared Phase 17 test fixtures

Create a temporary repo with current focus, backlog, adapter profiles, context files, and a packet fixture so the ranking consumers operate against realistic repository state.

---

## Step 2 — Add end-to-end ranking tests

Verify ranked context metadata, ranked task advice, and ranked impacted-file advice using the same fake provider setup.

---

## Step 3 — Run the Phase 17 ranking suites together

Re-run the new integration module plus the focused ranking/context/orchestration tests to catch cross-surface regressions.

---

## Verification

Run the Phase 17 integration module plus the surrounding task-advice, impact-ranking, context, orchestration, ranking-service, and import tests with the local virtualenv interpreter.
