# Plan: TASK-0151

## Approach

Close Phase 22 with one realistic launcher smoke flow and concise operator docs. The smoke path should exercise execute, review handoff, and close through the TUI launcher helpers without requiring a fragile interactive terminal harness. The docs should explain the actual current TUI surface and what remains intentionally deferred.

---

## Step 1 — Add a launcher smoke flow

Add one realistic smoke test that exercises the TUI launcher helpers across a packet lifecycle so the shell has more than isolated unit coverage.

---

## Step 2 — Document the current TUI surface

Add a README section for `grain tui` that explains what the shell currently provides, how it relates to the CLI, and what is still deferred.

---

## Step 3 — Re-run the focused verification slice

Run the TUI-focused verification slice with the workflow/review/context tests it depends on so Phase 22 can hand off on a clean signal.

---

## Verification

Run the focused TUI, workflow, review, task-close, and context-build tests and confirm the smoke path plus docs changes land cleanly.
