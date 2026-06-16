# Plan: TASK-0170

## Approach

Keep the first crawler slice structural, like the earlier Obsidian, database, and data scaffolds. Add the dedicated adapter profile in both runtime doc surfaces, then lock the expected fields and hints with focused parser assertions before any crawler-specific context behavior is introduced.

---

## Step 1 — Audit the current adapter inventory

Review the existing runtime adapter docs and tests to decide where `crawler_adapter` should sit in the supported inventory and what minimum contract fields it needs.

---

## Step 2 — Add the crawler adapter contract

Add `crawler_adapter` to the live runtime doc and shipped runtime copy with clear file patterns, review hints, and context-priority guidance centered on configs, selectors, extraction schemas, and output validation.

---

## Step 3 — Verify and close out the scaffold

Extend the adapter-profile parser tests to assert the new contract and run the focused runtime/release slice before writing `results.md` and the review bundle.

---

## Verification

Run the focused adapter profile and release-surface tests. Confirm `crawler_adapter` parses correctly, includes the expected crawl/selector/extraction hints, and is present in the shipped runtime copy.
