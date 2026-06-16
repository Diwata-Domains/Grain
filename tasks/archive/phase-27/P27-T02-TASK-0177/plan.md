# Plan: TASK-0177

## Approach

Extend the existing context bundle metadata rather than adding a parallel reporting surface. Compute deterministic byte and token proxies from selected files, rank trim candidates from non-packet sources, and expose the results through existing context commands.

---

## Step 1 — Add bundle-level budget metadata

Compute total bytes, estimated tokens, warning thresholds, and trim hints from the already selected context sources.

---

## Step 2 — Surface budget data through context commands

Expose the budget in JSON output and text output for `context build` and `context export`.

---

## Step 3 — Verify heuristic reporting

Add focused tests for budget presence, trim hints, and export visibility.

---

## Verification

Run focused context, workflow, and observability command tests to ensure the new budget surface does not regress existing command behavior.
