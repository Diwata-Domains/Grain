# Plan: TASK-0048

## Approach

Add a small CLI wrapper around the handoff service so the command can generate and write handoff artifacts without duplicating packet parsing or markdown rendering logic. Add tests that cover the common packet states and output-path behavior.

---

## Step 1 — Wire command behavior

Implement `review handoff` to call into the handoff service, emit a readable summary, and write the artifact to disk.

---

## Step 2 — Add tests

Cover review-ready packets, done packets, custom output paths, and failure modes for missing or incomplete packets.

---

## Step 3 — Verify behavior

Run the focused handoff tests and then the full pytest suite.

---

## Verification

Confirm that the command writes `handoff.md` by default and returns a stable JSON shape when requested.
