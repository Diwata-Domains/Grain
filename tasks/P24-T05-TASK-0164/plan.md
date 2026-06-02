# Plan: TASK-0164

## Approach

Treat this as a closeout and hardening slice. Update the operator-facing docs so the desktop and Obsidian paths are explicit, then lock those expectations with focused release-surface and smoke coverage rather than broad new implementation.

---

## Step 1 — Audit the current desktop and Obsidian guidance

Review the README and runtime agent guidance to identify what is already documented for the MCP wrapper, direct CLI usage, and the dedicated Obsidian adapter.

---

## Step 2 — Tighten operator docs and release expectations

Add the missing operator guidance so users and agents understand when to use direct CLI vs local MCP wrapper and how Obsidian vault work fits the dedicated `obsidian_adapter` path.

---

## Step 3 — Run the combined smoke slice and close the packet

Add or update focused tests that assert the shipped docs cover the desktop and Obsidian paths, run the combined smoke/release slice, and then record the results in the packet artifacts.

---

## Verification

Run the focused MCP, Obsidian integration, adapter profile, and release-surface tests. Confirm the docs are explicit about direct CLI vs local MCP wrapper and that the dedicated Obsidian adapter path is represented in the shipped guidance.
