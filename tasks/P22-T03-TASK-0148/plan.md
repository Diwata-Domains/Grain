# Plan: TASK-0148

## Approach

Extend the current TUI snapshot with two more read-only views of repo state: current-phase backlog tasks and active packet artifacts. Parse only the active phase section and the current packet path already tracked by `current_task.md`, then render compact inspector panels in the existing Textual layout. Cover the new behavior with focused tests on snapshot content and panel rendering.

---

## Step 1 — Expand inspector snapshot data

Add phase backlog task and packet artifact summaries to the shell snapshot using existing backlog and packet file structures.

---

## Step 2 — Render inspector panels in the shell

Add dedicated backlog and packet inspector panels to the TUI so operators can see current phase queue state and packet file presence at a glance.

---

## Step 3 — Add focused inspector tests

Add tests for snapshot parsing and rendered inspector content to pin the read-only inspector contract before action and deeper preview work lands.

---

## Verification

Run the focused TUI/CLI test slice and verify the inspector panels reflect the same file-backed state Grain uses elsewhere.
