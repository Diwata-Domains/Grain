# Plan: TASK-0146

## Approach

Add the TUI as a thin, lazy-loaded CLI surface so Grain keeps one Python runtime and one workflow engine. The scaffold should expose a `grain tui` entrypoint, build a lightweight workflow snapshot from the existing workflow service, and render a minimal Textual shell with clear placeholders for later Phase 22 views.

---

## Step 1 — Prepare the packet and command boundary

Fill the execution packet, inspect the current CLI registration pattern, and add the smallest new command surface needed for TUI launch so the shell does not fork existing workflow logic.

---

## Step 2 — Add the lazy-loaded Textual shell

Create a `grain.tui` package with an app factory and a shell snapshot builder. Keep Textual imports inside the TUI module’s runtime path so the codebase remains import-safe and testable even before the dependency is installed locally.

---

## Step 3 — Add focused tests and verify bootstrap behavior

Add tests for the `grain tui` command wiring and for the workflow snapshot data the TUI reads. Verify the command launches through the normal CLI entrypoint and that the shell snapshot stays aligned with workflow evaluation output.

---

## Verification

Run the focused CLI and TUI tests, then sanity-check the command surface and packet docs before writing results.
