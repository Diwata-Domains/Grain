# Plan: TASK-0147

## Approach

Keep the TUI dashboard purely derived from existing repo state. Expand the shell snapshot to gather workflow evaluation, prompt recommendation, current-task pointer data, and candidate-task summaries, then render those into a multi-panel Textual dashboard. Back the new panels with focused tests on snapshot and text rendering so the shell stays deterministic and cheap to evolve.

---

## Step 1 — Expand the packet and snapshot contract

Fill the packet and define the extra read-only data the dashboard needs: current task pointer fields, candidate tasks, prompt metadata, and blocker details.

---

## Step 2 — Replace placeholder panels with real dashboard sections

Update the Textual shell to render workflow status, current task, recommended prompt, and queue or blocker panels from the new snapshot instead of generic phase placeholders.

---

## Step 3 — Add focused dashboard tests

Add tests for the richer snapshot data and the summary text emitted for blocked and ready workflow states so the dashboard contract is pinned before later TUI tasks build on it.

---

## Verification

Run the focused TUI/CLI test slice and confirm the dashboard snapshot reflects real workflow rules rather than hard-coded assumptions.
