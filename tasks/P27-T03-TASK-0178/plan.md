# Plan: TASK-0178

## Approach

Consume the new packet-local observability file and context-budget metadata inside the existing TUI snapshot builder, then render that data in dedicated panels without adding a second workflow engine.

---

## Step 1 — Extend the TUI snapshot model

Add observability and budget fields to the shell snapshot and packet inspector.

---

## Step 2 — Render observability and budget surfaces

Add one observability panel, extend the context panel with cost hints, and surface recent results summary text in the packet panel.

---

## Step 3 — Verify panel rendering

Add focused snapshot and render tests for the new TUI surfaces.

---

## Verification

Run focused TUI, context, and observability command tests to confirm the shell reflects the new file-backed metadata correctly.
