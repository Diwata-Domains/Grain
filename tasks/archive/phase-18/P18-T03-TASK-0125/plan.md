# Plan: TASK-0125

## Approach

Shift notebook ownership at the adapter-profile layer and pair it with the smallest context-service compatibility tweak needed to preserve existing selection behavior. Then prove the migration with focused notebook-context tests rather than broad Phase 18 integration coverage.

---

## Step 1 — Update adapter profiles

Remove `.ipynb` ownership from `code_adapter`, add it to `data_adapter`, and move notebook-specific hints so the runtime doc reflects the new primary home.

---

## Step 2 — Preserve selection behavior

Adjust the context-service graph-trace gate so `data_adapter` notebook sources can still be selected deterministically before the broader Phase 18 integration slice lands.

---

## Step 3 — Add migration tests

Add focused coverage showing that a packet using `data_adapter` still selects and exports notebook content after the ownership move.

---

## Verification

Run focused notebook/context tests plus adapter-profile tests to confirm the migration did not regress existing notebook behavior.
