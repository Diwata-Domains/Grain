# Plan: TASK-0171

## Approach

Keep the first crawler behavior small and direct-select. Crawler artifacts do not need graph connectivity yet, so the adapter should select its files by profile patterns, then apply one narrow priority pass that lifts crawl configs and selectors first and keeps unrelated application code out of the bundle.

---

## Step 1 — Audit the existing selection pipeline

Inspect where adapter candidates are gathered, filtered, and reranked so the crawler behavior can slot into the same path used by other non-graph adapters.

---

## Step 2 — Add crawler-specific prioritization

Make `crawler_adapter` select its candidates without requiring graph traces, then add a small ordering helper that prioritizes crawl configs, selectors, and extraction-schema artifacts.

---

## Step 3 — Verify with focused integration coverage

Add a focused crawler-adapter integration test that proves configs, selectors, and schemas are selected while unrelated app code is left out, then record the verification slice in `results.md`.

---

## Verification

Run the focused adapter-profile, release-surface, and crawler-adapter integration tests. Confirm crawl configs and selectors are selected, unrelated code stays out of the bundle, and extraction-schema artifacts are still available as secondary context.
