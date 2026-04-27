# Plan: TASK-0120

## Approach

Keep the graph-derived `affected_files` list unchanged, then layer ranked impacted-file metadata on top through a dedicated helper. The orchestration payload should expose both the existing impact signal and the new ranked view so consumers can opt into the richer advisory data without breaking older behavior.

---

## Step 1 — Add impacted-file ranking helper

Create a helper that resolves the active embedding provider, semantically scores affected files against touched files, and passes normalized inputs into the shared ranking service.

---

## Step 2 — Attach ranked impact metadata

Extend orchestration scope signals to include the impacted-file ranking payload alongside the existing `affected_files` and `downstream_areas`.

---

## Step 3 — Add focused tests

Add helper-level tests for ranking output and an orchestration test that asserts the ranked impact payload is included without changing existing fields.

---

## Verification

Run the impacted-file ranking, orchestration, ranking-service, and import tests with the local virtualenv interpreter.
