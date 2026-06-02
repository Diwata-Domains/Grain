# Plan: TASK-0162

## Approach

Keep the first Obsidian slice structural. Add the dedicated adapter profile and the minimal code/domain scaffold needed so Grain can talk about Obsidian as a first-class adapter with explicit file patterns and vault semantics, while leaving deeper context behavior for the next task.

---

## Step 1 — Adapter surface audit

Review the existing adapter profiles and any generic docs-adapter behavior to identify what should remain generic and what should move into a dedicated Obsidian contract.

---

## Step 2 — Profile and scaffold implementation

Add the `obsidian_adapter` profile plus any minimal code/domain hooks needed for the adapter to exist cleanly as a first-class surface.

---

## Step 3 — Verification and packet closeout

Add focused tests for the new adapter/profile surface, then record the exact verification slice in `results.md` and prepare the review bundle.

---

## Verification

Run focused tests covering the new adapter profile or scaffold surfaces. Confirm the Obsidian contract is explicit and does not blur back into `docs_adapter`.
