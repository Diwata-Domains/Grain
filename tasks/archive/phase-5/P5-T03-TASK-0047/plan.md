# Plan: TASK-0047

## Approach

Build a small handoff service that reads packet metadata and packet results, derives a structured handoff report, and can render or validate a markdown handoff artifact. Keep the parser lightweight and constrained to the repository's existing packet artifact structure.

---

## Step 1 — Add handoff data model and parsing

Create a structured handoff report type and small helpers for reading task metadata and results sections.

---

## Step 2 — Implement rendering and write support

Render a markdown handoff artifact matching the packet template structure and support writing it to the packet directory by default.

---

## Step 3 — Add tests

Cover review-ready, done, incomplete, and missing-packet behavior plus markdown rendering/write-path expectations.

---

## Verification

Run the new handoff-service tests and the full pytest suite.
