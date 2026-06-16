# Plan: TASK-0149

## Approach

Implement execute, review, and close launchers as pure helper functions that call the existing Grain service layer and return a structured result plus a refreshed shell snapshot. Then bind those launchers into the Textual app with keyboard shortcuts and an action panel so the TUI can advance normal workflow steps without becoming its own workflow engine.

---

## Step 1 — Add structured launcher helpers

Create small helpers for execute, review, and close that delegate to `run_workflow_step`, `materialize_handoff_artifact`, and `close_packet`, then rebuild the TUI snapshot after each attempt.

---

## Step 2 — Bind launchers into the Textual shell

Add a visible action panel and Textual key bindings so operators can trigger the launchers and see the most recent launcher result inside the TUI.

---

## Step 3 — Add focused launcher tests

Add tests for the pure launcher helpers and their rendered action feedback so the control layer is pinned without requiring a full interactive terminal test harness.

---

## Verification

Run the focused TUI and workflow-related test slice and verify the launcher helpers respect normal Grain gates and return refreshed state after each attempt.
