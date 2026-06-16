# Plan: TASK-0173

## Approach

Keep this slice in shipped guidance and regression coverage. The crawler adapter already encodes review hints in its profile, so this task should surface those expectations in the operator-facing docs and lock them with release-surface tests.

---

## Step 1 — Audit existing shipped guidance

Review the README and runtime agent guidance to see where database, desktop, Obsidian, office, and other non-code workflows already define explicit operator rules.

---

## Step 2 — Add crawler review and safety guidance

Add crawler-specific instructions covering adapter choice, narrow context loading, robots constraints, rate limits, retry policy risk, selector brittleness, and extraction drift.

---

## Step 3 — Lock the guidance into regression tests

Extend the shipped release-surface tests so the crawler guidance is checked automatically and then record the exact verification slice in `results.md`.

---

## Verification

Run the focused release-surface, adapter-profile, and crawler integration tests. Confirm the shipped docs mention `crawler_adapter` and the key review risks without implying any live crawling surface.
